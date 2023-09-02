import sqlite3
import os
from os.path import abspath

events_db_path = os.getenv('EVENTS_DB_PATH') or abspath('../events_database.db')

def init_db():
    print("Creating 'events' database")
    conn = sqlite3.connect(events_db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        datetime TEXT,
        location TEXT,
        account TEXT
    )''')
    conn.close()

def persist_events(events):
    conn = sqlite3.connect(events_db_path)
    cursor = conn.cursor()
    for event in events:
        cursor.execute("INSERT INTO events (account, name, description, datetime, location) VALUES (?, ?, ?, ?, ?)",
                       (event['account'], event['name'], event['description'], event['datetime'], event['location']))
    conn.commit()
    conn.close()

def get_all_events():
    conn = sqlite3.connect(events_db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * from events')
    results = cursor.fetchall()
    conn.close()
    return results
