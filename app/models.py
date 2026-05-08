from datetime import datetime

from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    user_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name   = db.Column(db.String(100), nullable=False)
    last_name    = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password     = db.Column(db.String(255), nullable=False)
    role         = db.Column(db.String(20), nullable=False, default='user')
    is_report    = db.Column(db.Boolean, nullable=False, default=False)
    review       = db.Column(db.Text, nullable=True)
    created_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    products      = db.relationship('Product', backref='seller', lazy=True, foreign_keys='Product.seller_id')
    conversations = db.relationship('ConversationParticipant', backref='user', lazy=True, foreign_keys='ConversationParticipant.user_id')
    loggings      = db.relationship('Logging', backref='user', lazy=True, foreign_keys='Logging.user_id')
    sent_messages = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')


class Category(db.Model):
    __tablename__ = 'categories'

    category_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)

    products = db.relationship('Product', backref='category', lazy=True, foreign_keys='Product.category_id')


class Location(db.Model):
    __tablename__ = 'locations'

    location_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_name = db.Column(db.String(200), nullable=False)
    longitude     = db.Column(db.Float, nullable=False)
    latitude      = db.Column(db.Float, nullable=False)

    products = db.relationship('Product', backref='location', lazy=True, foreign_keys='Product.location_id')


class Product(db.Model):
    __tablename__ = 'products'

    product_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(200), nullable=False)
    description  = db.Column(db.Text, nullable=True)
    seller_id    = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    category_id  = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    price        = db.Column(db.Float, nullable=False, default=0.0)
    location_id  = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=False)
    is_legit     = db.Column(db.Boolean, nullable=False, default=True)
    status       = db.Column(db.String(20), nullable=False, default='available')
    created_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    review       = db.Column(db.Text, nullable=True)

    images        = db.relationship('ProductImage', backref='product', lazy=True, foreign_keys='ProductImage.product_id')
    conversations = db.relationship('Conversation', backref='product', lazy=True, foreign_keys='Conversation.product_id')


class ProductImage(db.Model):
    __tablename__ = 'product_images'

    image_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    image_url  = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, nullable=False, default=False)


class Conversation(db.Model):
    __tablename__ = 'conversations'

    conversation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id      = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=True)
    conv_type       = db.Column(db.String(30), nullable=False, default='direct')
    created_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    message_id      = db.Column(db.Integer, db.ForeignKey('messages.message_id', use_alter=True, name='fk_conversation_last_message'), nullable=True)
    participant_id  = db.Column(db.Integer, db.ForeignKey('conversation_participants.conversation_participant_id', use_alter=True, name='fk_conversation_participant'), nullable=True)

    messages     = db.relationship('Message', backref='conversation', lazy=True, foreign_keys='Message.conversation_id')
    participants = db.relationship('ConversationParticipant', backref='conversation', lazy=True, foreign_keys='ConversationParticipant.conversation_id')


class ConversationParticipant(db.Model):
    __tablename__ = 'conversation_participants'

    conversation_participant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id             = db.Column(db.Integer, db.ForeignKey('conversations.conversation_id'), nullable=False)
    user_id                     = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    participant_role            = db.Column(db.String(30), nullable=False, default='member')


class Message(db.Model):
    __tablename__ = 'messages'

    message_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.conversation_id'), nullable=False)
    sender_id       = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content         = db.Column(db.Text, nullable=False)
    is_read         = db.Column(db.Boolean, nullable=False, default=False)
    read_at         = db.Column(db.DateTime, nullable=True)
    sent_at         = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Logging(db.Model):
    __tablename__ = 'logging'

    logging_id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_id   = db.Column(db.Integer, nullable=False)
    action      = db.Column(db.String(100), nullable=False)
    reason      = db.Column(db.Text, nullable=True)
    created_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)