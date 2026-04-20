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
* Backend: Flask (Python) to handle application logic and user sessions.* Database: SQLite for data persistence, managed via SQLAlchemy.

## Core features
```
CITS5505-PROJECT/
├── .venv/                        ← Virtual environment
├── client/                       ← Frontend
│   ├── assets/
│   │   └── logo/
│   │       ├── swanflip_logo.png
│   │       └── UWA_logo.webp
│   ├── components/
│   │   ├── footer.css
│   │   ├── footer.html
│   │   ├── header.css
│   │   └── header.html
│   ├── pages/
│   │   ├── AboutPage/
│   │   ├── SignInPage/
│   │   ├── SignUpPage/
│   │   └── WelcomePage/
│   ├── index.html
│   ├── index.js
│   └── style.css
├── docs/
├── server/                       ← Flask API
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models.py
│   │   └── route.py
│   ├── instance/
│   │   └── app.db                ← SQLite database (auto-generated)
│   ├── migrations/               ← Migration files (auto-generated)
│   ├── tests/
│   ├── .env
│   ├── requirements.txt
│   └── run.py
├── .gitignore
└── README.md
```

## Folder Structure

## Application launching
### Client side

### Server side
The first step is to connect the server side to database. To execute, we follow the following steps:
 1. Create and activate virtual environments
```
# Create
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```
2. Install the depedencies to run the server side
```
pip install -r requirements.txt
```

3. Configure environment variables

Create a **.env** file inside server folder as followed:
```
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY="your-secret-key"
```

4. Create the database and tables for sqlite

We will execute the following command in orders:
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

The server side will be available at `http://127.0.0.1:5000`



## Testing running
