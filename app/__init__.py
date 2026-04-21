import os

from flask import Flask
from flask_migrate import Migrate

from app.config import Config
from app.models import db
from app.route import main

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(
	__name__,
	template_folder=os.path.join(BASE_DIR, 'templates'),
	static_folder=os.path.join(BASE_DIR, 'static'),
	static_url_path='/static',
)
app.config.from_object(Config)

# Register database and migration extensions.
db.init_app(app)
migrate = Migrate(app, db)

# Register application routes and API endpoints.
app.register_blueprint(main)
