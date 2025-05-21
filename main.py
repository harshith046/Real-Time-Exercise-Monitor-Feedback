import sys
import cv2
import json
from pose_estimation.estimation import PoseEstimator
from exercises.squat import Squat
from exercises.hammer_curl import HammerCurl
from exercises.push_up import PushUp
from feedback.layout import layout_indicators
from feedback.information import get_exercise_info
from utils.draw_text_with_background import draw_text_with_background

def main(exercise_type):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Unable to access webcam.")
        return

    pose_estimator = PoseEstimator()

    if exercise_type == "hammer_curl":
        exercise = HammerCurl()
    elif exercise_type == "squat":
        exercise = Squat()
    elif exercise_type == "push_up":
        exercise = PushUp()
    else:
        print("Invalid exercise type.")
        return

    exercise_info = get_exercise_info(exercise_type)
    total_reps = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab a frame from the webcam. Exiting...")
            break

        results = pose_estimator.estimate_pose(frame, exercise_type)
        if results.pose_landmarks:
            if exercise_type == "squat":
                counter, angle, stage = exercise.track_squat(results.pose_landmarks.landmark, frame)
                layout_indicators(frame, exercise_type, (counter, angle, stage))
                total_reps = max(total_reps, counter)
            elif exercise_type == "hammer_curl":
                (counter_right, angle_right, counter_left, angle_left,
                 warning_message_right, warning_message_left, progress_right, progress_left, stage_right, stage_left) = exercise.track_hammer_curl(
                    results.pose_landmarks.landmark, frame)
                layout_indicators(frame, exercise_type,
                                  (counter_right, angle_right, counter_left, angle_left,
                                   warning_message_right, warning_message_left, progress_right, progress_left, stage_right, stage_left))
                rep_sum = counter_right + counter_left
                total_reps = max(total_reps, rep_sum)
            elif exercise_type == "push_up":
                counter, angle, stage = exercise.track_push_up(results.pose_landmarks.landmark, frame)
                layout_indicators(frame, exercise_type, (counter, angle, stage))
                total_reps = max(total_reps, counter)

        draw_text_with_background(frame, f"Exercise: {exercise_info.get('name', 'N/A')}", (40, 50), 
                                  cv2.FONT_HERSHEY_DUPLEX, 0.7, (255,255,255), (118,29,14,0.79), 1)
        draw_text_with_background(frame, f"Reps: {total_reps}", (40, 80), 
                                  cv2.FONT_HERSHEY_DUPLEX, 0.7, (255,255,255), (118,29,14,0.79), 1)
        draw_text_with_background(frame, f"Sets: {exercise_info.get('sets', 0)}", (40, 110), 
                                  cv2.FONT_HERSHEY_DUPLEX, 0.7, (255,255,255), (118,29,14,0.79), 1)

        cv2.namedWindow(f"{exercise_type.replace('_', ' ').title()} Tracker", cv2.WINDOW_NORMAL)
        cv2.resizeWindow(f"{exercise_type.replace('_', ' ').title()} Tracker", 1280, 720)
        cv2.imshow(f"{exercise_type.replace('_', ' ').title()} Tracker", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()

    result = {"exercise": exercise_type, "total_reps": total_reps}
    with open("exercise_result.json", "w") as f:
        json.dump(result, f)
    print(json.dumps(result))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide an exercise type (e.g., push_up, hammer_curl, squat).")
        sys.exit(1)
    exercise_type = sys.argv[1]
    main(exercise_type)
