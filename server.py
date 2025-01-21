import os
import bcrypt
import sqlite3
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
import random

# Tracking logged-in user
SESSION = {}

# Global variable for captcha 
CAPTCHA_ANSWER = None

def render_template(template_name='index.html', path="templates", context=None):
    base_path = os.path.dirname(__file__)
    template_path = os.path.join(base_path, path, template_name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_str = f.read()
    except FileNotFoundError:
        html_str = f"Template {template_name} not found."

    # Replace
    if context:
        for key, value in context.items():
            html_str = html_str.replace(f"{{{{{key}}}}}", str(value))  
    return html_str

def home(environ):
    return render_template(template_name='index.html', path="templates")

def login(environ, start_response):
    global SESSION

    if environ['REQUEST_METHOD'] == 'POST':
        length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(length).decode('utf-8')
        form_data = parse_qs(post_data)

        email = form_data.get('email', [''])[0]
        password = form_data.get('password', [''])[0]

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        connection.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[4]):
            # Store user info in session
            SESSION['user'] = {'id': user[0], 'first_name': user[1], 'last_name': user[2], 'email': user[3]}
            return redirect('/update', start_response)
        else:
            print("Invalid credentials.")
            html = render_template(template_name='login.html', path="templates", context={"error_message": "Invalid credentials."})
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [html.encode('utf-8')]

    html = render_template(template_name='login.html', path="templates")
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [html.encode('utf-8')]

def register(environ, start_response):
    global CAPTCHA_ANSWER

    if environ['REQUEST_METHOD'] == 'POST':
        length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(length).decode('utf-8')
        form_data = parse_qs(post_data)

        first_name = form_data.get('first_name', [''])[0]
        last_name = form_data.get('last_name', [''])[0]
        email = form_data.get('email', [''])[0]
        password = form_data.get('password', [''])[0]
        captcha_input = form_data.get('captcha', [''])[0]

        # Checking captcha answer
        if int(captcha_input) != CAPTCHA_ANSWER:
            print("CAPTCHA failed. Regenerating CAPTCHA.")
            captcha_question = generate_captcha()
            html = render_template(template_name='register.html', path="templates", context={"captcha_question": captcha_question})
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [html.encode('utf-8')]

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            connection = sqlite3.connect('users.db')
            cursor = connection.cursor()
            cursor.execute(""" 
                INSERT INTO users (first_name, last_name, email, password)
                VALUES (?, ?, ?, ?)
            """, (first_name, last_name, email, hashed_password))
            connection.commit()
            print("User registered successfully.")
        except sqlite3.IntegrityError as e:
            print("Error inserting data into the database:", e)
            html = render_template(template_name='register.html', path="templates", context={"error_message": "Email already in use."})
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [html.encode('utf-8')]
        finally:
            connection.close()

        return redirect('/login', start_response)

    captcha_question = generate_captcha()

    html = render_template(template_name='register.html', path="templates", context={"captcha_question": captcha_question})
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [html.encode('utf-8')]

def generate_captcha():
    global CAPTCHA_ANSWER
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    CAPTCHA_ANSWER = num1 + num2
    print(f"Generated CAPTCHA: {num1} + {num2} = ?")
    return f"{num1} + {num2} = ?"

def update(environ, start_response):
    global SESSION

    if 'user' not in SESSION:
        return redirect('/login', start_response)

    user = SESSION['user']

    if environ['REQUEST_METHOD'] == 'POST':
        length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(length).decode('utf-8')
        form_data = parse_qs(post_data)

        first_name = form_data.get('first_name', [''])[0]
        last_name = form_data.get('last_name', [''])[0]
        email = form_data.get('email', [''])[0]
        password = form_data.get('password', [''])[0]
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute(""" 
            UPDATE users
            SET first_name = ?, last_name = ?, email = ?, password = ?
            WHERE id = ?
        """, (first_name, last_name, email, hashed_password, user['id']))
        connection.commit()
        connection.close()

        # Update user data in session
        SESSION['user'] = {'id': user['id'], 'first_name': first_name, 'last_name': last_name, 'email': email}
        return redirect('/update', start_response)

    html = render_template(template_name='update.html', path="templates", context=user)
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [html.encode('utf-8')]

def redirect(location, start_response):
    start_response('302 Found', [('Location', location)])
    return [b'']

def logout(environ, start_response):
    global SESSION
    SESSION.clear()
    return redirect('/login', start_response)

def app(environ, start_response):
    path = environ.get("PATH_INFO")

    if path == "/":
        html = home(environ)
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [html.encode("utf-8")]
    elif path == "/login":
        return login(environ, start_response)
    elif path == "/register":
        return register(environ, start_response)
    elif path == "/update":
        return update(environ, start_response)
    elif path == "/logout":
        return logout(environ, start_response)
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Page not found']

