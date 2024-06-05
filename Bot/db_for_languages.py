import sqlite3


def create_usage_database():
    conn = sqlite3.connect('language_users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usage (
        user_id INTEGER PRIMARY KEY,
        russian INTEGER DEFAULT 0,
        english INTEGER DEFAULT 0,
        german INTEGER DEFAULT 0,
        french INTEGER DEFAULT 0,
        italian INTEGER DEFAULT 0,
        spanish INTEGER DEFAULT 0
    )
    ''')
    return conn


def update_language_usage(user_id, language, conn):
    cursor = conn.cursor()
    column = {
        'russian': 'russian',
        'english': 'english',
        'german': 'german',
        'french': 'french',
        'italian': 'italian',
        'spanish': 'spanish'
    }.get(language.lower())
    if column:
        cursor.execute(f'''
                INSERT OR IGNORE INTO usage (user_id, {column}) VALUES (?, 0)
            ''', (user_id,))
        cursor.execute(f'''
                UPDATE usage SET {column} = {column} + 1 WHERE user_id = ?
            ''', (user_id,))
        conn.commit()
        print(f'Updated {language} usage for user id {user_id}')
    else:
        print(f'Invalid language: {language}')
