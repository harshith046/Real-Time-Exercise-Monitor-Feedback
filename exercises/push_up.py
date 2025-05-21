import cv2
import time
import pygame
from pose_estimation.angle_calculation import calculate_angle

pygame.mixer.init()
beep_sound = pygame.mixer.Sound("assets/beep.wav")

class PushUp:
    def __init__(self):
        self.counter = 0
        self.stage = "Initial"
        self.angle_threshold_up = 150
        self.angle_threshold_down = 70
        self.last_counter_update = time.time()

    def calculate_shoulder_elbow_wrist_angle(self, shoulder, elbow, wrist):
        return calculate_angle(shoulder, elbow, wrist)

    def track_push_up(self, landmarks, frame):
        h, w = frame.shape[:2]

        # Landmark
        shoulder_left = [int(landmarks[11].x * w), int(landmarks[11].y * h)]
        elbow_left = [int(landmarks[13].x * w), int(landmarks[13].y * h)]
        wrist_left = [int(landmarks[15].x * w), int(landmarks[15].y * h)]

        shoulder_right = [int(landmarks[12].x * w), int(landmarks[12].y * h)]
        elbow_right = [int(landmarks[14].x * w), int(landmarks[14].y * h)]
        wrist_right = [int(landmarks[16].x * w), int(landmarks[16].y * h)]

        hip_left = [int(landmarks[23].x * w), int(landmarks[23].y * h)]
        hip_right = [int(landmarks[24].x * w), int(landmarks[24].y * h)]
        knee_left = [int(landmarks[25].x * w), int(landmarks[25].y * h)]
        knee_right = [int(landmarks[26].x * w), int(landmarks[26].y * h)]

        nose = [int(landmarks[0].x * w), int(landmarks[0].y * h)]

        # Angle calculation
        angle_left = self.calculate_shoulder_elbow_wrist_angle(shoulder_left, elbow_left, wrist_left)
        angle_right = self.calculate_shoulder_elbow_wrist_angle(shoulder_right, elbow_right, wrist_right)

        color_left = (0, 255, 0) if self.angle_threshold_down < angle_left < self.angle_threshold_up else (0, 0, 255)
        color_right = (0, 255, 0) if self.angle_threshold_down < angle_right < self.angle_threshold_up else (0, 0, 255)

        self.draw_limbs(frame, shoulder_left, elbow_left, wrist_left, color_left)
        self.draw_limbs(frame, shoulder_right, elbow_right, wrist_right, color_right)
        self.show_angle(frame, elbow_left, angle_left)
        self.show_angle(frame, elbow_right, angle_right)

        current_time = time.time()

        # Rep counting
        if angle_left > self.angle_threshold_up and angle_right > self.angle_threshold_up:
            self.stage = "Starting position"
        elif self.angle_threshold_down < angle_left < self.angle_threshold_up and self.stage == "Starting position":
            self.stage = "Descent"
        elif angle_left < self.angle_threshold_down and self.stage == "Descent":
            self.stage = "Ascent"
            if current_time - self.last_counter_update > 1:
                self.counter += 1
                self.last_counter_update = current_time
            self.stage = "Starting position"

        # yellow color
        if angle_left < 45:
            self.draw_feedback_near_point(frame, elbow_left, "Elbow too flared!")
        if angle_right < 45:
            self.draw_feedback_near_point(frame, elbow_right, "Elbow too flared!")

        if angle_left > 170 and angle_right > 170:
            self.draw_feedback_near_point(frame, elbow_left, "Arms overextended")
            self.draw_feedback_near_point(frame, elbow_right, "Arms overextended")

        if nose[1] < shoulder_left[1] - 40 and nose[1] < shoulder_right[1] - 40:
            self.draw_feedback_near_point(frame, nose, "Neck craning!")

        avg_hip_y = (hip_left[1] + hip_right[1]) / 2
        avg_shoulder_y = (shoulder_left[1] + shoulder_right[1]) / 2
        avg_knee_y = (knee_left[1] + knee_right[1]) / 2

        if avg_hip_y > avg_shoulder_y + 30 and avg_hip_y > avg_knee_y - 30:
            center_hip = [(hip_left[0] + hip_right[0]) // 2, int(avg_hip_y)]
            self.draw_feedback_near_point(frame, center_hip, "Hips sagging!")

        return self.counter, angle_left, self.stage

    def draw_limbs(self, frame, shoulder, elbow, wrist, color):
        self.draw_line_with_style(frame, shoulder, elbow, color, 2)
        self.draw_line_with_style(frame, elbow, wrist, color, 2)
        self.draw_circle(frame, shoulder, color, 8)
        self.draw_circle(frame, elbow, color, 8)
        self.draw_circle(frame, wrist, color, 8)

    def show_angle(self, frame, point, angle):
        pos = (point[0] + 10, point[1] - 10)
        cv2.putText(frame, f'Angle: {int(angle)}', pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    def draw_line_with_style(self, frame, start_point, end_point, color, thickness):
        cv2.line(frame, start_point, end_point, color, thickness, lineType=cv2.LINE_AA)

    def draw_circle(self, frame, center, color, radius):
        cv2.circle(frame, center, radius, color, -1)

    def draw_feedback_near_point(self, frame, point, text):
        x, y = point[0], point[1]
        cv2.putText(frame, text, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        beep_sound.play()
