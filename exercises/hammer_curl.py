import cv2
import numpy as np
import pygame
from pose_estimation.angle_calculation import calculate_angle

class HammerCurl:
    def __init__(self):
        self.counter_right = 0
        self.counter_left = 0
        self.stage_right = None
        self.stage_left = None

        self.angle_threshold = 40  # Shoulder misalignment threshold
        self.flexion_angle_up = 155
        self.flexion_angle_down = 35

        self.angle_threshold_up = 155
        self.angle_threshold_down = 47

        pygame.mixer.init()
        self.beep_sound = pygame.mixer.Sound("assets/beep.wav")

    def play_beep(self):
        if not pygame.mixer.get_busy():
            self.beep_sound.play()

    def calculate_shoulder_elbow_hip_angle(self, shoulder, elbow, hip):
        return calculate_angle(elbow, shoulder, hip)

    def calculate_shoulder_elbow_wrist(self, shoulder, elbow, wrist):
        return calculate_angle(shoulder, elbow, wrist)

    def track_hammer_curl(self, landmarks, frame):
        def get_coords(index):
            return [int(landmarks[index].x * frame.shape[1]), int(landmarks[index].y * frame.shape[0])]

        shoulder_right, elbow_right, wrist_right, hip_right = map(get_coords, [11, 13, 15, 23])
        shoulder_left, elbow_left, wrist_left, hip_left = map(get_coords, [12, 14, 16, 24])

        angle_right_counter = self.calculate_shoulder_elbow_wrist(shoulder_right, elbow_right, wrist_right)
        angle_left_counter = self.calculate_shoulder_elbow_wrist(shoulder_left, elbow_left, wrist_left)
        angle_right = self.calculate_shoulder_elbow_hip_angle(shoulder_right, elbow_right, hip_right)
        angle_left = self.calculate_shoulder_elbow_hip_angle(shoulder_left, elbow_left, hip_left)

        self.draw_joint_lines(frame, shoulder_left, elbow_left, wrist_left, angle_left)
        self.draw_joint_lines(frame, shoulder_right, elbow_right, wrist_right, angle_right)

        self.show_angle_text(frame, elbow_left, angle_left_counter)
        self.show_angle_text(frame, elbow_right, angle_right_counter)

        warnings = []

        if abs(angle_right) > self.angle_threshold:
            warnings.append(("Right Misalignment!", shoulder_right))
        if abs(angle_left) > self.angle_threshold:
            warnings.append(("Left Misalignment!", shoulder_left))

        if wrist_right[1] < shoulder_right[1] - 20:
            warnings.append(("Right Wrist too High!", wrist_right))
        elif wrist_right[1] > elbow_right[1] + 40:
            warnings.append(("Right Wrist too Low!", wrist_right))

        if wrist_left[1] < shoulder_left[1] - 20:
            warnings.append(("Left Wrist too High!", wrist_left))
        elif wrist_left[1] > elbow_left[1] + 40:
            warnings.append(("Left Wrist too Low!", wrist_left))

        if abs(elbow_right[0] - shoulder_right[0]) > 70:
            warnings.append(("Right Elbow Flaring!", elbow_right))
        if abs(elbow_left[0] - shoulder_left[0]) > 70:
            warnings.append(("Left Elbow Flaring!", elbow_left))

        if angle_right_counter > 160:
            warnings.append(("Right Curl Too Short!", elbow_right))
        if angle_left_counter > 160:
            warnings.append(("Left Curl Too Short!", elbow_left))

        if warnings:
            self.play_beep()

        for text, position in warnings:
            cv2.putText(frame, " ", (position[0] - 25, position[1] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
            cv2.putText(frame, text, (position[0] - 60, position[1] - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Rep Count
        if angle_right_counter > self.angle_threshold_up:
            self.stage_right = "Flex"
        elif self.angle_threshold_down < angle_right_counter < self.angle_threshold_up and self.stage_right == "Flex":
            self.stage_right = "Up"
        elif angle_right_counter < self.angle_threshold_down and self.stage_right == "Up":
            self.stage_right = "Down"
            self.counter_right += 1

        # Rep Count
        if angle_left_counter > self.angle_threshold_up:
            self.stage_left = "Flex"
        elif self.angle_threshold_down < angle_left_counter < self.angle_threshold_up and self.stage_left == "Flex":
            self.stage_left = "Up"
        elif angle_left_counter < self.angle_threshold_down and self.stage_left == "Up":
            self.stage_left = "Down"
            self.counter_left += 1

        progress_right = 1 if self.stage_right == "Up" else 0
        progress_left = 1 if self.stage_left == "Up" else 0

        return (self.counter_right, angle_right_counter,
                self.counter_left, angle_left_counter,
                [w[0] for w in warnings if "Right" in w[0]],
                [w[0] for w in warnings if "Left" in w[0]],
                progress_right, progress_left,
                self.stage_right, self.stage_left)

    def draw_joint_lines(self, frame, shoulder, elbow, wrist, angle):
        color = (0, 255, 0) if abs(angle) <= self.angle_threshold else (0, 0, 255)
        self.draw_line_with_style(frame, shoulder, elbow, color, 4)
        self.draw_line_with_style(frame, elbow, wrist, (0, 0, 255), 4)
        for pt in [shoulder, elbow, wrist]:
            self.draw_circle(frame, pt, (255, 255, 255), 6)

    def draw_line_with_style(self, frame, pt1, pt2, color, thickness):
        cv2.line(frame, pt1, pt2, color, thickness)

    def draw_circle(self, frame, center, color, radius):
        cv2.circle(frame, center, radius, color, -1)

    def show_angle_text(self, frame, position, angle):
        cv2.putText(frame, str(int(angle)), (position[0] + 10, position[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
