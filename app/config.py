import os
from pathlib import Path
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> None:
        return None

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_URI = f"sqlite:///{(INSTANCE_DIR / 'app.db').as_posix()}"

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'hard-to-guess-secret'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or DEFAULT_DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,     
    }