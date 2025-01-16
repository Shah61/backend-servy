from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from typing import List
import sqlite3

app = FastAPI()



# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Services API"}

@app.get("/api/categories")
async def get_categories():
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    c.execute('SELECT * FROM categories')
    categories = c.fetchall()
    conn.close()
    
    return [
        {
            "id": cat[0],
            "name": cat[1],
            "path": cat[2],
            "icon": cat[3],
            "services": f"{cat[4]} Services"
        }
        for cat in categories
    ]

@app.get("/api/categories/{path}/services")
async def get_services_by_category_path(path: str):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    # First get the category id
    c.execute('SELECT id FROM categories WHERE path = ?', (path,))
    category = c.fetchone()
    
    if not category:
        conn.close()
        raise HTTPException(status_code=404, detail="Category not found")
        
    # Then get all services for this category
    c.execute('SELECT * FROM services WHERE category_id = ?', (category[0],))
    services = c.fetchall()
    conn.close()
    
    return [
        {
            "id": s[0],
            "title": s[2],
            "description": s[3],
            "price": s[4],
            "originalPrice": s[5],
            "rating": s[6],
            "reviews": s[7],
            "provider": {
                "name": s[8],
                "image": s[9],
                "role": s[10]
            },
            "image": s[11]
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
    
    # Get service reviews
    c.execute('SELECT * FROM reviews WHERE service_id = ? ORDER BY date DESC', (service_id,))
    reviews = c.fetchall()
    
    # Get category info
    c.execute('SELECT name, path FROM categories WHERE id = ?', (service[1],))
    category = c.fetchone()
    
    conn.close()
    
    return {
        "id": service[0],
        "category": {
            "name": category[0],
            "path": category[1]
        },
        "title": service[2],
        "description": service[3],
        "price": service[4],
        "originalPrice": service[5],
        "rating": service[6],
        "totalReviews": service[7],
        "provider": {
            "name": service[8],
            "image": service[9],
            "role": service[10]
        },
        "image": service[11],
        "reviews": [
            {
                "id": review[0],
                "userName": review[2],
                "rating": review[3],
                "comment": review[4],
                "date": review[5],
                "userAvatar": review[6]
            }
            for review in reviews
        ]
    }

@app.get("/api/services/{service_id}/reviews")
async def get_service_reviews(service_id: int):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    # First check if service exists
    c.execute('SELECT id FROM services WHERE id = ?', (service_id,))
    service = c.fetchone()
    
    if not service:
        conn.close()
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Get reviews for the service
    c.execute('SELECT * FROM reviews WHERE service_id = ? ORDER BY date DESC', (service_id,))
    reviews = c.fetchall()
    conn.close()
    
    return [
        {
            "id": review[0],
            "userName": review[2],
            "rating": review[3],
            "comment": review[4],
            "date": review[5],
            "userAvatar": review[6]
        }
        for review in reviews
    ]

# Optional: Add endpoint for searching services
@app.get("/api/services/search/{query}")
async def search_services(query: str):
    conn = sqlite3.connect('services.db')
    c = conn.cursor()
    
    # Search in service titles and descriptions
    c.execute('''
        SELECT * FROM services 
        WHERE title LIKE ? OR description LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    
    services = c.fetchall()
    conn.close()
    
    return [
        {
            "id": s[0],
            "title": s[2],
            "description": s[3],
            "price": s[4],
            "originalPrice": s[5],
            "rating": s[6],
            "reviews": s[7],
            "provider": {
                "name": s[8],
                "image": s[9],
                "role": s[10]
            },
            "image": s[11]
        }
        for s in services
    ]