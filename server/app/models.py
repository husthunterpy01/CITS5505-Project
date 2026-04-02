from app.extensions import db
from datetime import datetime

# Create models
class Customer(db.Model):
    customerId = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False)
    admin_id = db.Column(db.String, db.ForeignKey('admin.adminId'), nullable=True)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    orders   = db.relationship('Order',   backref='customer', lazy=True)
    products = db.relationship('Product', backref='customer', lazy=True)

class Admin(db.Model):
    adminId = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    customers = db.relationship('Customer', backref='admin', lazy=True)

class Order(db.Model):
    orderId = db.Column(db.String, primary_key=True)
    customerId = db.Column(db.String, db.ForeignKey('customer.customerId'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    orderStatus = db.Column(db.String, nullable=False, default='pending')
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    order_products = db.relationship('OrderProduct', backref='order', lazy=True)

class Product(db.Model):
    productId = db.Column(db.String, primary_key=True)
    customerId = db.Column(db.String, db.ForeignKey('customer.customerId'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    availability = db.Column(db.String, nullable=False, default='available')
    price = db.Column(db.Float, nullable=False, default=0.0)
    location = db.Column(db.String, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    order_products = db.relationship('OrderProduct', backref='product', lazy=True)

class OrderProduct(db.Model):
    orderProductId = db.Column(db.String, primary_key=True)
    orderId = db.Column(db.String, db.ForeignKey('order.orderId'), nullable=False)
    productId = db.Column(db.String, db.ForeignKey('product.productId'), nullable=False)
    numberProdductPerOrder = db.Column(db.Integer, nullable=False, default=0)
