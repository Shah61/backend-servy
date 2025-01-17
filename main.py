from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import sqlite3
from auth import get_current_user
from auth import router as auth_router
from address_routes import router as address_router

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(address_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Services API"}

@app.get("/api/services")
async def get_services():
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    c.execute('SELECT * FROM services')
    services = c.fetchall()
    conn.close()
    
    return [
        {
            "id": s[0],
            "name": s[1],
            "description": s[2],
            "price": s[3],
            "created_at": s[4]
        }
        for s in services
    ]

@app.get("/api/services/{service_id}")
async def get_service_details(service_id: int):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    # Get service details
    c.execute('SELECT * FROM services WHERE id = ?', (service_id,))
    service = c.fetchone()
    
    if not service:
        conn.close()
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Get service provider details
    c.execute('SELECT name, phone, profile_image, rating FROM service_providers WHERE id = ?', 
             (service[0],))
    provider = c.fetchone()
    
    # Get service reviews
    c.execute('''
        SELECT r.*, u.name as user_name, u.profile_image as user_avatar 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.booking_id IN (
            SELECT id FROM bookings WHERE service_id = ?
        )
        ORDER BY r.created_at DESC
    ''', (service_id,))
    reviews = c.fetchall()
    
    conn.close()
    
    return {
        "id": service[0],
        "name": service[1],
        "description": service[2],
        "price": service[3],
        "created_at": service[4],
        "provider": {
            "name": provider[0] if provider else None,
            "phone": provider[1] if provider else None,
            "profile_image": provider[2] if provider else None,
            "rating": provider[3] if provider else None
        },
        "reviews": [
            {
                "id": review[0],
                "rating": review[4],
                "comment": review[5],
                "created_at": review[6],
                "user_name": review[7],
                "user_avatar": review[8]
            }
            for review in reviews
        ] if reviews else []
    }

@app.get("/api/bookings")
async def get_user_bookings(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    if current_user["user_type"] == "user":
        # Get bookings for user
        c.execute('''
            SELECT b.*, s.name as service_name, sp.name as provider_name 
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            JOIN service_providers sp ON b.provider_id = sp.id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
        ''', (current_user["user_id"],))
    else:
        # Get bookings for provider
        c.execute('''
            SELECT b.*, s.name as service_name, u.name as user_name 
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            JOIN users u ON b.user_id = u.id
            WHERE b.provider_id = ?
            ORDER BY b.created_at DESC
        ''', (current_user["user_id"],))
    
    bookings = c.fetchall()
    conn.close()
    
    if current_user["user_type"] == "user":
        return [
            {
                "id": b[0],
                "service_name": b[8],
                "provider_name": b[9],
                "booking_type": b[4],
                "schedule_date": b[5],
                "status": b[6],
                "payment_status": b[7],
                "created_at": b[8]
            }
            for b in bookings
        ]
    else:
        return [
            {
                "id": b[0],
                "service_name": b[8],
                "user_name": b[9],
                "booking_type": b[4],
                "schedule_date": b[5],
                "status": b[6],
                "payment_status": b[7],
                "created_at": b[8]
            }
            for b in bookings
        ]

@app.get("/api/chats/{booking_id}")
async def get_booking_chats(booking_id: int, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    # Verify booking belongs to current user
    if current_user["user_type"] == "user":
        c.execute('SELECT id FROM bookings WHERE id = ? AND user_id = ?', 
                 (booking_id, current_user["user_id"]))
    else:
        c.execute('SELECT id FROM bookings WHERE id = ? AND provider_id = ?', 
                 (booking_id, current_user["user_id"]))
    
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=403, detail="Not authorized to access this chat")
    
    # Get chat messages
    c.execute('''
        SELECT * FROM chats 
        WHERE booking_id = ?
        ORDER BY created_at ASC
    ''', (booking_id,))
    
    chats = c.fetchall()
    conn.close()
    
    return [
        {
            "id": chat[0],
            "sender_id": chat[2],
            "sender_type": chat[3],
            "message": chat[4],
            "created_at": chat[5]
        }
        for chat in chats
    ]

@app.get("/api/services/search/{query}")
async def search_services(query: str):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT s.*, sp.name as provider_name, sp.rating as provider_rating 
        FROM services s
        LEFT JOIN service_providers sp ON s.id = sp.id
        WHERE s.name LIKE ? OR s.description LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    
    services = c.fetchall()
    conn.close()
    
    return [
        {
            "id": s[0],
            "name": s[1],
            "description": s[2],
            "price": s[3],
            "created_at": s[4],
            "provider": {
                "name": s[5],
                "rating": s[6]
            }
        }
        for s in services
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)