import sqlite3
from datetime import datetime, timedelta

DB = "users.db"

def log_login(username, success, ip, user_agent):
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO login_logs (username, success, ip, user_agent) VALUES (?, ?, ?, ?)",
        (username, int(success), ip, user_agent)
    )
    conn.commit()
    conn.close()

def get_recent_failures(username, window_minutes=5):
    since = datetime.utcnow() - timedelta(minutes=window_minutes)
    conn = sqlite3.connect(DB)
    cur = conn.execute(
        "SELECT COUNT(*) FROM login_logs WHERE username=? AND success=0 AND timestamp>=?",
        (username, since)
    )
    cnt = cur.fetchone()[0]
    conn.close()
    return cnt

def raise_alert(username, alert_type, details):
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO alerts (username, alert_type, details) VALUES (?, ?, ?)",
        (username, alert_type, details)
    )
    conn.commit()
    conn.close()
