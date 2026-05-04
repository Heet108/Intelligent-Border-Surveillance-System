import cv2

def draw_alert_overlay(frame, box, track_id, dwell_time, status="NORMAL"):

    x1, y1, x2, y2 = map(int, box)

    color = (0, 0, 255) if status == "ALERT" else (0, 255, 0)

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    label = f"ID:{track_id} | {dwell_time:.1f}s | {status}"

    cv2.putText(
        frame,
        label,
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2
    )