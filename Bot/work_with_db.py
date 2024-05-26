import sqlite3


def create_database():
    conn = sqlite3.connect('telegram_users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT
    )
    ''')
    return conn


def add_elements(sender, conn):
    cursor = conn.cursor()
    user_id = sender.id
    username = sender.username
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)
        ''', (user_id, username))
    conn.commit()
    print(f'user {username} with id {user_id}')
