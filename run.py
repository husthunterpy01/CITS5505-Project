from app import app
from app.seed import seed_database

if __name__ == '__main__':
    seed_database()
    app.run(debug=True)