import streamlit as st
import subprocess
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from feedback.information import get_exercise_info
import sqlite3

def run_dashboard(username):
    st.title(f"{username}'s Exercise Tracking Dashboard")
    user_csv = f"exercise_history_{username}.csv"

    exercise_type = st.selectbox("Select an Exercise:", ["push_up", "hammer_curl", "squat"])

    exercise_info = get_exercise_info(exercise_type)
    st.subheader("Exercise Details")
    if exercise_info:
        st.markdown(f"**Name:** {exercise_info.get('name', 'N/A')}")
        target_muscles = exercise_info.get("target_muscles", [])
        st.markdown(f"**Target Muscles:** {', '.join(target_muscles) if target_muscles else 'N/A'}")
        st.markdown(f"**Equipment:** {exercise_info.get('equipment', 'N/A')}")
        st.markdown(f"**Reps:** {exercise_info.get('reps', 'N/A')}")
        st.markdown(f"**Sets:** {exercise_info.get('sets', 'N/A')}")
        st.markdown("**Benefits:**")
        for benefit in exercise_info.get("benefits", []):
            st.write(f"- {benefit}")
    else:
        st.info("No details available.")

    if st.button("Start Exercise Session", key="start_exercise"):
        st.info("Starting session. Perform exercise in the OpenCV window and press 'q' to quit.")
        subprocess.run(["python", "main.py", exercise_type], shell=False)

        result_file = "exercise_result.json"
        if os.path.exists(result_file):
            with open(result_file) as f:
                result = json.load(f)
            total_reps = result.get("total_reps", 0)
            st.success(f"Session Completed! Reps: {total_reps}")

            conn = sqlite3.connect("users.db", check_same_thread=False)
            try:
                conn.execute(
                    "INSERT INTO exercise_history (username, exercise_type, reps) VALUES (?, ?, ?)",
                    (username, exercise_type, total_reps)
                )
                conn.commit()
            except Exception as e:
                st.error(f"Failed to save exercise data: {e}")
            finally:
                conn.close()

            record = {
                "Exercise": exercise_type,
                "Reps": total_reps,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if os.path.exists(user_csv):
                df = pd.read_csv(user_csv)
                df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
            else:
                df = pd.DataFrame([record])
            df.to_csv(user_csv, index=False)
        else:
            st.error("Result not found.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Refresh"):
            st.rerun()
    with col2:
        if st.button("Clear History"):
            if os.path.exists(user_csv):
                os.remove(user_csv)
                st.success("History cleared.")
            else:
                st.info("No history to clear.")

    if os.path.exists(user_csv):
        history_df = pd.read_csv(user_csv)
        st.subheader("Exercise History")
        st.dataframe(history_df)

        filtered_df = history_df[history_df["Exercise"] == exercise_type]
        if not filtered_df.empty:
            filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
            filtered_df.sort_values("Date", inplace=True)

            st.subheader("Progress Over Time")
            plt.figure(figsize=(10, 5))
            plt.plot(filtered_df["Date"], filtered_df["Reps"], marker='o', linestyle='-', color='blue')
            plt.xlabel("Date")
            plt.ylabel("Reps")
            plt.title(f"{exercise_type.title()} Progress")
            st.pyplot(plt)

            st.subheader("Workout Summary")
            st.markdown(f"- **Avg Reps:** {filtered_df['Reps'].mean():.2f}")
            st.markdown(f"- **Max Reps:** {filtered_df['Reps'].max()}")
            st.markdown(f"- **Min Reps:** {filtered_df['Reps'].min()}")