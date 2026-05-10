import os
from flask import Flask
from app.extensions import db, socketio
from app.config import Config
from app.route import main
from app.chat import chat
try:
    from flask_migrate import Migrate
except ModuleNotFoundError:
    Migrate = None

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

os.makedirs(INSTANCE_DIR, exist_ok=True)

app = Flask(
	__name__,
	template_folder=os.path.join(BASE_DIR, 'templates'),
	static_folder=os.path.join(BASE_DIR, 'static'),
	instance_path=INSTANCE_DIR,
	static_url_path='/static',
)
app.config.from_object(Config)

# Register database and migration extensions.
db.init_app(app)
if Migrate is not None:
    migrate = Migrate(app, db)

# Register application routes and API endpoints.
app.register_blueprint(main)

# Register SocketIO for real-time communication.
socketio.init_app(app, async_mode='threading')