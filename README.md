1. Technologies Used
-Python, SQLite, bcrypt, HTML, WSGI, Gunicorn
Requirements
To run this project, you will need to prepare:
Linux or Windows Subsystem for Linux (WSL) on Windows (because Gunicorn can be run only on Linux).
Need to run first users.py separete from the server so it can use database.

2. Implemented Functionalities and How They Were Realized:
User Registration:
Using a POST request to create a new user.The password is hashed using bcrypt.
User Login:
Checking the database for email and password. bcrypt is used to verify the password.
Account Update:
User update their information (first name, last name, email, and password) using a POST request to update database.
CAPTCHA:
CAPTCHA is dynamically generated in the generate_captcha function.

3. Predefined Functions Used:
bcrypt.hashpw(): Hashing password.
sqlite3.connect(): To connect to the database.
sqlite3.Cursor.execute(): For executing SQL queries.
wsgiref.simple_server.make_server(): Used to create and start the WSGI server.
render_template(): Custom function to render HTML.
redirect(): Custom function to redirect HTTP.

4. File Descriptions and Purposes:
index.html: The landing page of the app
login.html: The login of users with credentials
register.html: The registration with credentials and captcha
update.html: The page where the logged-in user can update information.
server.py: Handles all routing, logic for registration, login, update, and user sessions.
users.py: File you will need to run in order to create the database. 
