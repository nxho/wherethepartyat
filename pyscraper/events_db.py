import sqlite3

def init_db():
    print("Creating 'events' database")
    conn = sqlite3.connect('events_database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        datetime TEXT,
        location TEXT
        account TEXT
    )''')
    conn.close()

def persist_events(events):
    conn = sqlite3.connect('events_database.db')
    cursor = conn.cursor()
    for event in events:
        cursor.execute("INSERT INTO events (name, description, datetime, location) VALUES (?, ?, ?, ?)",
                       (event['name'], event['description'], event['datetime'], event['location']))
    conn.commit()
    conn.close()

def get_all_events():
    conn = sqlite3.connect('events_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * from events')
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    # init_db()
    get_all_events()
