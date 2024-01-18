import sqlite3
connection = sqlite3.connect('database.db')

with open('setup.sql') as f:
    connection.executescript(f.read())
