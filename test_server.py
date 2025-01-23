import unittest
import sqlite3
import bcrypt
import os
import sys
import urllib.parse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import register, login, generate_captcha

class MockEnviron:
    def __init__(self, method='GET', content_length=0, input_data=b'', path_info=''):
        self.environ = {
            'REQUEST_METHOD': method,
            'CONTENT_LENGTH': content_length,
            'PATH_INFO': path_info,
            'wsgi.input': MockInput(input_data)
        }

    def __getitem__(self, key):
        return self.environ[key]

    def get(self, key, default=None):
        return self.environ.get(key, default)

class MockInput:
    def __init__(self, data):
        self.data = data

    def read(self, length):
        return self.data

class MockStartResponse:
    def __init__(self):
        self.status = None
        self.headers = None

    def __call__(self, status, headers):
        self.status = status
        self.headers = headers

class TestUserRegistrationAndLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists('users.db'):
            os.remove('users.db')
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def setUp(self):
        # Reset variables before each test
        global SESSION, CAPTCHA_ANSWER
        SESSION = {}
        CAPTCHA_ANSWER = None

    def test_successful_registration(self):
        global CAPTCHA_ANSWER
        CAPTCHA_ANSWER = None

        generate_captcha()
        captcha_answer = CAPTCHA_ANSWER
        print(f"captcha answrr is {captcha_answer}")

        input_data = urllib.parse.urlencode({
            'first_name': 'plamen', 
            'last_name': 'pandev', 
            'email': 'ppandev5@gmail.com', 
            'password': 'password123', 
            'captcha': str(captcha_answer)
        }).encode('utf-8')

        environ = {
            'REQUEST_METHOD': 'POST',
            'CONTENT_LENGTH': str(len(input_data)),
            'wsgi.input': MockInput(input_data)
        }
        start_response = MockStartResponse()

        register(environ, start_response)

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", ('ppandev5@gmail.com',))
        user = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(user, "User was not added to the database")
        self.assertEqual(user[1], 'plamen', "First name does not match")
        self.assertEqual(user[2], 'pandev', "Last name does not match")
        self.assertEqual(user[3], 'ppandev5@gmail.com', "Email does not match")

    def test_registration_duplicate_email(self):
        generate_captcha()
        captcha_answer1 = CAPTCHA_ANSWER

        input_data1 = urllib.parse.urlencode({
            'first_name': 'Plamen', 
            'last_name': 'Pandev', 
            'email': 'ppandev5@gmail.com', 
            'password': 'password123', 
            'captcha': str(captcha_answer1)
        }).encode('utf-8')

        environ1 = MockEnviron(
            method='POST', 
            content_length=len(input_data1), 
            input_data=input_data1
        )
        start_response1 = MockStartResponse()

        register(environ1, start_response1)

        generate_captcha()
        captcha_answer2 = CAPTCHA_ANSWER

        input_data2 = urllib.parse.urlencode({
            'first_name': 'plamen', 
            'last_name': 'pandev', 
            'email': 'ppandev5@gmail.com', 
            'password': 'password123', 
            'captcha': str(captcha_answer2)
        }).encode('utf-8')

        environ2 = MockEnviron(
            method='POST', 
            content_length=len(input_data2), 
            input_data=input_data2
        )
        start_response2 = MockStartResponse()

        result = register(environ2, start_response2)

        self.assertEqual(start_response2.status, '200 OK')

    def test_successful_login(self):
        generate_captcha()
        captcha_answer_reg = CAPTCHA_ANSWER

        input_data_reg = urllib.parse.urlencode({
            'first_name': 'Login', 
            'last_name': 'Test', 
            'email': 'login@example.com', 
            'password': '1234', 
            'captcha': str(captcha_answer_reg)
        }).encode('utf-8')

        environ_reg = MockEnviron(
            method='POST', 
            content_length=len(input_data_reg), 
            input_data=input_data_reg
        )
        start_response_reg = MockStartResponse()

        register(environ_reg, start_response_reg)

        input_data_login = urllib.parse.urlencode({
            'email': 'login@example.com', 
            'password': 'password123'
        }).encode('utf-8')

        environ_login = MockEnviron(
            method='POST', 
            content_length=len(input_data_login), 
            input_data=input_data_login
        )
        start_response_login = MockStartResponse()

        result = login(environ_login, start_response_login)

        self.assertEqual(start_response_login.status, '200 OK')

    def test_failed_login(self):
        input_data_login = urllib.parse.urlencode({
            'email': 'nonexistent@example.com', 
            'password': 'password'
        }).encode('utf-8')

        environ_login = MockEnviron(
            method='POST', 
            content_length=len(input_data_login), 
            input_data=input_data_login
        )
        start_response_login = MockStartResponse()

        result = login(environ_login, start_response_login)

        self.assertEqual(start_response_login.status, '200 OK')

if __name__ == '__main__':
    unittest.main()