from flask import Flask
from flask_migrate import Migrate

from app.config import Config
from app.models import db

app = Flask(__name__)
app.config.from_object(Config)

# Register database and migration extensions.
db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    return {'message': 'Flask + SQLite connected!'}
