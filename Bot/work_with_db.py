import sqlite3


def create_database():
    conn = sqlite3.connect('telegram_users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    last_message TEXT,
    language TEXT
    )
    ''')
    return conn


def get_last_translated_message(user_id, conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT last_message FROM users WHERE id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None


def add_elements(sender, target_language, message, conn):
    cursor = conn.cursor()
    user_id = sender.id
    username = sender.username
    last_translated_message = message
    language = target_language
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, username, last_message, language) VALUES (?, ?, ?, ?)
        ''', (user_id, username, last_translated_message, language))
    cursor.execute('''
           UPDATE users SET last_message = ? WHERE id = ?
       ''', (last_translated_message, user_id))
    conn.commit()
    print(f'user {username}, id {user_id} his(her) {last_translated_message} with {language}')


def add_last_message(user_id, last_message, conn):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET last_translated_message = ? WHERE id = ?
    ''', (last_message, user_id))
    conn.commit()
    print(f'Updated last translated message for user id {user_id}: {last_message}')
