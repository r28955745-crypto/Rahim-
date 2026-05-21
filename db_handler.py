import sqlite3
import datetime

DB_NAME = 'tracker.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            mood INTEGER,
            study_hours REAL,
            sleep_hours REAL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_record(user_id, mood, study_hours, sleep_hours, comment=None):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.date.today()
    cursor.execute('''
        INSERT INTO records (user_id, date, mood, study_hours, sleep_hours, comment)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, today, mood, study_hours, sleep_hours, comment))
    conn.commit()
    conn.close()
    return True

def get_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, mood, study_hours, sleep_hours 
        FROM records 
        WHERE user_id = ? 
        ORDER BY date ASC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'date': datetime.datetime.strptime(str(row['date']), '%Y-%m-%d').date(),
            'mood': row['mood'],
            'study': row['study_hours'],
            'sleep': row['sleep_hours']
        })
    return history

def clear_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM records WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()