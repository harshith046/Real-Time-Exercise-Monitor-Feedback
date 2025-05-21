import cv2 
import numpy as np
from feedback.information import get_exercise_info
from utils.draw_text_with_background import draw_text_with_background

def display_counter(frame, counter, position, color=(255, 255, 255), background_color=(0, 102, 204)):
    draw_text_with_background(
        frame, f'Counter: {counter}', position,
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, background_color, 2
    )

def display_stage(frame, stage, text, position, color=(255, 255, 255), background_color=(0, 102, 204)):
    label = f'{text}: '
    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]

    # Draw label
    draw_text_with_background(frame, label, position,
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, background_color, 2)

    # "up" or "down"
    if stage: 
        stage_position = (position[0] + label_size[0], position[1])
        stage_color = (0, 255, 0) if stage.lower() == 'up' else (0, 0, 255)
        draw_text_with_background(frame, stage, stage_position,
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, stage_color, background_color, 2)

def draw_progress_bar(frame, exercise, value, position, size, color=(0, 255, 0), background_color=(50, 50, 50)):
    x, y = position
    width, height = size

    exercise_info = get_exercise_info(exercise)
    reps = int(exercise_info.get("reps", 10))
    sets = int(exercise_info.get("sets", 3))
    max_value = reps * sets

    cv2.rectangle(frame, (x, y), (x + width, y + height), background_color, -1)

    # Progress bar
    progress_width = int((value / max_value) * width)
    cv2.rectangle(frame, (x, y), (x + progress_width, y + height), color, -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (128, 128, 128), 2)

    # Labels
    draw_text_with_background(frame, "Progress", (x, y - 10),
                              cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), (8, 103, 32), 1)

    # Percentage
    percentage_text = f"{int((value / max_value) * 100)}%"
    percent_size = cv2.getTextSize(percentage_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    percent_x = x + (width - percent_size[0]) // 2
    percent_y = y + (height + percent_size[1]) // 2

    cv2.putText(frame, percentage_text, (percent_x, percent_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

def draw_gauge_meter(frame, angle, text, position, radius, color=(0, 153, 255)):
    x, y = position

    # Outer Circle
    cv2.circle(frame, (x, y), radius, color, 2)

    # Filled Arc
    angle_start = -90
    angle_end = angle_start + angle
    axes = (radius, radius)
    cv2.ellipse(frame, (x, y), axes, 0, angle_start, angle_end, color, -1)

    # Needle Line
    end_x = int(x + radius * np.cos(np.radians(angle - 90)))
    end_y = int(y + radius * np.sin(np.radians(angle - 90)))
    cv2.line(frame, (x, y), (end_x, end_y), (255, 255, 255), 3)

    # Labels
    draw_text_with_background(frame, text, (x + 100, y),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), (40, 40, 40), 2)
    draw_text_with_background(frame, f'{int(angle)}', (x - 20, y + 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), (40, 40, 40), 2)
    cv2.putText(frame, '0', (x - 10, y - radius - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(frame, '180', (x - 25, y + radius + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
