import argparse
from werkzeug.security import generate_password_hash
from app import app
from app.extensions import db
from app.models import Category, Message, Product, ProductImage, User


def seed_database(force_reset: bool = False):
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
            Message.query.delete()
            ProductImage.query.delete()
            Product.query.delete()
            Category.query.delete()
            User.query.delete()
            db.session.commit()

        users = [
            User(first_name="Alice",last_name="Nguyen",email="alice@example.com",password=generate_password_hash("password123"), role="user"),
            User(first_name="Ben",last_name="Lee",email="ben@example.com",password=generate_password_hash("password123"),role="user"),
            User(first_name="Carol",last_name="Tan",email="carol@example.com",password=generate_password_hash("password123"),role="admin"),
            User(first_name="Daisy", last_name="Wong", email="daisy@example.com", password=generate_password_hash("password123"), role="user", is_report=True),
            User(first_name="Ethan", last_name="Smith", email="ethan@example.com", password=generate_password_hash("password123"), role="user", is_report=True),
            User(first_name="Fiona", last_name="Brown", email="fiona@example.com", password=generate_password_hash("password123"), role="user"),
            User(first_name="George", last_name="Wilson", email="george@example.com", password=generate_password_hash("password123"), role="user"),
            User(first_name="Hannah", last_name="Kim", email="hannah@example.com", password=generate_password_hash("password123"), role="user"),
            User(first_name="Ivan", last_name="Petrov", email="ivan@example.com", password=generate_password_hash("password123"), role="user")
        ]
        db.session.add_all(users)
        db.session.flush()


        categories = [
            Category(category_name="Electronics"),
            Category(category_name="Books"),
            Category(category_name="Home"),
            Category(category_name="Clothing"),
            Category(category_name="Fitness"),
            Category(category_name="Beauty"),
            Category(category_name="Toys"),
            Category(category_name="Automotive"),
            Category(category_name="Garden"),
            Category(category_name="Gaming"),
        ]
        db.session.add_all(categories)
        db.session.flush()

        products = [
            Product(product_name="iPhone 12", description="Good condition, 128GB.", seller_id=users[3].user_id, category_id=categories[0].category_id, price=650.0, location="Perth", status="available"),
            Product(product_name="Python Crash Course", description="Like new programming book.", seller_id=users[1].user_id, category_id=categories[1].category_id, price=25.0, location="Fremantle", status="available"),
            Product(product_name="Desk Lamp", description="Warm light, minimal design.", seller_id=users[2].user_id, category_id=categories[2].category_id, price=30.0, location="Subiaco", status="sold", is_legit=False),
            Product(product_name="Vintage Jacket", description="Leather jacket in great condition.", seller_id=users[3].user_id, category_id=categories[3].category_id, price=80.0, location="Perth", status="available"),
            Product(product_name="Yoga Mat", description="Non-slip mat, barely used.", seller_id=users[4].user_id, category_id=categories[4].category_id, price=20.0, location="Crawley", status="available"),
            Product(product_name="Skincare Set", description="3-piece skincare routine set.", seller_id=users[3].user_id, category_id=categories[5].category_id, price=40.0, location="Nedlands", status="available", is_legit=False),
            Product(product_name="LEGO Classic Box", description="Includes over 500 pieces.", seller_id=users[6].user_id, category_id=categories[6].category_id, price=45.0, location="Joondalup", status="available"),
            Product(product_name="Car Phone Holder", description="Universal dashboard mount.", seller_id=users[3].user_id, category_id=categories[7].category_id, price=15.0, location="Osborne Park", status="available"),
            Product(product_name="Garden Hose 20m", description="Durable hose for backyard use.", seller_id=users[8].user_id, category_id=categories[8].category_id, price=28.0, location="Willetton", status="available"),
            Product(product_name="Gaming Keyboard", description="Mechanical RGB keyboard.", seller_id=users[6].user_id, category_id=categories[9].category_id, price=70.0, location="Perth", status="available"),
            Product(product_name="Wireless Earbuds", description="Compact earbuds with charging case.", seller_id=users[3].user_id, category_id=categories[0].category_id, price=120.0, location="Perth", status="sold"),
            Product(product_name="Desk Organizer", description="Wooden organizer for study desk.", seller_id=users[3].user_id, category_id=categories[2].category_id, price=18.0, location="Nedlands", status="pending"),
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

        messages = [
            Message(
                product_id=products[0].product_id,
                sender_id=users[1].user_id,
                receiver_id=users[3].user_id,
                content="Hi, is this still available?",
            ),
            Message(
                product_id=products[0].product_id,
                sender_id=users[3].user_id,
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
