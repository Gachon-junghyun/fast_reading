import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS pdfs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        pdf_name TEXT NOT NULL,
        progress TEXT NOT NULL,
        mode TEXT NOT NULL
    )
    ''')
    conn.close()
