import streamlit as st
import sqlite3
import time
import socket
import bcrypt
from utils.security import log_login, get_recent_failures, raise_alert
from utils.email_alerts import send_alert_email
import config

DB = "users.db"

def get_client_ip():
    return socket.gethostbyname(socket.gethostname())

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def create_user(username, password, email):
    conn = get_conn()
    try:
        query = "SELECT 1 FROM users WHERE username = ? OR email = ?"
        existing = conn.execute(query, (username, email)).fetchone()
        if existing:
            return False
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                     (username, hashed_password, email))
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR in create_user]: {e}")
        return False
    finally:
        conn.close()

def authenticate(username, password):
    try:
        conn = get_conn()
        result = conn.execute(
            "SELECT id, email, password FROM users WHERE username=?",
            (username,)
        ).fetchone()
        if result:
            user_id, email, stored_hashed_pw = result
            try:
                if bcrypt.checkpw(password.encode(), stored_hashed_pw.encode()):
                    return (user_id, email)
            except ValueError as ve:
                print(f"[BCRYPT ERROR] Invalid hash for user {username}: {ve}")
        return None
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        return None
    finally:
        conn.close()

def log_audit(actor, action, target=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO audit_logs (actor_username, action, target) VALUES (?, ?, ?)",
        (actor, action, target)
    )
    conn.commit()
    conn.close()

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        ip = get_client_ip()
        ua = "streamlit-app"

        user = authenticate(username, password)
        success = bool(user)

        log_login(username, success, ip, ua)

        fails = get_recent_failures(username)
        if fails >= 5:
            raise_alert(username, "Failed Login Spike", f"{fails} failures from IP: {ip}")

            user_email = None
            try:
                conn = get_conn()
                result = conn.execute("SELECT email FROM users WHERE username=?", (username,)).fetchone()
                if result:
                    user_email = result[0]
            except Exception as e:
                print(f"[DB ERROR] Failed to fetch user email for {username}: {e}")
            finally:
                conn.close()

            recipients = [config.ALERT_RECIPIENT]
            if user_email and user_email != config.ALERT_RECIPIENT:
                recipients.append(user_email)

            admin_body = (
                f"Security Alert: {fails} failed login attempts detected for user {username} from IP {ip}.\n"
                f"Please review the account activity in the admin dashboard."
            )
            user_body = (
                f"Dear {username},\n\n"
                f"We detected {fails} failed login attempts on your Exercise Tracker account from IP {ip}.\n"
                f"If this was not you, please secure your account by changing your password or contacting support.\n\n"
                f"Best,\nExercise Tracker Team"
            )

            try:
                if user_email:
                    send_alert_email(
                        user_email,
                        f"{config.EMAIL_SUBJECT_PREFIX} Suspicious Activity on Your Account",
                        user_body
                    )
                send_alert_email(
                    recipients,
                    f"{config.EMAIL_SUBJECT_PREFIX} Failed Login Spike for {username}",
                    admin_body
                )
            except Exception as e:
                print(f"[EMAIL ERROR] Failed to send alert email: {e}")
                st.warning("Failed to send alert email. Admins have been notified via logs.")

        if user:
            user_id, user_email = user
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.email = user_email or config.ALERT_RECIPIENT
            log_audit(username, "Login", username)
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def signup_page():
    st.title("User Sign Up")
    username = st.text_input("New Username")
    email = st.text_input("Email Address")
    password = st.text_input("New Password", type='password')
    if st.button("Sign Up"):
        if username.lower() == "admin":
            st.error("Admin account already exists. You cannot register as admin.")
            return
        if create_user(username, password, email):
            st.success("Account created! Please log in.")
            log_audit(username, "User Registered", username)
        else:
            st.error("Username or email already taken.")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        page = st.radio("Select:", ["Login", "Sign Up"])
        if page == "Login":
            login_page()
        else:
            signup_page()
    else:
        st.success(f"Welcome, {st.session_state.username}!")
        if st.button("Logout"):
            log_audit(st.session_state.username, "Logout", st.session_state.username)
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.email = ""
            st.rerun()
        if st.session_state.username == "admin":
            import admin_dashboard
            admin_dashboard.show_admin_dashboard()
        else:
            import exercise_dashboard
            exercise_dashboard.run_dashboard(st.session_state.username)

if __name__ == '__main__':
    main()