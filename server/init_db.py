import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'people.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ProductionPlans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        quantity INTEGER,
        status TEXT,
        notes TEXT,
        customer TEXT,
        priority TEXT
    )
''')

conn.commit()
conn.close()

print("✅ ProductionPlans table created in people.db")
