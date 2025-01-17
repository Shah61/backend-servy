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
    try:
        # Connect to SQLite
        conn = sqlite3.connect('services.db')
        cursor = conn.cursor()
        print("Connected to database successfully")

        # Drop existing tables if they exist
        tables = [
            'chats', 'reviews', 'notifications', 'rankings', 'reports', 
            'bookings', 'services', 'addresses', 'service_providers', 
            'users', 'admins', 'categories'
        ]
        for table in tables:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')
        print("Dropped existing tables")

        # Create users table (no dependencies)
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR NOT NULL UNIQUE,
            password VARCHAR NOT NULL,
            name VARCHAR,
            phone VARCHAR,
            profile_image VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created users table")

        # Create service_providers table (no dependencies)
        cursor.execute('''
        CREATE TABLE service_providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR NOT NULL UNIQUE,
            password VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            ic_number VARCHAR NOT NULL UNIQUE,
            phone VARCHAR,
            profile_image VARCHAR,
            is_verified BOOLEAN DEFAULT FALSE,
            rating FLOAT DEFAULT 0,
            points INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created service_providers table")

        # Create admins table (no dependencies)
        cursor.execute('''
        CREATE TABLE admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR NOT NULL UNIQUE,
            password VARCHAR NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created admins table")

        # Create categories table (no dependencies)
        cursor.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR NOT NULL,
            path VARCHAR NOT NULL UNIQUE,
            icon VARCHAR NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created categories table")

        # Create services table (depends on categories and service_providers)
        cursor.execute('''
        CREATE TABLE services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR NOT NULL,
            description TEXT,
            price FLOAT NOT NULL,
            category_id INTEGER,
            provider_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (provider_id) REFERENCES service_providers(id)
        )
        ''')
        print("Created services table")

        # Create addresses table (depends on users)
        cursor.execute('''
        CREATE TABLE addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            is_default BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        print("Created addresses table")

        # Create bookings table (depends on users, services, and providers)
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
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (service_id) REFERENCES services(id),
            FOREIGN KEY (provider_id) REFERENCES service_providers(id)
        )
        ''')
        print("Created bookings table")

        # Create reviews table
        cursor.execute('''
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (provider_id) REFERENCES service_providers(id)
        )
        ''')
        print("Created reviews table")

        # Create chats table
        cursor.execute('''
        CREATE TABLE chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            sender_type VARCHAR NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
        ''')
        print("Created chats table")

        # Create notifications table
        cursor.execute('''
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            provider_id INTEGER,
            booking_id INTEGER,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (provider_id) REFERENCES service_providers(id),
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
        ''')
        print("Created notifications table")

        # Create rankings table
        cursor.execute('''
        CREATE TABLE rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_id INTEGER NOT NULL,
            rank INTEGER NOT NULL,
            points INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (provider_id) REFERENCES service_providers(id)
        )
        ''')
        print("Created rankings table")

        # Create reports table
        cursor.execute('''
        CREATE TABLE reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER NOT NULL,
            reported_id INTEGER NOT NULL,
            report_type VARCHAR NOT NULL,
            reason TEXT NOT NULL,
            status VARCHAR DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created reports table")

        # Insert sample data
        print("\nInserting sample data...")

        # Insert sample categories
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
        print("Inserted categories")

        # Insert sample users
        cursor.execute('''
            INSERT INTO users (email, password, name, phone, profile_image)
            VALUES (?, ?, ?, ?, ?)
        ''', ('user@example.com', 'hashed_password', 'John Doe', '+1234567890', 'profile1.jpg'))
        print("Inserted sample user")

        # Insert sample service provider
        cursor.execute('''
            INSERT INTO service_providers 
            (email, password, name, ic_number, phone, profile_image, is_verified, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('provider@example.com', 'hashed_password', 'Jane Smith', 'IC123456', 
              '+0987654321', 'profile2.jpg', True, 4.5))
        print("Inserted sample service provider")

        # Insert sample admin
        cursor.execute('''
            INSERT INTO admins (username, password)
            VALUES (?, ?)
        ''', ('admin', 'admin_password'))
        print("Inserted sample admin")

        # Insert sample services
        sample_services = [
            ('Deep House Cleaning', 'Complete house deep cleaning service including all rooms and surfaces', 150.00, 1, 1),
            ('Kitchen Cleaning', 'Professional kitchen cleaning and sanitizing', 80.00, 1, 1),
            ('Bathroom Cleaning', 'Deep bathroom cleaning and disinfection', 70.00, 1, 1),
            ('Pipe Repair', 'Fix leaking pipes and plumbing issues', 120.00, 2, 1),
            ('Drain Cleaning', 'Professional drain unclogging and cleaning', 90.00, 2, 1),
            ('Water Heater Repair', 'Water heater maintenance and repair', 200.00, 2, 1),
            ('Electrical Repair', 'Fix electrical issues and wiring problems', 130.00, 3, 1),
            ('Light Installation', 'Install new lighting fixtures', 70.00, 3, 1),
            ('Circuit Repair', 'Electrical circuit diagnosis and repair', 150.00, 3, 1),
            ('AC Repair', 'Air conditioner repair and maintenance', 180.00, 7, 1),
            ('Washing Machine Repair', 'Washing machine diagnosis and repair', 120.00, 7, 1),
            ('Refrigerator Service', 'Refrigerator maintenance and repair', 160.00, 7, 1)
        ]
        cursor.executemany('''
            INSERT INTO services (name, description, price, category_id, provider_id)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_services)
        print("Inserted sample services")

        # Insert sample addresses
        sample_addresses = [
            (1, 'Home', 'No. 15, Jalan Suria 12, Taman Suria', 'Johor Bahru, Johor 81100', True),
            (1, 'Work', 'Block A-12-3, Plaza Sentral, Jalan Stesen Sentral 5', 'Kuala Lumpur 50470', False),
            (1, "Parent's House", 'No. 27, Lorong Kelapa 3, Taman Indah', 'Penang 11900', False)
        ]
        cursor.executemany('''
            INSERT INTO addresses (user_id, type, address, city, is_default)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_addresses)
        print("Inserted sample addresses")

        # Commit the changes
        conn.commit()
        print("\nAll changes committed successfully!")

    except sqlite3.Error as e:
        print(f"SQLite error occurred: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'conn' in locals():
            conn.close()
            print("Database connection closed")
    
if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization completed!")