import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from utils.email_alerts import send_alert_email
import config

def get_conn():
    return sqlite3.connect('users.db', check_same_thread=False) 

def fetch_df(query, conn, params=None):
    try:
        if params is None:
            params = ()
        df = pd.read_sql_query(query, conn, params=params)
        print("Fetched DataFrame:\n", df)
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def export_csv(df, filename):
    if df is not None and not df.empty:
        st.write("Preview of CSV:")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name=filename,
            mime='text/csv'
        )
    else:
        st.warning("No data to export.")

def show_user_management():
    conn = get_conn()
    query = "SELECT id, username, email FROM users"
    df = fetch_df(query, conn)

    if df is not None:
        st.write(df)

def show_suspicious_activity():
    st.subheader("Suspicious Activity Alerts")
    conn = get_conn()
    df = fetch_df("SELECT id, username, alert_type, details, is_resolved, timestamp FROM alerts ORDER BY timestamp DESC", conn)
    st.dataframe(df)
    export_csv(df, "alerts.csv")

    to_resolve = st.multiselect("Mark resolved (IDs):", df.id.tolist())
    if st.button("Resolve Alerts"):
        for aid in to_resolve:
            conn.execute("UPDATE alerts SET is_resolved=1 WHERE id=?", (aid,))
        conn.commit()
        st.success("Alerts resolved.")

def show_user_progress():
    st.subheader("User Progress")
    try:
        conn = get_conn()
        exercise_filter = st.selectbox("Filter by Exercise", ["All", "push_up", "squat", "hammer_curl"])
        query = """
        SELECT username, exercise_type, SUM(reps) as total_reps, COUNT(*) as sessions
        FROM exercise_history
        WHERE exercise_type = ? OR ? = 'All'
        GROUP BY username, exercise_type
        """
        df = fetch_df(query, conn, (exercise_filter, exercise_filter))

        if df is not None and not df.empty:
            st.write("**User Exercise Progress**")
            st.dataframe(df)
            export_csv(df, "user_progress.csv")
        else:
            st.warning("No user progress found in the database.")
    except Exception as e:
        st.error(f"Error fetching user progress: {e}")
    finally:
        conn.close()

def show_leaderboards():
    st.subheader("Leaderboards")
    mode = st.radio("Mode:", ["All Exercises", "By Exercise"])
    conn = get_conn()
    if mode == "All Exercises":
        df = fetch_df("""
          SELECT username, SUM(reps) AS total_reps
          FROM exercise_history
          GROUP BY username
          ORDER BY total_reps DESC
        """, conn)
        st.table(df)
        export_csv(df, "leaderboard_all.csv")
    else:
        ex = st.selectbox("Exercise", ["push_up", "squat", "hammer_curl"])
        df = fetch_df("""
          SELECT username, SUM(reps) AS total_reps
          FROM exercise_history
          WHERE exercise_type=?
          GROUP BY username
          ORDER BY total_reps DESC
        """, conn, (ex,))
        st.table(df)
        export_csv(df, f"leaderboard_{ex}.csv")

def show_audit_logs():
    st.subheader("Audit Logs")
    conn = get_conn() 
    df = fetch_df("SELECT actor_username, action, target, timestamp FROM audit_logs ORDER BY timestamp DESC", conn)
    st.dataframe(df)
    export_csv(df, "audit_logs.csv")

def show_admin_dashboard():
    st.title("Admin Control Panel")
    tabs = st.tabs([
        "1️⃣ Manage Users",
        "2️⃣ Suspicious Activity",
        "3️⃣ User Progress",
        "4️⃣ Leaderboards",
        "5️⃣ Audit & Export"
    ])
    with tabs[0]:
        show_user_management()
    with tabs[1]:
        show_suspicious_activity()
    with tabs[2]:
        show_user_progress()
    with tabs[3]:
        show_leaderboards()
    with tabs[4]:
        show_audit_logs()
