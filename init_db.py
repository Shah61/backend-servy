import sqlite3
from datetime import datetime
from enum import Enum

class BookingType(Enum):
    URGENT = 'urgent'
    SCHEDULED = 'scheduled'

class BookingStatus(Enum):
    PENDING = 'pending'
    ONGOING = 'ongoing'
    COMPLETED = 'completed'
    CANCELED = 'canceled'

class PaymentStatus(Enum):
    UNPAID = 'unpaid'
    PAID = 'paid'
    FLOATING = 'floating'

class ReportType(Enum):
    USER = 'user'
    PROVIDER = 'provider'

def init_db():
    # Connect to SQLite
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()

    # Drop existing tables if they exist
    tables = ['chats', 'reviews', 'notifications', 'rankings', 'reports', 'bookings', 
              'services', 'service_providers', 'users', 'admins', 'categories']
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')

    # Create users table
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email VARCHAR NOT NULL,
        password VARCHAR NOT NULL,
        name VARCHAR,
        phone VARCHAR,
        profile_image VARCHAR,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create service_providers table
    cursor.execute('''
    CREATE TABLE service_providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email VARCHAR NOT NULL,
        password VARCHAR NOT NULL,
        name VARCHAR NOT NULL,
        ic_number VARCHAR NOT NULL,
        phone VARCHAR,
        profile_image VARCHAR,
        is_verified BOOLEAN DEFAULT FALSE,
        rating FLOAT,
        points INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create admins table
    cursor.execute('''
    CREATE TABLE admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR NOT NULL,
        password VARCHAR NOT NULL
    )
    ''')
    # Create bookings table
    cursor.execute('''
    CREATE TABLE bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        provider_id INTEGER NOT NULL,
        booking_type VARCHAR NOT NULL,
        schedule_date DATETIME,
        status VARCHAR NOT NULL,
        payment_status VARCHAR NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (service_id) REFERENCES services (id),
        FOREIGN KEY (provider_id) REFERENCES service_providers (id)
    )
    ''')

    # Create reviews table
    cursor.execute('''
    CREATE TABLE reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        provider_id INTEGER NOT NULL,
        rating INTEGER,
        comment TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (booking_id) REFERENCES bookings (id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (provider_id) REFERENCES service_providers (id)
    )
    ''')

    # Create chats table
    cursor.execute('''
    CREATE TABLE chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        sender_type VARCHAR NOT NULL,
        message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (booking_id) REFERENCES bookings (id)
    )
    ''')

    # Create notifications table
    cursor.execute('''
    CREATE TABLE notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        provider_id INTEGER,
        booking_id INTEGER,
        message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (provider_id) REFERENCES service_providers (id),
        FOREIGN KEY (booking_id) REFERENCES bookings (id)
    )
    ''')

    # Create rankings table
    cursor.execute('''
    CREATE TABLE rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider_id INTEGER NOT NULL,
        rank INTEGER,
        points INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (provider_id) REFERENCES service_providers (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    path VARCHAR NOT NULL,
    icon VARCHAR NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    sample_categories = [
         ('House Cleaning', 'house-cleaning', '🧹'),
        ('Plumbing', 'plumbing', '🔧'),
        ('Electrical', 'electrical', '⚡'),
        ('Moving', 'moving', '📦'),
        ('Gardening', 'gardening', '🌱'),
        ('Painting', 'painting', '🎨'),
        ('Appliance Repair', 'appliance-repair', '🔨'),
        ('Pest Control', 'pest-control', '🐜')
    ]
    

    cursor.executemany('''
    INSERT INTO categories (name, path, icon)
    VALUES (?, ?, ?)
    ''', sample_categories)
    
    # Add category_id to services table
    cursor.execute('''
    ALTER TABLE services 
    ADD COLUMN category_id INTEGER
    REFERENCES categories(id)
    ''')
                       

    # Create reports table
    cursor.execute('''
    CREATE TABLE reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reporter_id INTEGER,
        reported_id INTEGER,
        report_type VARCHAR NOT NULL,
        reason TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create addresses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        is_default BOOLEAN NOT NULL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create services table
    cursor.execute('''
    CREATE TABLE services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR NOT NULL,
        description TEXT,
        price FLOAT NOT NULL,
        category_id INTEGER REFERENCES categories(id),
        provider_id INTEGER REFERENCES service_providers(id),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Insert sample services data - add this right after creating the services table
    sample_services = [
        # House Cleaning services
        ('Deep House Cleaning', 'Complete house deep cleaning service including all rooms and surfaces', 150.00, 1, 1),
        ('Kitchen Cleaning', 'Professional kitchen cleaning and sanitizing', 80.00, 1, 1),
        ('Bathroom Cleaning', 'Deep bathroom cleaning and disinfection', 70.00, 1, 1),

        # Plumbing services
        ('Pipe Repair', 'Fix leaking pipes and plumbing issues', 120.00, 2, 1),
        ('Drain Cleaning', 'Professional drain unclogging and cleaning', 90.00, 2, 1),
        ('Water Heater Repair', 'Water heater maintenance and repair', 200.00, 2, 1),

        # Electrical services
        ('Electrical Repair', 'Fix electrical issues and wiring problems', 130.00, 3, 1),
        ('Light Installation', 'Install new lighting fixtures', 70.00, 3, 1),
        ('Circuit Repair', 'Electrical circuit diagnosis and repair', 150.00, 3, 1),

        # Appliance Repair services
        ('AC Repair', 'Air conditioner repair and maintenance', 180.00, 7, 1),
        ('Washing Machine Repair', 'Washing machine diagnosis and repair', 120.00, 7, 1),
        ('Refrigerator Service', 'Refrigerator maintenance and repair', 160.00, 7, 1)
    ]

    cursor.executemany('''
        INSERT INTO services (name, description, price, category_id, provider_id)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_services)

    

    # Sample addresses data
    sample_addresses = [
        (1, 'Home', 'No. 15, Jalan Suria 12, Taman Suria', 'Johor Bahru, Johor 81100', True),
        (1, 'Work', 'Block A-12-3, Plaza Sentral, Jalan Stesen Sentral 5', 'Kuala Lumpur 50470', False),
        (1, 'Parent\'s House', 'No. 27, Lorong Kelapa 3, Taman Indah', 'Penang 11900', False)
    ]

    cursor.executemany('''
        INSERT INTO addresses (user_id, type, address, city, is_default)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_addresses)

    

    # Insert sample data
    # Sample users
    cursor.execute('''
    INSERT INTO users (email, password, name, phone, profile_image)
    VALUES (?, ?, ?, ?, ?)
    ''', ('user@example.com', 'hashed_password', 'John Doe', '+1234567890', 'profile1.jpg'))

    # Sample service provider
    cursor.execute('''
    INSERT INTO service_providers 
    (email, password, name, ic_number, phone, profile_image, is_verified, rating)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('provider@example.com', 'hashed_password', 'Jane Smith', 'IC123456', 
          '+0987654321', 'profile2.jpg', True, 4.5))

    # Sample admin
    cursor.execute('''
    INSERT INTO admins (username, password)
    VALUES (?, ?)
    ''', ('admin', 'admin_password'))

    # Sample service
    cursor.execute('''
    INSERT INTO services (name, description, price)
    VALUES (?, ?, ?)
    ''', ('House Cleaning', 'Complete house cleaning service', 100.00))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Database initialized successfully with the new schema!")

if __name__ == "__main__":
    init_db()