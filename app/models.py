from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    user_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name   = db.Column(db.String(100), nullable=False)
    last_name    = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role         = db.Column(db.String(20), nullable=False, default='normal') 
    is_report    = db.Column(db.Boolean, nullable=False, default=False)
    review       = db.Column(db.Text, nullable=True)
    created_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    products          = db.relationship('Product', backref='seller', lazy=True, foreign_keys='Product.seller_id')
    sent_messages     = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    received_messages = db.relationship('Message', backref='receiver', lazy=True, foreign_keys='Message.receiver_id')



class Category(db.Model):
    __tablename__ = 'categories'

    category_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)

    products = db.relationship('Product', backref='category', lazy=True, foreign_keys='Product.category_id')


class Product(db.Model):
    __tablename__ = 'products'

    product_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(200), nullable=False)
    description  = db.Column(db.Text, nullable=True)
    seller_id    = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    category_id  = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    price        = db.Column(db.Float, nullable=False, default=0.0)
    location     = db.Column(db.String(200), nullable=False)
    is_legit     = db.Column(db.Boolean, nullable=False, default=True)
    status       = db.Column(db.String(20), nullable=False, default='available')
    created_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    images   = db.relationship('ProductImage', backref='product', lazy=True, foreign_keys='ProductImage.product_id')
    messages = db.relationship('Message', backref='product', lazy=True, foreign_keys='Message.product_id')


class ProductImage(db.Model):
    __tablename__ = 'product_images'

    image_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    image_url  = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, nullable=False, default=False)


class Message(db.Model):
    __tablename__ = 'messages'

    message_id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id  = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    sender_id   = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content     = db.Column(db.Text, nullable=False)
    sent_at     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)