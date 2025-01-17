from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from auth import get_current_user

router = APIRouter(prefix="/api")

class AddressBase(BaseModel):
    type: str
    address: str
    city: str
    is_default: bool = False

class Address(AddressBase):
    id: int
    user_id: int

@router.get("/address")
async def get_addresses(current_user: dict = Depends(get_current_user)):
    try:
        conn = sqlite3.connect('services.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, type, address, city, is_default 
            FROM addresses 
            WHERE user_id = ?
            ORDER BY is_default DESC, id DESC
        ''', (current_user["user_id"],))
        
        addresses = cursor.fetchall()
        
        return [
            {
                "id": addr[0],
                "user_id": addr[1],
                "type": addr[2],
                "address": addr[3],
                "city": addr[4],
                "is_default": bool(addr[5])
            }
            for addr in addresses
        ]
    finally:
        conn.close()

@router.post("/address")
async def create_address(address: AddressBase, current_user: dict = Depends(get_current_user)):
    try:
        conn = sqlite3.connect('services.db')
        cursor = conn.cursor()
        
        if address.is_default:
            cursor.execute('''
                UPDATE addresses 
                SET is_default = 0 
                WHERE user_id = ?
            ''', (current_user["user_id"],))
        
        cursor.execute('''
            INSERT INTO addresses (user_id, type, address, city, is_default)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            current_user["user_id"],
            address.type,
            address.address,
            address.city,
            address.is_default
        ))
        
        address_id = cursor.lastrowid
        conn.commit()
        
        return {
            "id": address_id,
            "user_id": current_user["user_id"],
            "type": address.type,
            "address": address.address,
            "city": address.city,
            "is_default": address.is_default
        }
    finally:
        conn.close()

@router.put("/address/{address_id}")
async def update_address(
    address_id: int,
    address: AddressBase,
    current_user: dict = Depends(get_current_user)
):
    try:
        conn = sqlite3.connect('services.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM addresses 
            WHERE id = ? AND user_id = ?
        ''', (address_id, current_user["user_id"]))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Address not found")
        
        if address.is_default:
            cursor.execute('''
                UPDATE addresses 
                SET is_default = 0 
                WHERE user_id = ? AND id != ?
            ''', (current_user["user_id"], address_id))
        
        cursor.execute('''
            UPDATE addresses 
            SET type = ?, address = ?, city = ?, is_default = ?
            WHERE id = ?
        ''', (
            address.type,
            address.address,
            address.city,
            address.is_default,
            address_id
        ))
        
        conn.commit()
        
        return {
            "id": address_id,
            "user_id": current_user["user_id"],
            "type": address.type,
            "address": address.address,
            "city": address.city,
            "is_default": address.is_default
        }
    finally:
        conn.close()

@router.delete("/address/{address_id}")
async def delete_address(address_id: int, current_user: dict = Depends(get_current_user)):
    try:
        conn = sqlite3.connect('services.db')
        cursor = conn.cursor()
        
        # First check if the address exists and get its default status
        cursor.execute('''
            SELECT is_default FROM addresses 
            WHERE id = ? AND user_id = ?
        ''', (address_id, current_user["user_id"]))
        
        address = cursor.fetchone()
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        
        was_default = address[0]
        
        # Delete the address
        cursor.execute('''
            DELETE FROM addresses 
            WHERE id = ? AND user_id = ?
        ''', (address_id, current_user["user_id"]))
        
        if was_default:
            # If the deleted address was default, set a new default
            cursor.execute('''
                UPDATE addresses 
                SET is_default = 1 
                WHERE user_id = ? 
                ORDER BY id DESC 
                LIMIT 1
            ''', (current_user["user_id"],))
        
        conn.commit()
        return {"message": "Address deleted successfully"}
    except Exception as e:
        print(f"Error deleting address: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()