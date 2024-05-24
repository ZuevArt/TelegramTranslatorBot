import sqlite3
import os

database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'telegram_users.db')

conn = sqlite3.connect(database_path)
cursor = conn.cursor()

cursor.execute('SELECT * FROM users')
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
