import argparse
import base64

from app import app
from app.extensions import db
from app.models import Category, Message, Product, ProductImage, User


def _to_base64(raw_password: str) -> str:
    return base64.b64encode(raw_password.encode("utf-8")).decode("utf-8")


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
            User(first_name="Alice", last_name="Nguyen", email="alice@example.com", password=_to_base64("password123"), role="normal"),
            User(first_name="Ben", last_name="Lee", email="ben@example.com", password=_to_base64("password123"), role="normal"),
            User(first_name="Carol", last_name="Tan", email="carol@example.com", password=_to_base64("admin123"), role="admin"),
            User(first_name="David", last_name="Wong", email="david@example.com", password=_to_base64("password123"), role="normal"),
            User(first_name="Eva", last_name="Lim", email="eva@example.com", password=_to_base64("password123"), role="normal"),
            User(first_name="Farah", last_name="Hassan", email="farah@example.com", password=_to_base64("password123"), role="normal"),
            User(first_name="George", last_name="Tan", email="george@example.com", password=_to_base64("password123"), role="normal"),
            User(first_name="Hannah", last_name="Yeo", email="hannah@example.com", password=_to_base64("password123"), role="normal"),
            User(first_name="Ivan", last_name="Koh", email="ivan@example.com", password=_to_base64("password123"), role="normal"),
            User(first_name="Jasmine", last_name="Teo", email="jasmine@example.com", password=_to_base64("password123"), role="normal"),
        ]
        db.session.add_all(users)
        db.session.flush()

        categories = [
            Category(category_name="Electronics"),
            Category(category_name="Books"),
            Category(category_name="Home"),
            Category(category_name="Fashion"),
            Category(category_name="Sports"),
            Category(category_name="Beauty"),
            Category(category_name="Toys"),
            Category(category_name="Automotive"),
            Category(category_name="Garden"),
            Category(category_name="Gaming"),
        ]
        db.session.add_all(categories)
        db.session.flush()

        products = [
            Product(product_name="iPhone 12", description="Good condition, 128GB.", seller_id=users[0].user_id, category_id=categories[0].category_id, price=650.0, location="Perth", status="available"),
            Product(product_name="Python Crash Course", description="Like new programming book.", seller_id=users[1].user_id, category_id=categories[1].category_id, price=25.0, location="Fremantle", status="available"),
            Product(product_name="Desk Lamp", description="Warm light, minimal design.", seller_id=users[2].user_id, category_id=categories[2].category_id, price=30.0, location="Subiaco", status="sold"),
            Product(product_name="Vintage Jacket", description="Leather jacket in great condition.", seller_id=users[3].user_id, category_id=categories[3].category_id, price=80.0, location="Perth", status="available"),
            Product(product_name="Yoga Mat", description="Non-slip mat, barely used.", seller_id=users[4].user_id, category_id=categories[4].category_id, price=20.0, location="Crawley", status="available"),
            Product(product_name="Skincare Set", description="3-piece skincare routine set.", seller_id=users[5].user_id, category_id=categories[5].category_id, price=40.0, location="Nedlands", status="available"),
            Product(product_name="LEGO Classic Box", description="Includes over 500 pieces.", seller_id=users[6].user_id, category_id=categories[6].category_id, price=45.0, location="Joondalup", status="available"),
            Product(product_name="Car Phone Holder", description="Universal dashboard mount.", seller_id=users[7].user_id, category_id=categories[7].category_id, price=15.0, location="Osborne Park", status="available"),
            Product(product_name="Garden Hose 20m", description="Durable hose for backyard use.", seller_id=users[8].user_id, category_id=categories[8].category_id, price=28.0, location="Willetton", status="available"),
            Product(product_name="Gaming Keyboard", description="Mechanical RGB keyboard.", seller_id=users[9].user_id, category_id=categories[9].category_id, price=70.0, location="Perth", status="available"),
        ]
        db.session.add_all(products)
        db.session.flush()

        images = [
            ProductImage(product_id=products[0].product_id, image_url="https://example.com/images/iphone12.jpg", is_primary=True),
            ProductImage(product_id=products[1].product_id, image_url="https://example.com/images/python-book.jpg", is_primary=True),
            ProductImage(product_id=products[2].product_id, image_url="https://example.com/images/desk-lamp.jpg", is_primary=True),
            ProductImage(product_id=products[3].product_id, image_url="https://example.com/images/vintage-jacket.jpg", is_primary=True),
            ProductImage(product_id=products[4].product_id, image_url="https://example.com/images/yoga-mat.jpg", is_primary=True),
            ProductImage(product_id=products[5].product_id, image_url="https://example.com/images/skincare-set.jpg", is_primary=True),
            ProductImage(product_id=products[6].product_id, image_url="https://example.com/images/lego-box.jpg", is_primary=True),
            ProductImage(product_id=products[7].product_id, image_url="https://example.com/images/car-phone-holder.jpg", is_primary=True),
            ProductImage(product_id=products[8].product_id, image_url="https://example.com/images/garden-hose.jpg", is_primary=True),
            ProductImage(product_id=products[9].product_id, image_url="https://example.com/images/gaming-keyboard.jpg", is_primary=True),
        ]
        db.session.add_all(images)

        messages = [
            Message(product_id=products[0].product_id, sender_id=users[1].user_id, receiver_id=users[0].user_id, content="Hi, is this still available?"),
            Message(product_id=products[0].product_id, sender_id=users[0].user_id, receiver_id=users[1].user_id, content="Yes, it is still available."),
            Message(product_id=products[1].product_id, sender_id=users[2].user_id, receiver_id=users[1].user_id, content="Can you share more photos?"),
            Message(product_id=products[2].product_id, sender_id=users[3].user_id, receiver_id=users[2].user_id, content="Is pickup possible tomorrow?"),
            Message(product_id=products[3].product_id, sender_id=users[4].user_id, receiver_id=users[3].user_id, content="Is the size medium?"),
            Message(product_id=products[4].product_id, sender_id=users[5].user_id, receiver_id=users[4].user_id, content="Can you do 18 dollars?"),
            Message(product_id=products[5].product_id, sender_id=users[6].user_id, receiver_id=users[5].user_id, content="Is this unopened?"),
            Message(product_id=products[6].product_id, sender_id=users[7].user_id, receiver_id=users[6].user_id, content="Any missing pieces?"),
            Message(product_id=products[7].product_id, sender_id=users[8].user_id, receiver_id=users[7].user_id, content="Will this fit an iPhone?"),
            Message(product_id=products[9].product_id, sender_id=users[0].user_id, receiver_id=users[9].user_id, content="Can you meet in the city today?"),
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
