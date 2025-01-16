import sqlite3

def init_db():
    # Connect to SQLite
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()

    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS reviews')
    cursor.execute('DROP TABLE IF EXISTS services')
    cursor.execute('DROP TABLE IF EXISTS categories')

    # Create categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        path TEXT NOT NULL,
        icon TEXT NOT NULL,
        service_count INTEGER NOT NULL
    )
    ''')

    # Create services table with additional fields
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        original_price REAL NOT NULL,
        rating INTEGER NOT NULL,
        reviews INTEGER NOT NULL,
        provider_name TEXT NOT NULL,
        provider_image TEXT NOT NULL,
        provider_role TEXT NOT NULL,
        image TEXT NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    ''')

    # Create reviews table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        date TEXT NOT NULL,
        user_avatar TEXT NOT NULL,
        FOREIGN KEY (service_id) REFERENCES services (id)
    )
    ''')

    # Sample categories data
    categories_data = [
        ("Carpenter", "carpenter", "🔨", 20),
        ("Cleaner", "cleaning", "🧹", 14),
        ("Painter", "painter", "🎨", 8),
        ("Electrician", "electrician", "⚡", 15),
        ("AC Repair", "ac-repair", "❄️", 10),
        ("Plumber", "plumber", "🔧", 25),
        ("Men's Salon", "mens-salon", "✂️", 5)
    ]

    cursor.executemany('INSERT INTO categories (name, path, icon, service_count) VALUES (?, ?, ?, ?)', categories_data)

    # Sample services data
    sample_services = [
        # Carpenter Services (category_id: 1)
        (1, "Furniture Repair", "Expert furniture repair service with attention to detail. We fix all types of furniture including chairs, tables, and cabinets.", 
         120.00, 150.00, 5, 180, "John Smith", "https://placehold.co/40x40", "Master Carpenter", "https://placehold.co/400x200"),
        (1, "Cabinet Installation", "Professional cabinet installation service. We handle everything from measurement to final installation.", 
         300.00, 350.00, 5, 120, "David Wilson", "https://placehold.co/40x40", "Cabinet Specialist", "https://placehold.co/400x200"),
        (1, "Door Repair", "Quick and efficient door repair service. We handle all types of door problems.", 
         90.00, 100.00, 5, 150, "Michael Wood", "https://placehold.co/40x40", "Door Expert", "https://placehold.co/400x200"),
        (1, "Custom Furniture Making", "Custom furniture design and creation. We bring your vision to life.", 
         500.00, 600.00, 5, 90, "Robert Carpenter", "https://placehold.co/40x40", "Custom Furniture Maker", "https://placehold.co/400x200"),

        # Cleaning Services (category_id: 2)
        (2, "Complete Kitchen Cleaning", "Thorough kitchen cleaning service including appliances, countertops, and cabinets.", 
         150.00, 180.00, 5, 150, "Mark Willions", "https://placehold.co/40x40", "Senior Cleaner", "https://placehold.co/400x200"),
        (2, "Window Cleaning", "Professional window cleaning service for both residential and commercial properties.", 
         80.00, 100.00, 5, 130, "Jane Cooper", "https://placehold.co/40x40", "Window Specialist", "https://placehold.co/400x200"),
        (2, "Living Room Cleaning", "Comprehensive living room cleaning service including furniture and carpet cleaning.", 
         200.00, 250.00, 5, 250, "Ronald Richards", "https://placehold.co/40x40", "Cleaning Expert", "https://placehold.co/400x200"),
        (2, "Deep House Cleaning", "Complete house deep cleaning service. We clean every corner of your home.", 
         350.00, 400.00, 5, 200, "Sarah Clean", "https://placehold.co/40x40", "Deep Clean Specialist", "https://placehold.co/400x200"),

        # Painter Services (category_id: 3)
        (3, "Interior Wall Painting", "Professional interior wall painting with premium quality paints.", 
         300.00, 350.00, 5, 90, "Mike Paint", "https://placehold.co/40x40", "Interior Painter", "https://placehold.co/400x200"),
        (3, "Exterior Painting", "Complete exterior house painting service with weather-resistant paints.", 
         500.00, 600.00, 5, 75, "John Color", "https://placehold.co/40x40", "Exterior Paint Expert", "https://placehold.co/400x200"),
        (3, "Furniture Painting", "Custom furniture painting and refinishing services.", 
         200.00, 250.00, 5, 60, "Lisa Art", "https://placehold.co/40x40", "Furniture Paint Specialist", "https://placehold.co/400x200"),
        (3, "Decorative Painting", "Artistic and decorative painting services for unique wall designs.", 
         400.00, 450.00, 5, 45, "Tom Design", "https://placehold.co/40x40", "Decorative Artist", "https://placehold.co/400x200"),

        # Electrician Services (category_id: 4)
        (4, "Wiring Installation", "Complete electrical wiring installation for new constructions or renovations.", 
         200.00, 250.00, 5, 120, "Tom Electric", "https://placehold.co/40x40", "Master Electrician", "https://placehold.co/400x200"),
        (4, "Circuit Repair", "Quick and reliable electrical circuit repair service.", 
         150.00, 180.00, 5, 95, "Sarah Spark", "https://placehold.co/40x40", "Circuit Specialist", "https://placehold.co/400x200"),
        (4, "Electrical Safety Inspection", "Comprehensive electrical safety inspection and certification.", 
         100.00, 120.00, 5, 150, "Mike Volt", "https://placehold.co/40x40", "Safety Inspector", "https://placehold.co/400x200"),
        (4, "Emergency Electrical Repair", "24/7 emergency electrical repair service.", 
         250.00, 300.00, 5, 200, "John Power", "https://placehold.co/40x40", "Emergency Electrician", "https://placehold.co/400x200"),

        # AC Repair Services (category_id: 5)
        (5, "AC Installation", "Professional AC installation service with warranty.", 
         300.00, 350.00, 5, 80, "Cool Tech", "https://placehold.co/40x40", "AC Installation Expert", "https://placehold.co/400x200"),
        (5, "AC Maintenance", "Regular AC maintenance service to ensure optimal performance.", 
         100.00, 120.00, 5, 150, "Frost Fix", "https://placehold.co/40x40", "AC Maintenance Pro", "https://placehold.co/400x200"),
        (5, "AC Repair", "Quick and reliable AC repair service for all brands.", 
         200.00, 250.00, 5, 120, "Chill Master", "https://placehold.co/40x40", "AC Repair Specialist", "https://placehold.co/400x200"),
        (5, "AC Deep Cleaning", "Complete AC deep cleaning service for better efficiency.", 
         150.00, 180.00, 5, 90, "Air Pro", "https://placehold.co/40x40", "AC Cleaning Expert", "https://placehold.co/400x200"),

        # Plumber Services (category_id: 6)
        (6, "Pipe Repair", "Expert pipe repair service for all types of plumbing issues.", 
         120.00, 150.00, 5, 180, "Flow Master", "https://placehold.co/40x40", "Master Plumber", "https://placehold.co/400x200"),
        (6, "Drain Cleaning", "Professional drain cleaning service with advanced equipment.", 
         100.00, 120.00, 5, 150, "Drain Pro", "https://placehold.co/40x40", "Drain Specialist", "https://placehold.co/400x200"),
        (6, "Water Heater Installation", "Water heater installation and replacement service.", 
         300.00, 350.00, 5, 90, "Heat Expert", "https://placehold.co/40x40", "Installation Specialist", "https://placehold.co/400x200"),
        (6, "Emergency Plumbing", "24/7 emergency plumbing service for urgent issues.", 
         200.00, 250.00, 5, 200, "Quick Fix", "https://placehold.co/40x40", "Emergency Plumber", "https://placehold.co/400x200"),

        # Men's Salon Services (category_id: 7)
        (7, "Haircut", "Professional men's haircut service with styling.", 
         30.00, 35.00, 5, 300, "Style Master", "https://placehold.co/40x40", "Senior Stylist", "https://placehold.co/400x200"),
        (7, "Beard Trim", "Expert beard trimming and styling service.", 
         20.00, 25.00, 5, 250, "Beard Pro", "https://placehold.co/40x40", "Beard Specialist", "https://placehold.co/400x200"),
        (7, "Hair Color", "Professional hair coloring service with quality products.", 
         50.00, 60.00, 5, 150, "Color Expert", "https://placehold.co/40x40", "Color Specialist", "https://placehold.co/400x200"),
        (7, "Facial", "Relaxing facial treatment with premium products.", 
         40.00, 45.00, 5, 200, "Face Pro", "https://placehold.co/40x40", "Facial Expert", "https://placehold.co/400x200")
    ]

    cursor.executemany('''
    INSERT INTO services (
        category_id, title, description, price, original_price,
        rating, reviews, provider_name, provider_image, provider_role, image
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_services)

    # Sample reviews for each service
    sample_reviews = []
    for service_id in range(1, len(sample_services) + 1):
        sample_reviews.extend([
            (service_id, "John Doe", 5, "Excellent service! Very professional and punctual.", "2024-01-15", "https://placehold.co/40x40"),
            (service_id, "Jane Smith", 5, "Great experience! Would highly recommend.", "2024-01-14", "https://placehold.co/40x40"),
            (service_id, "Mike Johnson", 4, "Good service, reasonable prices.", "2024-01-13", "https://placehold.co/40x40")
        ])

    cursor.executemany('''
    INSERT INTO reviews (
        service_id, user_name, rating, comment, date, user_avatar
    ) VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_reviews)

    conn.commit()
    conn.close()
    print("Database initialized successfully with all categories, services, and reviews!")

if __name__ == "__main__":
    init_db()