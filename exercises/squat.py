import cv2
import time
import pygame
from pose_estimation.angle_calculation import calculate_angle

class Squat:
    def __init__(self):
        self.counter = 0
        self.stage = "Initial"
        self.last_counter_update = time.time()
        self.last_warning_text = ""

        pygame.mixer.init()
        self.beep_sound = pygame.mixer.Sound("assets/beep.wav")

    def calculate_angle(self, a, b, c):
        return calculate_angle(a, b, c)

    def is_leg_posture_correct(self, angle):
        return 70 <= angle <= 130 or angle >= 160

    def is_back_posture_correct(self, angle):
        return angle > 60

    def track_squat(self, landmarks, frame):
        height, width = frame.shape[:2]

        hip_left = [int(landmarks[23].x * width), int(landmarks[23].y * height)]
        knee_left = [int(landmarks[25].x * width), int(landmarks[25].y * height)]
        ankle_left = [int(landmarks[27].x * width), int(landmarks[27].y * height)]

        hip_right = [int(landmarks[24].x * width), int(landmarks[24].y * height)]
        knee_right = [int(landmarks[26].x * width), int(landmarks[26].y * height)]
        ankle_right = [int(landmarks[28].x * width), int(landmarks[28].y * height)]

        shoulder_left = [int(landmarks[11].x * width), int(landmarks[11].y * height)]
        shoulder_right = [int(landmarks[12].x * width), int(landmarks[12].y * height)]

        angle_left = self.calculate_angle(hip_left, knee_left, ankle_left)
        angle_right = self.calculate_angle(hip_right, knee_right, ankle_right)

        back_angle_left = self.calculate_angle(shoulder_left, hip_left, knee_left)
        back_angle_right = self.calculate_angle(shoulder_right, hip_right, knee_right)

        color_left_leg = (0, 255, 0) if self.is_leg_posture_correct(angle_left) else (0, 0, 255)
        color_right_leg = (0, 255, 0) if self.is_leg_posture_correct(angle_right) else (0, 0, 255)

        color_left_back = (0, 255, 0) if self.is_back_posture_correct(back_angle_left) else (0, 0, 255)
        color_right_back = (0, 255, 0) if self.is_back_posture_correct(back_angle_right) else (0, 0, 255)

        self.draw_limbs(frame, hip_left, knee_left, ankle_left, color_left_leg)
        self.draw_limbs(frame, hip_right, knee_right, ankle_right, color_right_leg)

        self.draw_limbs(frame, shoulder_left, hip_left, knee_left, color_left_back)
        self.draw_limbs(frame, shoulder_right, hip_right, knee_right, color_right_back)

        self.show_angle(frame, knee_left, angle_left)
        self.show_angle(frame, knee_right, angle_right)

        current_time = time.time()

        # Rep count
        if angle_left > 160 and angle_right > 160:
            self.stage = "Up"
        elif 70 < angle_left < 130 and 70 < angle_right < 130 and self.stage == "Up":
            self.stage = "Down"
            if current_time - self.last_counter_update > 1:
                self.counter += 1
                self.last_counter_update = current_time
                self.beep_sound.play()

        # Feedback
        if angle_left < 60 or angle_right < 60:
            self.display_warning_near_landmark(frame, knee_left, "Too low! Avoid going past 60°.")

        if angle_left > 175 or angle_right > 175:
            self.display_warning_near_landmark(frame, knee_right, "Don't lock your knees at the top!")

        if back_angle_left < 60 or back_angle_right < 60:
            self.display_warning_near_landmark(frame, hip_left, "Keep your back straighter!")

        if self.stage == "Up":
            self.display_warning_near_landmark(frame, hip_left, "Push hips back to start the squat.")

        if self.stage == "Down":
            self.display_warning_near_landmark(frame, hip_right, "Drive up through your heels.")

        if (knee_left[0] - ankle_left[0] > 60) or (knee_right[0] - ankle_right[0] > 60):
            self.display_warning_near_landmark(frame, knee_right, "Don't let knees go too far forward!")

        if ankle_left[1] < knee_left[1] - 20 or ankle_right[1] < knee_right[1] - 20:
            self.display_warning_near_landmark(frame, ankle_right, "Keep your heels grounded!")

        ankle_distance = abs(ankle_right[0] - ankle_left[0])
        if ankle_distance < width * 0.15:
            self.display_warning_near_landmark(frame, ankle_left, "Widen your stance!")

        if abs(angle_left - angle_right) > 15:
            self.display_warning_near_landmark(frame, knee_left, "Keep both legs even!")

        if self.stage == "Down" and (angle_left > 130 or angle_right > 130):
            self.display_warning_near_landmark(frame, knee_right, "Go lower to complete the rep!")

        knee_distance = abs(knee_right[0] - knee_left[0])
        if knee_distance < ankle_distance:
            self.display_warning_near_landmark(frame, knee_left, "Don't let knees cave in!")

        return self.counter, angle_left, self.stage

    def draw_limbs(self, frame, point1, point2, point3, color):
        self.draw_line_with_style(frame, point1, point2, color, 2)
        self.draw_line_with_style(frame, point2, point3, color, 2)
        self.draw_circle(frame, point1, color, 8)
        self.draw_circle(frame, point2, color, 8)
        self.draw_circle(frame, point3, color, 8)

    def draw_line_with_style(self, frame, start, end, color, thickness):
        cv2.line(frame, start, end, color, thickness, lineType=cv2.LINE_AA)

    def draw_circle(self, frame, center, color, radius):
        cv2.circle(frame, center, radius, color, -1)

    def show_angle(self, frame, position, angle):
        cv2.putText(frame, str(int(angle)), tuple(position),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

    def display_warning_near_landmark(self, frame, position, message):
        x, y = position
        cv2.putText(frame, message, (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv2.LINE_AA)
