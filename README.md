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

### Seeded mock users

`app/seed.py` populates the database with the following accounts for local testing and Selenium runs. Student emails follow the `8digits@student.uwa.edu.au` format; admin emails use `@uwa.edu.au`.

| Role          | Name           | Email                              | Password      |
|---------------|----------------|------------------------------------|---------------|
| Standard user | Alice Nguyen   | `20000002@student.uwa.edu.au`      | `password123` |
| Standard user | Ben Lee        | `20000003@student.uwa.edu.au`      | `password123` |
| Admin         | Carol Tan      | `carol.tan@uwa.edu.au`             | `admin123`    |
| Standard user | David Wong     | `20000004@student.uwa.edu.au`      | `password123` |
| Standard user | Eva Lim        | `20000005@student.uwa.edu.au`      | `password123` |
| Standard user | Farah Hassan   | `20000006@student.uwa.edu.au`      | `password123` |
| Standard user | George Tan     | `20000007@student.uwa.edu.au`      | `password123` |
| Standard user | Hannah Yeo     | `20000008@student.uwa.edu.au`      | `password123` |
| Standard user | Ivan Koh       | `20000009@student.uwa.edu.au`      | `password123` |
| Standard user | Jasmine Teo    | `20000010@student.uwa.edu.au`      | `password123` |
| Admin         | Nora Admin     | `nora.admin@uwa.edu.au`            | `admin123`    |

To reset and reseed the database:
```bash
python -m app.seed --force-reset
```

## Testing running

### Quick reference

| Goal | Command |
|------|---------|
| Run all tests (unit + integration) | `python -m pytest -v` |
| Run unit tests only | `python -m pytest tests/unit -v` |
| Run Selenium integration tests only (headless) | `python -m pytest tests/integration -v` |
| Run Selenium integration tests with a visible browser | `python -m pytest tests/integration -v --headful` |
| Force headless even if env says otherwise | `python -m pytest tests/integration -v --headless` |
| Run a single test | `python -m pytest tests/unit/test_auth_service.py::TestSignupUser -v` |

### Run all tests
```bash
python -m pytest -v
```

### Run unit tests only
```bash
python -m pytest tests/unit -v
```

### Run Selenium integration tests only
```bash
python -m pytest tests/integration -v
```

By default, Selenium runs **headless** (no visible browser window).

#### Headful vs Headless

Selenium mode can be controlled via pytest CLI flags or an environment variable.

**Option A — pytest CLI flags (preferred):**
```bash
# Default (headless)
python -m pytest tests/integration -v

# Watch the browser (headful)
python -m pytest tests/integration -v --headful

# Force headless (overrides --headful and env)
python -m pytest tests/integration -v --headless
```

**Option B — Environment variable:**
```powershell
# PowerShell - run headful
$env:SELENIUM_HEADLESS="0"
python -m pytest tests/integration -v

# PowerShell - back to headless
Remove-Item Env:SELENIUM_HEADLESS
```

```bash
# Mac/Linux - run headful
SELENIUM_HEADLESS=0 python -m pytest tests/integration -v
```

Priority order (highest first): `--headless` → `--headful` → `SELENIUM_HEADLESS` env → default headless.

#### Step delay (visual pacing)

When running headful, each Selenium action pauses briefly so you can follow along. Tune via `SELENIUM_STEP_DELAY` (seconds):

```powershell
# Slow it right down to 2s per step
$env:SELENIUM_STEP_DELAY="2"
python -m pytest tests/integration -v --headful

# Speed it up for CI (no pauses)
$env:SELENIUM_STEP_DELAY="0"
python -m pytest tests/integration -v
```

Notes:
- Selenium tests automatically start a temporary live server and test database via `tests/integration/conftest.py`.
- You do **not** need to manually run `python run.py` before Selenium tests.
