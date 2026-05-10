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
            # Full reset including users.
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
        else:
            # Keep users but reset listing data for idempotent seeds.
            Message.query.delete()
            ProductImage.query.delete()
            Product.query.delete()
            Category.query.delete()
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
        categories = [Category(category_name=name) for name in category_seed_names]
        db.session.add_all(categories)
        db.session.flush()

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

        category_by_name = {
            category.category_name: category for category in Category.query.all()
        }

        product_seed_data = [
            ("iPhone 12", "Good condition, 128GB unlocked.", "Electronics", 650.0, "Perth", "available", 3),
            ("Dell XPS 13", "13-inch ultrabook with charger included.", "Electronics", 850.0, "Subiaco", "available", 3),
            ("Sony WH-1000XM4", "Noise-cancelling headphones in excellent condition.", "Electronics", 220.0, "Fremantle", "available", 3),
            ("Python Book", "Beginner-friendly Python textbook with practice tasks.", "Textbooks", 28.0, "Perth", "available", 3),
            ("Data Structures Notes", "University notes and solved examples.", "Textbooks", 20.0, "Nedlands", "available", 3),
            ("Calculus Workbook", "Workbook with minimal markings.", "Textbooks", 18.0, "Joondalup", "available", 3),
            ("Study Desk", "Wooden study desk with cable hole.", "Furniture", 120.0, "Osborne Park", "available", 3),
            ("Ergonomic Chair", "Mesh back support, adjustable height.", "Furniture", 140.0, "Perth", "available", 3),
            ("Bedside Table", "Compact bedside table, good condition.", "Furniture", 40.0, "Willetton", "sold", 8),
            ("Road Bike", "Lightweight frame, recently serviced.", "Bikes & Transport", 300.0, "Fremantle", "available", 9),
            ("Electric Scooter", "Up to 25km range, includes charger.", "Bikes & Transport", 380.0, "Perth", "available", 0),
            ("Skateboard", "Street deck with upgraded bearings.", "Bikes & Transport", 65.0, "Subiaco", "available", 1),
            ("Air Fryer", "5L capacity, used for 6 months.", "Kitchen", 70.0, "Crawley", "available", 2),
            ("Rice Cooker", "Reliable cooker with steamer tray.", "Kitchen", 35.0, "Nedlands", "available", 3),
            ("Jacket", "Warm winter jacket, size M.", "Clothing", 55.0, "Perth", "available", 4),
            ("Denim Jeans", "Slim fit jeans, size 32.", "Clothing", 30.0, "Subiaco", "available", 5)
        ]
        products = []
        for name, description, category_name, price, location, status, seller_idx in product_seed_data:
            category = category_by_name.get(category_name)
            if not category:
                raise ValueError(f"Missing category '{category_name}' while seeding products.")
            products.append(
                Product(
                    product_name=name,
                    description=description,
                    seller_id=users[seller_idx].user_id,
                    category_id=category.category_id,
                    price=price,
                    location_id=location_map[location].location_id,
                    status=status,
                )
            )
        db.session.add_all(products)
        db.session.flush()

        image_url_by_product = {
            "iPhone 12": "https://www.apple.com/newsroom/images/product/iphone/geo/apple_iphone-12_2-up_geo_10132020_inline.jpg.large_2x.jpg",
            "Dell XPS 13": "https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/notebooks/xps-notebooks/xps-13-9350/media-gallery/graphite/notebook-xps-13-9350-t-oled-gy-gallery-4.psd?fmt=png-alpha&pscan=auto&scl=1&wid=3509&hei=2072&qlt=100,1&resMode=sharp2&size=3509,2072&chrss=full&imwidth=5000",
            "Sony WH-1000XM4": "https://i.ebayimg.com/images/g/-5MAAeSwg3Npyveh/s-l1600.webp",
            "Python Book": "https://i.etsystatic.com/59802327/r/il/c49d16/7885352408/il_1588xN.7885352408_gevf.jpg",
            "Data Structures Notes": "https://pictures.abebooks.com/isbn/9780914894209-us.jpg",
            "Calculus Workbook": "https://learnwell.co.nz/cdn/shop/files/9781988586618.gif?v=1694998219&width=823",
            "Study Desk": "https://i.ebayimg.com/images/g/BGsAAOSwPgNmQ36Y/s-l1600.webp",
            "Ergonomic Chair": "https://cloudofficestudio.com.au/cdn/shop/files/OCHAIR-H-FZ20-BK-150724-00.jpg?v=1774881247&width=832",
            "Bedside Table": "https://m.media-amazon.com/images/I/81rpKYnGBQL._AC_SX679_.jpg",
            "Road Bike": "https://www.canyon.com/dw/image/v2/BCML_PRD/on/demandware.static/-/Library-Sites-canyon-shared/default/dwe45b0c7a/images/blog/Road/01-blog-what-is-allroad-bike.jpg?sw=1145&sfrm=jpg&q=80",
            "Electric Scooter": "https://eozzie.com.au/cdn/shop/files/MiniWalker_Tiger_8_Electric_Scooter_6_Months_Free_Service_1800x1800.png?v=1751611108",
            "Skateboard": "https://skatesupplyaustralia.com.au/cdn/shop/files/imgi_87_zoo-york-logo-block-complete-skateboard-p9.png?v=1777474680",
            "Air Fryer": "https://img.lb.wbmdstatic.com/vim/live/webmd/consumer_assets/site_images/article_thumbnails/SEEDs/1800x1200-do-air-fryers-have-health-benefits-seed.jpg",
            "Rice Cooker": "https://assets.epicurious.com/photos/5e83af6772d6ca0008d69123/1:1/w_2945,h_2945,c_limit/RiceCooker_HERO_032720_5770_VOG.jpg",
            "Jacket": "https://m.media-amazon.com/images/I/81echJ4rAiL._AC_SX679_.jpg",
            "Denim Jeans": "https://www.tods.com/fashion/tods/X3M8249407LJDEU612/X3M8249407LJDEU612-30.jpg?imwidth=1620",
        }
        images = []
        for product in products:
            images.append(
                ProductImage(
                    product_id=product.product_id,
                    image_url=image_url_by_product.get(
                        product.product_name,
                        "https://images.pexels.com/photos/356056/pexels-photo-356056.jpeg?auto=compress&cs=tinysrgb&w=1200",
                    ),
                    is_primary=True,
                )
            )
        db.session.add_all(images)

        conversations = [
            Conversation(product_id=products[0].product_id),
            Conversation(product_id=products[1].product_id),
            Conversation(product_id=products[5].product_id),
            Conversation(product_id=products[9].product_id),
            Conversation(product_id=products[9].product_id),
        ]
        db.session.add_all(conversations)
        db.session.flush()

        participants = [
            ConversationParticipant(conversation_id=conversations[0].conversation_id, user_id=users[1].user_id),
            ConversationParticipant(conversation_id=conversations[0].conversation_id, user_id=users[3].user_id),
            ConversationParticipant(conversation_id=conversations[1].conversation_id, user_id=users[0].user_id),
            ConversationParticipant(conversation_id=conversations[1].conversation_id, user_id=users[1].user_id),
            ConversationParticipant(conversation_id=conversations[2].conversation_id, user_id=users[4].user_id),
            ConversationParticipant(conversation_id=conversations[2].conversation_id, user_id=users[3].user_id),
            ConversationParticipant(conversation_id=conversations[3].conversation_id, user_id=users[7].user_id),
            ConversationParticipant(conversation_id=conversations[3].conversation_id, user_id=users[6].user_id),
            ConversationParticipant(conversation_id=conversations[4].conversation_id, user_id=users[0].user_id),
            ConversationParticipant(conversation_id=conversations[4].conversation_id, user_id=users[6].user_id),
        ]
        db.session.add_all(participants)
        db.session.flush()

        messages = [
            Message(
                conversation_id=conversations[0].conversation_id,
                sender_id=users[1].user_id,
                content="Hi, is this still available?",
            ),
            Message(
                conversation_id=conversations[0].conversation_id,
                sender_id=users[3].user_id,
                content="Yes, it is available.",
            ),
            Message(
                conversation_id=conversations[1].conversation_id,
                sender_id=users[0].user_id,
                content="Can you do $20?",
            ),
            Message(
                conversation_id=conversations[2].conversation_id,
                sender_id=users[4].user_id,
                content="Is this skincare set unused and sealed?",
            ),
            Message(
                conversation_id=conversations[2].conversation_id,
                sender_id=users[3].user_id,
                content="Yes, still sealed and ready for pickup.",
            ),
            Message(
                conversation_id=conversations[3].conversation_id,
                sender_id=users[7].user_id,
                content="Could you hold the keyboard until Friday?",
            ),
            Message(
                conversation_id=conversations[4].conversation_id,
                sender_id=users[0].user_id,
                content="Hi George, is the gaming keyboard still available?",
            ),
            Message(
                conversation_id=conversations[4].conversation_id,
                sender_id=users[6].user_id,
                content="Hi Alice, yes it is available and works perfectly.",
            ),
        ]
        db.session.add_all(messages)

        # Create an admin conversation (Carol is admin at index 2) with Alice (index 0)
        admin_conv = Conversation(product_id=products[0].product_id)
        db.session.add(admin_conv)
        db.session.flush()

        admin_participants = [
            ConversationParticipant(conversation_id=admin_conv.conversation_id, user_id=users[2].user_id),
            ConversationParticipant(conversation_id=admin_conv.conversation_id, user_id=users[0].user_id),
        ]
        db.session.add_all(admin_participants)
        db.session.flush()

        admin_messages = [
            Message(
                conversation_id=admin_conv.conversation_id,
                sender_id=users[2].user_id,
                content="Hello Alice, I can help with your issue.",
            ),
            Message(
                conversation_id=admin_conv.conversation_id,
                sender_id=users[0].user_id,
                content="Thanks Carol, I have a question about my listing.",
            ),
        ]
        db.session.add_all(admin_messages)

        logs = [
            Logging(user_id=users[2].user_id, target_type='user', target_id=users[3].user_id, action='report', reason='Repeated suspicious activity.'),
            Logging(user_id=users[2].user_id, target_type='product', target_id=products[2].product_id, action='flag', reason='Mismatch between description and condition.'),
            Logging(user_id=users[2].user_id, target_type='product', target_id=products[5].product_id, action='approve', reason='Reviewed and approved by admin.'),
        ]
        db.session.add_all(logs)

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
