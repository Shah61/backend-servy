from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import sqlite3

router = APIRouter()

# OAuth2 and JWT settings
SECRET_KEY = "your-secret-key-here"  # Change this to a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic models for request/response
class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    phone: str
    profile_image: Optional[str] = None

class ProviderRegister(BaseModel):
    email: str
    password: str
    name: str
    ic_number: str
    phone: str
    profile_image: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    user_type: str

# JWT token creation
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Password hashing
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# User authentication endpoints
@router.post("/api/auth/user/register")
async def register_user(user: UserRegister):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    # Check if email already exists
    c.execute('SELECT id FROM users WHERE email = ?', (user.email,))
    if c.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    hashed_password = hash_password(user.password)
    
    try:
        c.execute('''
            INSERT INTO users (email, password, name, phone, profile_image)
            VALUES (?, ?, ?, ?, ?)
        ''', (user.email, hashed_password, user.name, user.phone, user.profile_image))
        
        user_id = c.lastrowid
        conn.commit()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user_id), "type": "user"}
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            user_type="user"
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    finally:
        conn.close()

@router.post("/api/auth/provider/register")
async def register_provider(provider: ProviderRegister):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    # Check if email already exists
    c.execute('SELECT id FROM service_providers WHERE email = ?', (provider.email,))
    if c.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    hashed_password = hash_password(provider.password)
    
    try:
        c.execute('''
            INSERT INTO service_providers 
            (email, password, name, ic_number, phone, profile_image, is_verified, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (provider.email, hashed_password, provider.name, provider.ic_number, 
              provider.phone, provider.profile_image, False, 0))
        
        provider_id = c.lastrowid
        conn.commit()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(provider_id), "type": "provider"}
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=provider_id,
            user_type="provider"
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    finally:
        conn.close()

@router.post("/api/auth/user/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    c.execute('SELECT id, password FROM users WHERE email = ?', (form_data.username,))
    user = c.fetchone()
    conn.close()
    
    if not user or not verify_password(form_data.password, user[1]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user[0]), "type": "user"}
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user[0],
        user_type="user"
    )

@router.post("/api/auth/provider/login")
async def login_provider(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    c.execute('SELECT id, password FROM service_providers WHERE email = ?', (form_data.username,))
    provider = c.fetchone()
    conn.close()
    
    if not provider or not verify_password(form_data.password, provider[1]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(provider[0]), "type": "provider"}
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=provider[0],
        user_type="provider"
    )

# Authentication middleware
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("type")
        if user_id is None or user_type is None:
            raise credentials_exception
        return {"user_id": int(user_id), "user_type": user_type}
    except jwt.JWTError:
        raise credentials_exception

@router.get("/api/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    if current_user["user_type"] == "user":
        c.execute('SELECT id, email, name, phone, profile_image FROM users WHERE id = ?', 
                 (current_user["user_id"],))
    else:
        c.execute('''SELECT id, email, name, phone, profile_image, is_verified, rating, points 
                    FROM service_providers WHERE id = ?''', 
                 (current_user["user_id"],))
    
    user_data = c.fetchone()
    conn.close()
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user["user_type"] == "user":
        return {
            "id": user_data[0],
            "email": user_data[1],
            "name": user_data[2],
            "phone": user_data[3],
            "profile_image": user_data[4],
            "type": "user"
        }
    else:
        return {
            "id": user_data[0],
            "email": user_data[1],
            "name": user_data[2],
            "phone": user_data[3],
            "profile_image": user_data[4],
            "is_verified": bool(user_data[5]),
            "rating": user_data[6],
            "points": user_data[7],
            "type": "provider"
        }