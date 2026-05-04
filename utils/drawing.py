# import cv2
# import numpy as np

# def draw_line(frame, y):
#     cv2.line(frame, (0, y), (frame.shape[1], y), (0, 0, 255), 2)

# def draw_box(frame, box, track_id):
#     x1, y1, x2, y2 = map(int, box)
#     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#     cv2.putText(frame, f"ID {track_id}",
#                 (x1, y1 - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 (0, 255, 0),
#                 2)


# import cv2
# import numpy as np

# def draw_polygon(frame, points, color):
#     pts = np.array(points, np.int32)
#     cv2.polylines(frame, [pts], isClosed=True, color=(0,0,255), thickness=2)



import cv2
import numpy as np

def draw_polygon(frame, points, color, label=None):
    pts = np.array(points, np.int32)
    cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)

    if label:
        x, y = pts[0]
        cv2.putText(
            frame,
            label,
            (x, max(y - 10, 25)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

def draw_clean_label(frame, text, x, y, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness = 2
    padding = 6

    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)

    # Keep label inside frame
    x = max(5, x)
    y = max(25, y)

    # Background rectangle
    cv2.rectangle(
        frame,
        (x, y - text_h - padding),
        (x + text_w + 2 * padding, y + padding // 2),
        (20, 20, 20),
        -1
    )

    # Border
    cv2.rectangle(
        frame,
        (x, y - text_h - padding),
        (x + text_w + 2 * padding, y + padding // 2),
        color,
        2
    )

    # Text
    cv2.putText(
        frame,
        text,
        (x + padding, y - 4),
        font,
        font_scale,
        color,
        thickness
    )