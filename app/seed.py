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

        if force_reset:
            # Delete child tables first to avoid foreign-key issues.
            Message.query.delete()
            ProductImage.query.delete()
            Product.query.delete()
            Category.query.delete()
            User.query.delete()
            db.session.commit()

        # Only skip when product rows already exist.
        # This allows recovery from partial states (e.g. users exist but products are empty).
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
            ProductImage(product_id=products[0].product_id, image_url="https://www.apple.com/newsroom/images/product/iphone/geo/apple_iphone-12_2-up_geo_10132020_inline.jpg.large.jpg", is_primary=True),
            ProductImage(product_id=products[1].product_id, image_url="https://miro.medium.com/1*bK7mTjpXcWosebjDQsZgYA.jpeg", is_primary=True),
            ProductImage(product_id=products[2].product_id, image_url="https://lifeinteriors.com.au/cdn/shop/products/DL-MFL-MARG-SABR-LIFESTYLE.jpg?v=1666064170&width=800", is_primary=True),
            ProductImage(product_id=products[3].product_id, image_url="https://www.arcanefox.com/cdn/shop/files/custom-mens-trucker-distressed-leather-jacket-in-dark-brown-arcane-fox.png?v=1704898302&width=533", is_primary=True),
            ProductImage(product_id=products[4].product_id, image_url="https://contents.mediadecathlon.com/p2939785/k$84ca93a383ab82ea901a517640dc2590/8-mm-grippy-and-comfortable-gentle-yoga-mat-burgundy-kimjaly-8644104.jpg", is_primary=True),
            ProductImage(product_id=products[5].product_id, image_url="https://assets.manscaped.com/manscaped-prod/image/upload/f_png,h_1000,w_1000,f_auto,q_auto/v1/site-assets/strapi-assets/mens-advanced-skincare-set/mens-advanced-skincare-set_buy-box-6?_a=AXALAXh0", is_primary=True),
            ProductImage(product_id=products[6].product_id, image_url="https://www.lego.com/cdn/cs/set/assets/bltf7601db33f12c491/10698_box1_na.png", is_primary=True),
            ProductImage(product_id=products[7].product_id, image_url="https://m.media-amazon.com/images/I/81D75XKZHiL.jpg", is_primary=True),
            ProductImage(product_id=products[8].product_id, image_url="https://valvewarehouseaustralia.com.au/wp-content/uploads/pvc-garden-hose-20m-1.jpg", is_primary=True),
            ProductImage(product_id=products[9].product_id, image_url="https://images.ctfassets.net/w5r1fvmogo3f/2Sx0d0xP1sqQ4lqnNghSTr/f7fc939bbb9f196bdd62805af0642dd6/3f91bf6de6ad4e3ca3c86bd3b46264c5.jpg", is_primary=True),
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
