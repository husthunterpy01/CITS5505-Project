from app import app
from app.seed import seed_database
from app.extensions import socketio

if __name__ == '__main__':
    seed_database()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
