import argparse

from werkzeug.security import generate_password_hash

from app import app
from app.extensions import db
from app.models import Category, Message, Product, ProductImage, User


def seed_database(force_reset: bool = False) -> None:
    """
    Insert starter data into all database tables.
    Use force_reset=True to clear existing rows first.
    """
    with app.app_context():
        db.create_all()

        if force_reset:
            # Full reset including users.
            Message.query.delete()
            ProductImage.query.delete()
            Product.query.delete()
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

        categories = []
        for category_name in category_seed_names:
            category = Category.query.filter_by(category_name=category_name).first()
            if not category:
                category = Category(category_name=category_name)
                db.session.add(category)
                db.session.flush()
            categories.append(category)

        category_by_name = {
            category.category_name: category for category in Category.query.all()
        }

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
                    location=location,
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

        messages = [
            Message(
                product_id=products[0].product_id,
                sender_id=users[1].user_id,
                receiver_id=users[0].user_id,
                content="Hi, is this still available?",
            ),
            Message(
                product_id=products[0].product_id,
                sender_id=users[0].user_id,
                receiver_id=users[1].user_id,
                content="Yes, it is available.",
            ),
            Message(
                product_id=products[1].product_id,
                sender_id=users[0].user_id,
                receiver_id=users[1].user_id,
                content="Can you do $20?",
            ),
        ]
        db.session.add_all(messages)

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
