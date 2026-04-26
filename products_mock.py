import sqlite3
from datetime import datetime

conn = sqlite3.connect("instance/app.db")
cur = conn.cursor()

# Seed categories first
categories = [
    "Textbooks",
    "Furniture",
    "Electronics",
    "Stationery",
    "Clothing"
]

for category_name in categories:
    cur.execute("""
        INSERT OR IGNORE INTO categories (category_name)
        VALUES (?)
    """, (category_name,))

# Get category ids from the database
cur.execute("SELECT category_id, category_name FROM categories")
category_map = {name: category_id for category_id, name in cur.fetchall()}

# Product seed data
products = [
    {
        "product_name": "Calculus Textbook",
        "description": "Good condition, a few highlighted pages, perfect for first-year units.",
        "seller_id": 1,
        "category_name": "Textbooks",
        "price": 35.00,
        "location": "UWA Crawley",
        "is_legit": 1,
        "status": "available",
        "image_url": "assets/logo/uwa_logo.webp"
    },
    {
        "product_name": "Desk Lamp",
        "description": "Compact study lamp with adjustable brightness. Works perfectly.",
        "seller_id": 2,
        "category_name": "Furniture",
        "price": 20.00,
        "location": "Perth",
        "is_legit": 1,
        "status": "available",
        "image_url": "assets/logo/uwa_logo.webp"
    },
    {
        "product_name": "Monitor Stand",
        "description": "Useful for keeping your study setup tidy and ergonomic.",
        "seller_id": 3,
        "category_name": "Electronics",
        "price": 18.50,
        "location": "Nedlands",
        "is_legit": 1,
        "status": "available",
        "image_url": "assets/logo/uwa_logo.webp"
    },
    {
        "product_name": "Lab Coat",
        "description": "Barely used lab coat, clean and ready for semester.",
        "seller_id": 4,
        "category_name": "Clothing",
        "price": 15.00,
        "location": "UWA Campus",
        "is_legit": 1,
        "status": "available",
        "image_url": "assets/logo/uwa_logo.webp"
    },
    {
        "product_name": "Office Chair",
        "description": "Comfortable chair for long study sessions at home.",
        "seller_id": 1,
        "category_name": "Furniture",
        "price": 60.00,
        "location": "Subiaco",
        "is_legit": 1,
        "status": "available",
        "image_url": "assets/logo/uwa_logo.webp"
    },
    {
        "product_name": "Notebook Bundle",
        "description": "A set of unused notebooks and stationery for the new term.",
        "seller_id": 2,
        "category_name": "Stationery",
        "price": 12.00,
        "location": "Perth",
        "is_legit": 1,
        "status": "available",
        "image_url": "assets/logo/uwa_logo.webp"
    }
]

for product in products:
    # Avoid duplicate product names if you run the script more than once
    cur.execute("""
        SELECT product_id FROM products WHERE product_name = ?
    """, (product["product_name"],))
    existing = cur.fetchone()

    if existing:
        continue

    cur.execute("""
        INSERT INTO products (
            product_name, description, seller_id, category_id,
            price, location, is_legit, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product["product_name"],
        product["description"],
        product["seller_id"],
        category_map[product["category_name"]],
        product["price"],
        product["location"],
        product["is_legit"],
        product["status"],
        datetime.now()
    ))

    product_id = cur.lastrowid

    cur.execute("""
        INSERT INTO product_images (
            product_id, image_url, is_primary
        ) VALUES (?, ?, ?)
    """, (
        product_id,
        product["image_url"],
        1
    ))

conn.commit()
conn.close()

print("Products, categories, and product images seeded successfully.")
