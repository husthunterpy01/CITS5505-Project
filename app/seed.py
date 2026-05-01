import argparse

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
            # Delete child tables first to avoid foreign-key issues.
            Message.query.delete()
            ProductImage.query.delete()
            Product.query.delete()
            Category.query.delete()
            User.query.delete()
            db.session.commit()
            
        if Product.query.first() and not force_reset:
            print("Seed skipped: products already exist.")
            print("Run with --force-reset to clear and reseed.")
            return

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
        users = [
            User(
                first_name="Alice",
                last_name="Nguyen",
                email="alice@example.com",
                password="password123",
                role="normal",
            ),
            User(
                first_name="Ben",
                last_name="Lee",
                email="ben@example.com",
                password="password123",
                role="normal",
            ),
            User(
                first_name="Carol",
                last_name="Tan",
                email="carol@example.com",
                password="password123",
                role="admin",
            ),
        ]

        users = []
        for first_name, last_name, email, raw_password, role in user_seed_data:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=_to_base64(raw_password),
                    role=role,
                )
                db.session.add(user)
                db.session.flush()
            users.append(user)

        category_seed_names = [
            "Electronics",
            "Books",
            "Home",
            "Fashion",
            "Sports",
            "Beauty",
            "Toys",
            "Automotive",
            "Garden",
            "Gaming",
        categories = [
            Category(category_name="Electronics"),
            Category(category_name="Books"),
            Category(category_name="Home"),
        ]

        categories = []
        for category_name in category_seed_names:
            category = Category.query.filter_by(category_name=category_name).first()
            if not category:
                category = Category(category_name=category_name)
                db.session.add(category)
                db.session.flush()
            categories.append(category)

        products = [
            Product(
                product_name="iPhone 12",
                description="Good condition, 128GB.",
                seller_id=users[0].user_id,
                category_id=categories[0].category_id,
                price=650.0,
                location="Perth",
                status="available",
            ),
            Product(
                product_name="Python Crash Course",
                description="Like new programming book.",
                seller_id=users[1].user_id,
                category_id=categories[1].category_id,
                price=25.0,
                location="Fremantle",
                status="available",
            ),
            Product(
                product_name="Desk Lamp",
                description="Warm light, minimal design.",
                seller_id=users[0].user_id,
                category_id=categories[2].category_id,
                price=30.0,
                location="Subiaco",
                status="sold",
            ),
        ]
        db.session.add_all(products)
        db.session.flush()

        images = [
            ProductImage(
                product_id=products[0].product_id,
                image_url="https://example.com/images/iphone12.jpg",
                is_primary=True,
            ),
            ProductImage(
                product_id=products[1].product_id,
                image_url="https://example.com/images/python-book.jpg",
                is_primary=True,
            ),
            ProductImage(
                product_id=products[2].product_id,
                image_url="https://example.com/images/desk-lamp.jpg",
                is_primary=True,
            ),
        ]
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
