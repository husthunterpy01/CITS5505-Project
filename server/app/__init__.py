from flask import Flask

from app.config import Config
from app.extensions import db, migrate


def create_app(config_class=Config):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_object(config_class)

	db.init_app(app)
	migrate.init_app(app, db)

	# Import models so Flask-Migrate can discover metadata.
	__import__("app.models")

	@app.get("/")
	def index():
		return {"message": "Flask + SQLite connected!"}

	return app
