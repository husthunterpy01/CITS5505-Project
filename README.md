# SwanFlip - a trade marketplace for UWA student
This is the project followed by the subject CITS5505 Agile Web Development (SEM-1-2026)

## Introduction
**SwanFlip** is dedicated peer-to-peer marketplace platform designed for the University of Western Australia students. 

Being a student is expensive, and campus life moves fast. uswap provides a secure, localized platform where UWA students can buy, sell, or trade textbooks, lab gear, electronics, and furniture. By keeping trade within the Crawley and Albany campuses, we aim to reduce the financial burden on students while promoting a circular economy that keeps usable items out of landfills.

The application will be built using Python Flask for the backend and JavaScript, HTML and CSS for the frontend.

## Group Member
This project is proposed by the following members:

| StudentId | Student Name | Github Account |
|-----------|--------------|---------------|
| 24715379  | Martin Dang  | [husthunterpy01](https://github.com/husthunterpy01) |
| 25054008  | Adarsh Sharma   | [aspoudel](https://github.com/aspoudel)   |
| 21941306  | Daniel Collier  | [nathanielcollenstein-cmd](https://github.com/nathanielcollenstein-cmd) |
| 24819852 |Roshan Shanker | [roshss2508](https://github.com/Roshss2508) |

## Technologies
This project is built using a client-server architecture with the following core technologies:
* Frontend: Standard HTML, CSS, and JavaScript.
* Styling: Tailwind CSS or Bootstrap for a responsive design
* Dynamic Interactions: jQuery for DOM manipulation and AJAX for seamless data updates.
* Backend: Flask (Python) to handle application logic and user sessions.
* Database: SQLite for data persistence, managed via SQLAlchemy.

## Project Structure
```
CITS5505-Project/
├── app/                               Flask application package
│   ├── __init__.py                    App setup, blueprint registration, context processors
│   ├── chat/
│   │   ├── __init__.py
│   │   └── chat.py                    SocketIO chat event handlers
│   ├── config.py                      Environment-based configuration
│   ├── extensions.py                  SQLAlchemy, Migrate, SocketIO, CSRF instances
│   ├── forms.py                       Flask-WTF forms
│   ├── models.py                      SQLAlchemy models
│   ├── route.py                       Main web/API routes
│   ├── seed.py                        Seed data generator
│   ├── service/                       Business/domain services
│   │   ├── authservice.py
│   │   ├── chatservice.py
│   │   ├── geolocationservice.py
│   │   ├── logservice.py
│   │   ├── notificationservice.py
│   │   ├── paginationservice.py
│   │   ├── productlistingservice.py
│   │   └── productqueryservice.py
│   └── utils.py
├── docs/
├── migrations/
│   └── versions/                      Alembic migration history
├── static/
│   ├── assets/
│   ├── components/
│   ├── js/
│   ├── mock_userdata.json
│   ├── pages/                         Page-level CSS/JS (AdminPage, BrowsePage, etc.)
│   └── style.css
├── templates/                         Jinja templates (base, auth, browse, admin, profile, chat)
├── tests/
│   ├── conftest.py
│   ├── integration/                   Selenium live-server tests
│   │   ├── conftest.py
│   │   ├── live_server_entry.py
│   │   └── test_selenium_workflows.py
│   └── unit/                          Service/unit tests
│       ├── test_auth_service.py
│       ├── test_geolocation_service.py
│       └── test_product_listing_service.py
├── pytest.ini
├── requirements.txt
├── run.py                             SocketIO-enabled app entry point
└── README.md
```

The main split is simple: `app/` contains the backend logic, `templates/` holds rendered HTML, and `static/` stores the frontend assets served by Flask.

## Application launching

The frontend is served directly by Flask templates/static files, so there is no separate client build step.

### 1) Create and activate a virtual environment
```bash
# Create
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/app.db
GEOAPIFY_API_KEY=your-geoapify-api-key
```

### 4) Apply migrations
```bash
flask --app run.py db upgrade
```

### 5) Start the app (SocketIO + Flask)

Use the project entry file:
```bash
python run.py
```

`run.py` starts the app via `socketio.run(...)`, so websocket features (chat/notifications) are enabled.

The app runs at: `http://127.0.0.1:5000`

## Testing running

### Run all tests
```bash
pytest
```

### Run unit tests only
```bash
pytest tests/unit -q
```

### Run Selenium integration tests only
```bash
pytest tests/integration -q
```

Notes:
- Selenium tests automatically start a temporary live server and test database via `tests/integration/conftest.py`.
- You do **not** need to manually run `python run.py` before Selenium tests.
- To run Selenium with visible browser (not headless) on PowerShell:
  ```powershell
  $env:SELENIUM_HEADLESS="0"
  pytest tests/integration -q
  ```
