import sqlite3
connection = sqlite3.connect('users.db')
cursor = connection.cursor()

sql_commad="""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL )
"""
cursor.execute(sql_commad)
connection.close()