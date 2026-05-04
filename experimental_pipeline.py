from core.detector import PersonDetector
from core.zone_logic import PolygonZone
# from core.tracker import Tracker   # ❌ REMOVED
from utils.drawing import draw_polygon, draw_clean_label
from utils.fps import FPS
from utils.overlay import draw_alert_overlay
from config.setting import CAMERA_SOURCE, MAX_DWELL_SECONDS
from core.alert import AlertSystem
from memory.track_memory import TrackMemory
from core.behavior_analyzer import BehaviorAnalyzer
from core.threat_engine import ThreatEngine
from logs.event_logger import EventLogger
from core.group_detector import GroupDetector
from utils.manual_zone import get_or_create_zone
from firebase_upload import upload_image, save_detection
from flask import Flask, Response
import threading
import time
from firebase_upload import save_alert

import cv2
import datetime
import os
import queue

# --- Shared encoded frame for streaming ---
encoded_frame = None
frame_lock = threading.Lock()

# --- Camera frame queue: maxsize=1 keeps it fresh, never stale ---
frame_queue = queue.Queue(maxsize=1)

# --- Firebase alert throttle ---
last_alert_time = {}

def can_send(track_id, gap=3):
    now = time.time()
    if track_id not in last_alert_time or now - last_alert_time[track_id] > gap:
        last_alert_time[track_id] = now
        return True
    return False


def save_and_upload(frame, filename, track_id, score):
    try:
        cv2.imwrite(filename, frame)

        import os, time
        for _ in range(10):
            if os.path.exists(filename):
                break
            time.sleep(0.05)

        url = upload_image(filename)
        save_detection(url, track_id, score)

        print("Uploaded:", url)

    except Exception as e:
        print("Firebase Error:", e)


if not os.path.exists("alerts"):
    os.makedirs("alerts")

detector = PersonDetector()
# tracker = Tracker()   # ❌ REMOVED
fps_counter = FPS()
alert_system = AlertSystem()

memory = TrackMemory()
behavior = BehaviorAnalyzer()
threat_engine = ThreatEngine()

logger = EventLogger()
group_detector = GroupDetector()

cap = cv2.VideoCapture(CAMERA_SOURCE)

cap.set(3, 640)
cap.set(4, 480)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

ret, frame = cap.read()
if not ret:
    exit()

h, w = frame.shape[:2]

app = Flask(__name__)


# --- Thread 1: Camera reader runs independently at full speed ---
def camera_reader():
    while True:
        ret, frm = cap.read()
        if not ret:
            break
        if frame_queue.full():
            try:
                frame_queue.get_nowait()
            except queue.Empty:
                pass
        frame_queue.put(frm)

threading.Thread(target=camera_reader, daemon=True).start()


# --- Thread 3: Flask MJPEG streamer ---
def generate():
    global encoded_frame
    while True:
        with frame_lock:
            if encoded_frame is None:
                time.sleep(0.01)
                continue
            data = encoded_frame

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

        time.sleep(0.03)


@app.route('/video')
def video():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def run_stream():
    app.run(host='0.0.0.0', port=5000, debug=False)


# -------- Zone Selection --------
restricted_points = get_or_create_zone(frame)

if restricted_points is None:
    print("Zone selection cancelled.")
    cap.release()
    cv2.destroyAllWindows()
    exit()

print("Restricted Zone Selected:", restricted_points)

restricted_zone = PolygonZone(restricted_points)

threading.Thread(target=run_stream, daemon=True).start()


# --- Thread 2: Main detection + logic loop ---
while True:
    try:
        frame = frame_queue.get(timeout=1.0)
    except queue.Empty:
        continue

    raw_boxes = detector.detect(frame)

    # -------- TRACKING (ByteTrack IDs) --------
    tracked_objects = []

    for box in raw_boxes:
        if box.id is None:
            continue

        track_id = int(box.id.item())
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        tracked_objects.append(((x1, y1, x2, y2), track_id))

    current_ids = set()

    for box, track_id in tracked_objects:
        track_id = int(track_id)
        current_ids.add(track_id)

        x1, y1, x2, y2 = map(int, box)

        foot_x = (x1 + x2) // 2
        foot_y = y2
        foot_point = (foot_x, foot_y)

        inside_now = restricted_zone.is_inside(foot_point)
        restricted_zone.update(track_id, foot_point)

        zone_type = "RESTRICTED" if inside_now else "OUTSIDE"

        memory.update(track_id, foot_point, zone_type)
        track_data = memory.get_track(track_id)

        event = behavior.analyze(track_id, track_data)

        dwell = restricted_zone.get_dwell_time(track_id)
        status = restricted_zone.get_status(track_id)

        if status == "DWELL" and can_send(track_id):
            save_alert("dwell", track_id, restricted_zone.zone_id, dwell)

        if status == "LOITERING" and can_send(track_id):
            save_alert("loitering", track_id, restricted_zone.zone_id, dwell)

        score = threat_engine.evaluate(
            track_id,
            zone_type,
            dwell,
            status,
            event
        )
        threat_level = threat_engine.get_level(score)

        if inside_now and score >= 5 and threat_engine.can_alert(track_id):

            timestamps = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alerts/track_{track_id}_{timestamps}.jpg"

            threading.Thread(
                target=save_and_upload,
                args=(frame.copy(), filename, track_id, score),
                daemon=True
            ).start()

            alert_system.send_intrusion_alert(track_id, restricted_zone.zone_id)
            save_alert("intrusion", track_id, restricted_zone.zone_id)

            logger.log(track_id, "THREAT_ALERT", score)

        if event == "APPROACH_INTRUSION":
            draw_clean_label(frame, "APPROACHING BORDER", x1, y1 - 40, (0, 0, 255))

        if status == "LOITERING":
            color = (0, 0, 255)
        elif status == "DWELL":
            color = (0, 165, 255)
        elif status == "NORMAL":
            color = (0, 255, 0)
        else:
            color = (255, 255, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.circle(frame, foot_point, 6, (255, 255, 255), -1)
        cv2.circle(frame, foot_point, 4, color, -1)

        if inside_now:
            label = f"ID {track_id} | RESTRICTED | {status} | {threat_level} | S:{score}"
        else:
            label = f"ID {track_id} | OUTSIDE | {threat_level} | S:{score}"

        draw_clean_label(frame, label, x1, y1 - 10, color)

    if group_detector.detect(restricted_zone.current_insider):
        cv2.putText(frame, "GROUP INTRUSION DETECTED",
                    (w//2 - 200, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        logger.log(-1, "GROUP_INTRUSION", restricted_zone.current_insider)

    memory.cleanup_lost_tracks(current_ids)
    restricted_zone.cleanup_lost_tracks(current_ids)

    draw_polygon(frame, restricted_points, (0, 0, 255), "RESTRICTED ZONE")

    fps = fps_counter.update()

    cv2.putText(frame, f"FPS: {int(fps)}",
                (20, 40), cv2.FONT_HERSHEY_COMPLEX,
                0.7, (0, 255, 0), 2)

    cv2.putText(frame, f"Inside: {restricted_zone.current_insider}",
                (20, 100), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 0, 255), 2)

    cv2.putText(frame, f"Intrusions: {restricted_zone.intrusion_count}",
                (20, 140), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 255, 255), 2)

    cv2.imshow("Surveillance System", frame)

    small = cv2.resize(frame, (480, 270))
    _, buffer = cv2.imencode('.jpg', small, [int(cv2.IMWRITE_JPEG_QUALITY), 60])

    with frame_lock:
        encoded_frame = buffer.tobytes()

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()