import sqlite3
import os
import time

DATABASE = 'db.db'

# Function to initialize the database
def init_db():
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            # Create a table for messages
            cursor.execute('''
                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    verify_key TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT UNIQUE NOT NULL,
                    first_timestamp INTEGER NOT NULL
                )
            ''')
            conn.commit()

def insert_message(message, key):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO messages (message, timestamp, verify_key) VALUES (?, ?, ?)''', 
                       (message, int(time.time()), key))
        conn.commit()

def insert_node(address):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO nodes (address, first_timestamp) VALUES (?, ?)''', 
                       (address, int(time.time())))
        conn.commit()

def get_messages():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages')
        messages = cursor.fetchall()
    return messages

def get_nodes():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM nodes')
        nodes = cursor.fetchall()
    return nodes

def get_nodes_pub():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT (address) FROM nodes')
        nodes = cursor.fetchall()
    return nodes
