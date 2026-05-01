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
├── app/                          Flask application package
│   ├── __init__.py               App factory and blueprint registration
│   ├── config.py                Configuration values
│   ├── extensions.py            Shared Flask extensions
│   ├── models.py                Database models
│   ├── route.py                 Application routes
│   └── service/                 Domain services and business logic
├── docs/                        Project documentation
├── instance/                    Local runtime files such as the SQLite database
├── migrations/                  Alembic migration history
├── static/                      CSS, JavaScript, images, and other static assets
│   ├── assets/
│   ├── js/
│   ├── pages/
│   ├── mock_userdata.json
│   └── style.css
├── templates/                   Jinja templates rendered by Flask
├── tests/                       Automated tests
├── requirements.txt             Python dependencies
├── run.py                       Application entry point
└── README.md                    Project overview and setup guide
```

The main split is simple: `app/` contains the backend logic, `templates/` holds rendered HTML, and `static/` stores the frontend assets served by Flask.

## Application launching
### Client side

The frontend is served directly by Flask templates and static assets, so there is no separate client build step.

### Server side
The first step is to connect the server side to the database. To execute, follow these steps:
1. Create and activate a virtual environment
```
# Create
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```
2. Install the dependencies to run the server side
```
pip install -r requirements.txt
```

3. Configure environment variables

Create a **.env** file in the project root as follows:
```
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY="your-secret-key"
```

4. Create the database and tables for SQLite

Run the following commands:
```
# Initialise migrations folder (first time only)
flask --app run.py db init

# Generate migration script
flask --app run.py db migrate -m "<your_message>"

# Apply migration and create tables
flask --app run.py db upgrade
```

To test the query on the database, we can access to sqlite3 using the following commands:
```
sqlite3 instance/app.db
```
5. Execute the server side
```
flask --app run.py run
```

The server will be available at `http://127.0.0.1:5000`.



## Testing running
