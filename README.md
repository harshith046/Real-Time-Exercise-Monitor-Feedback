# Real-Time Exercise Monitor & Feedback

## 📌 About the Project

The **Real-Time Exercise Monitor & Feedback System** is a computer vision-based application designed to assist individuals in performing physical exercises with proper form. It leverages real-time **pose estimation** to analyze user movements through a webcam and provides **instant corrective feedback**, helping improve technique and prevent injury.

Ideal for:
- 🧘‍♀️ Personal fitness routines
- 🏋️‍♂️ Remote training sessions
- 🏥 Physical therapy and rehabilitation

This project combines computer vision, pose analysis, and a user-friendly interface into a practical, at-home fitness monitoring solution.

---

## ⚙️ Features

- ✅ Real-time human pose tracking via webcam  
- ✅ Feedback on form and posture for exercises (hammer curls, squats, push up)  
- ✅ Interactive dashboards for users and administrators  
- ✅ Persistent exercise tracking with SQLite  
- ✅ Simple local deployment for personal or prototype use  

---

## 🚀 How to Run the Project

1. Clone the repository:  
   ```
   git clone https://github.com/harshith046/Real-Time-Exercise-Monitor-Feedback.git
   cd Real-Time-Exercise-Monitor-Feedback
   ```

3. Create and activate a virtual environment:  
   ```
   python -m venv venv 
   venv\Scripts\activate
   ```

5. Install dependencies:  
   ```pip install opencv-python mediapipe numpy matplotlib```

6. Run the application:  
   ```python main.py```

---

## 🗃️ Data Storage

User exercise data is saved locally in a SQLite database file named `users.db`. This allows tracking of form accuracy and progress across multiple sessions.

---

## 🧠 Technologies Used

- 🎥 **OpenCV** – For video capture and image processing  
- 🧍 **MediaPipe** – For real-time human pose estimation  
- 📊 **NumPy**, **Matplotlib** – For data processing and plotting  
- 🗄️ **SQLite** – For lightweight local data persistence

---

## 🤝 Contributions

Feel free to contribute by opening issues, submitting pull requests, or suggesting new features. All contributions that enhance functionality, usability, or accuracy are welcome!

---
