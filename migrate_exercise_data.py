import sqlite3
import pandas as pd
import os
import glob

conn = sqlite3.connect("users.db")

csv_files = glob.glob("exercise_history_*.csv")

for csv_file in csv_files:
    username = csv_file.replace("exercise_history_", "").replace(".csv", "")
    try:
        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            conn.execute(
                """
                INSERT INTO exercise_history (username, exercise_type, reps, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (username, row["Exercise"], row["Reps"], row["Date"])
            )
        print(f"Migrated data for {username} from {csv_file}")
    except Exception as e:
        print(f"Error migrating {csv_file}: {e}")

conn.commit()
conn.close()
print("Migration completed.")