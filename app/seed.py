import argparse
from werkzeug.security import generate_password_hash
from app import app
from app.extensions import db
from app.models import Category, Conversation, ConversationParticipant, Location, Logging, Message, Product, ProductImage, User
from flask_migrate import upgrade


def seed_database(force_reset: bool = False):
    """
    Insert starter data into all database tables.
    Use force_reset=True to clear existing rows first.
    """
    with app.app_context():
        if upgrade is not None:
            upgrade()
        db.create_all()

        if User.query.first() and not force_reset:
            print("Seed skipped: database already contains data.")
            print("Run with --force-reset to clear and reseed.")
            return

        if force_reset:
            Message.query.delete()
            ConversationParticipant.query.delete()
            Conversation.query.delete()
            Logging.query.delete()
            ProductImage.query.delete()
            Product.query.delete()
            Location.query.delete()
            Category.query.delete()
            User.query.delete()
            db.session.commit()

        user_seed_data = [
            ("Alice", "Nguyen", "alice@example.com", "password123", "normal"),
            ("Ben", "Lee", "ben@example.com", "password123", "normal"),
            ("Carol", "Tan", "carol@example.com", "admin123", "admin"),
            ("David", "Wong", "david@example.com", "password123", "normal"),
            ("Eva", "Lim", "eva@example.com", "password123", "normal"),
            ("Farah", "Hassan", "farah@example.com", "password123", "normal"),
            ("George", "Tan", "george@example.com", "password123", "normal"),
            ("Hannah", "Yeo", "hannah@example.com", "password123", "normal"),
            ("Ivan", "Koh", "ivan@example.com", "password123", "normal"),
            ("Jasmine", "Teo", "jasmine@example.com", "password123", "normal"),
        ]
        

        users = []
        for first_name, last_name, email, raw_password, role in user_seed_data:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=generate_password_hash(raw_password),
                    role=role,
                )
                db.session.add(user)
                db.session.flush()
            users.append(user)

        category_seed_names = [
            "Textbooks",
            "Electronics",
            "Furniture",
            "Bikes & Transport",
            "Kitchen",
            "Clothing",
        ]
        categories = []
        for name in category_seed_names:
            category = Category.query.filter_by(category_name=name).first()
            if not category:
                category = Category(category_name=name)
                db.session.add(category)
                db.session.flush()
            categories.append(category)

        location_seed_data = [
            ("Perth", 115.8605, -31.9505),
            ("Fremantle", 115.7439, -32.0569),
            ("Subiaco", 115.8233, -31.9489),
            ("Crawley", 115.8210, -31.9780),
            ("Nedlands", 115.8040, -31.9800),
            ("Joondalup", 115.7660, -31.7440),
            ("Osborne Park", 115.8270, -31.9000),
            ("Willetton", 115.8810, -32.0520),
        ]
        locations = [
            Location(location_name=name, longitude=longitude, latitude=latitude)
            for name, longitude, latitude in location_seed_data
        ]
        db.session.add_all(locations)
        db.session.flush()

        location_map = {location.location_name: location for location in locations}

        category_map = {c.category_name: c for c in categories}
        product_seed_data = [
            ("iPhone 12", "Good condition, 128GB unlocked.", "Electronics", 650.0, "Perth", "available", 0),
            ("Dell XPS 13", "13-inch ultrabook with charger included.", "Electronics", 850.0, "Subiaco", "available", 1),
            ("Sony WH-1000XM4", "Noise-cancelling headphones in excellent condition.", "Electronics", 220.0, "Fremantle", "available", 2),
            ("Python Book", "Beginner-friendly Python textbook with practice tasks.", "Textbooks", 28.0, "Perth", "available", 3),
            ("Data Structures Notes", "University notes and solved examples.", "Textbooks", 20.0, "Nedlands", "available", 4),
            ("Calculus Workbook", "Workbook with minimal markings.", "Textbooks", 18.0, "Joondalup", "available", 5),
            ("Study Desk", "Wooden study desk with cable hole.", "Furniture", 120.0, "Cannington", "available", 6),
            ("Ergonomic Chair", "Mesh back support, adjustable height.", "Furniture", 140.0, "Perth", "available", 7),
            ("Bedside Table", "Compact bedside table, good condition.", "Furniture", 40.0, "Victoria Park", "sold", 8),
            ("Road Bike", "Lightweight frame, recently serviced.", "Bikes & Transport", 300.0, "Scarborough", "available", 9),
            ("Electric Scooter", "Up to 25km range, includes charger.", "Bikes & Transport", 380.0, "Perth", "available", 0),
            ("Skateboard", "Street deck with upgraded bearings.", "Bikes & Transport", 65.0, "Leederville", "available", 1),
            ("Air Fryer", "5L capacity, used for 6 months.", "Kitchen", 70.0, "Booragoon", "available", 2),
            ("Rice Cooker", "Reliable cooker with steamer tray.", "Kitchen", 35.0, "Murdoch", "available", 3),
            ("Jacket", "Warm winter jacket, size M.", "Clothing", 55.0, "Perth", "available", 4),
            ("Denim Jeans", "Slim fit jeans, size 32.", "Clothing", 30.0, "Subiaco", "available", 5),
        ]
        products = [
            Product(
                product_name=name,
                description=description,
                seller_id=users[seller_idx].user_id,
                category_id=category_map[category_name].category_id,
                price=price,
                location_id=location_map[location_name].location_id,
                status=status,
            )
            for name, description, category_name, price, location_name, status, seller_idx in product_seed_data
        ]
        db.session.add_all(products)
        db.session.flush()

        images = [
            ProductImage(product_id=products[0].product_id, image_url="https://d2e6ccujb3mkqf.cloudfront.net/df8d5f51-6de8-49df-92a5-059d278430a0-1_d1ccd919-3b3d-4bc1-b88f-a163a7422b33.jpg", is_primary=True),
            ProductImage(product_id=products[1].product_id, image_url="https://miro.medium.com/1*7N2toTOHbJELw-i1GFT-oA.jpeg", is_primary=True),
            ProductImage(product_id=products[2].product_id, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRYTWvXWPjPHNS8e4iEhtxLyJuD4NGvQDVacA&s", is_primary=True),
            ProductImage(product_id=products[3].product_id, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2vhUCN1DPc6Eo42kGpEzHz8PRTWsLpJGPcg&s", is_primary=True),
            ProductImage(product_id=products[4].product_id, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRwl7gWVfjDYVvGgz8s5WKbtjG60C6SHl39hQ&s", is_primary=True),
            ProductImage(product_id=products[5].product_id, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSyBDdyc5vniAoZMdQA9RNU2EqBlgNfQngFYQ&s", is_primary=True),
            ProductImage(product_id=products[6].product_id, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTSu7coXy-_70nfm-pm-iyHxQ6FrLNp9Sdw8A&s", is_primary=True),
            ProductImage(product_id=products[7].product_id, image_url="https://m.media-amazon.com/images/I/81D75XKZHiL.jpg", is_primary=True),
            ProductImage(product_id=products[8].product_id, image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTZKcFgjIg1ei6J16_VupczcpOtfJRxni4a7g&s", is_primary=True),
            ProductImage(product_id=products[9].product_id, image_url="https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/peripherals/keyboard/aw-pro-wireless-keyboard/media-galleries/ll/accessories-aw-pro-cp-keyboard-wh-gallery-1.psd?fmt=pjpg&pscan=auto&scl=1&wid=4717&hei=1631&qlt=100,1&resMode=sharp2&size=4717,1631&chrss=full&imwidth=5000", is_primary=True),
            ProductImage(product_id=products[10].product_id, image_url="https://m.media-amazon.com/images/I/61ZeYix5cbL._AC_SL1500_.jpg", is_primary=True),
            ProductImage(product_id=products[11].product_id, image_url="https://www.ikea.com/au/en/images/products/elloven-monitor-stand-with-drawer-white__1124027_pe874979_s5.jpg?f=xxs", is_primary=True),
        ]
        db.session.add_all(images)

        # Conversation and moderation seed data is intentionally skipped here.
        # The current project schema differs across branches/migrations for these tables,
        # and Issue 2 only requires stable product/category data for browse filtering.

        db.session.commit()
        print("Database seeded successfully.")


def main():
    parser = argparse.ArgumentParser(description="Seed SQLite database with sample data.")
    parser.add_argument(
        "--force-reset",
        action="store_true",
        help="Delete existing rows before seeding.",
    )
    args = parser.parse_args()
    seed_database(force_reset=args.force_reset)


if __name__ == "__main__":
    main()
