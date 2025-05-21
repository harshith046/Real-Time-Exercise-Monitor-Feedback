import sqlite3
import bcrypt

conn = sqlite3.connect("users.db")

conn.execute("DROP TABLE IF EXISTS users")
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT UNIQUE
);
''')

admin_username = 'admin'
admin_password = 'admin123'
admin_email = 'admin@gmail.com'
hashed_pw = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
             (admin_username, hashed_pw, admin_email))

conn.execute('''
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_username TEXT,
    action TEXT,
    target TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS login_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    success INTEGER,
    ip TEXT,
    user_agent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    alert_type TEXT,
    details TEXT,
    is_resolved INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS exercise_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    exercise_type TEXT,
    reps INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS exercise_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    exercise_type TEXT,
    reps INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')
conn.commit()
conn.close()
print("exercise_history table created.")