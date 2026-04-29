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

        if User.query.first() and not force_reset:
            print("Seed skipped: database already contains data.")
            print("Run with --force-reset to clear and reseed.")
            return

        if force_reset:
            # Delete child tables first to avoid foreign-key issues.
            Message.query.delete()
            ProductImage.query.delete()
            Product.query.delete()
            Category.query.delete()
            User.query.delete()
            db.session.commit()

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
        db.session.add_all(users)
        db.session.flush()

        categories = [
            Category(category_name="Electronics"),
            Category(category_name="Books"),
            Category(category_name="Home"),
        ]
        db.session.add_all(categories)
        db.session.flush()

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


def main() -> None:
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
