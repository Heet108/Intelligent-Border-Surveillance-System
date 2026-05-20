import time
import cv2
import numpy as np
from config.setting import MAX_DWELL_SECONDS, MIN_MOVEMENT_PIXELS
from core.alert_manager import AlertSystem


class PolygonZone:
    def __init__(self, zone_points, zone_id="zone_1"):
        self.zone = np.array(zone_points, np.int32)
        self.zone_id = zone_id

        self.track_history = {}
        self.last_intrusion_time = {}
        self.entry_time = {}

        self.prev_centers = {}

        self.motion_distance = {}
        self.last_position = {}

        self.loitering_ids = set()
        self.dwell_alerted_ids = set()

        self.recent_exit_tracks = {}

        self.current_insider = 0
        self.intrusion_count = 0

        self.min_movement = MIN_MOVEMENT_PIXELS

        self.reentry_cooldown = 3
        self.intrusion_cooldown = 5

        self.LOITER_DWELL_THRESHOLD = 8
        self.LOITER_MOVEMENT_THRESHOLD = 15

        self.alert_system = AlertSystem()

    def is_inside(self, point):
        x, y = int(point[0]), int(point[1])
        return cv2.pointPolygonTest(self.zone, (x, y), False) >= 0

    def update(self, track_id, center):

        inside_now = self.is_inside(center)
        prev_center = self.prev_centers.get(track_id)

        if prev_center is not None:
            dx = center[0] - prev_center[0]
            dy = center[1] - prev_center[1]

            if (dx * dx + dy * dy) < self.min_movement ** 2:
                center = prev_center

        self.prev_centers[track_id] = center

        if track_id not in self.track_history:
            self.track_history[track_id] = inside_now

            if inside_now:
                self._on_entry(track_id)

            return

        was_inside = self.track_history[track_id]

        if not was_inside and inside_now:
            self._on_entry(track_id)

        elif was_inside and not inside_now:
            self._on_exit(track_id)

        if inside_now:
            self._handle_inside(track_id, center)

        self.track_history[track_id] = inside_now

    def _on_entry(self, track_id):
        now = time.time()

        if track_id in self.recent_exit_tracks:
            if now - self.recent_exit_tracks[track_id] < self.reentry_cooldown:
                return

        self.current_insider += 1
        self.entry_time[track_id] = now

        last_time = self.last_intrusion_time.get(track_id, 0)

        if now - last_time >= self.intrusion_cooldown:
            self.intrusion_count += 1
            self.last_intrusion_time[track_id] = now

            self.alert_system.send_intrusion_alert(track_id, self.zone_id)

    def _on_exit(self, track_id):
        self.current_insider = max(0, self.current_insider - 1)

        self.recent_exit_tracks[track_id] = time.time()

        if track_id in self.entry_time:
            dwell = time.time() - self.entry_time[track_id]
            print(f"Track {track_id} stayed {dwell:.2f}s")
            del self.entry_time[track_id]

        self.motion_distance.pop(track_id, None)
        self.last_position.pop(track_id, None)
        self.loitering_ids.discard(track_id)
        self.dwell_alerted_ids.discard(track_id)

    def _handle_inside(self, track_id, center):

        if track_id not in self.motion_distance:
            self.motion_distance[track_id] = 0
            self.last_position[track_id] = center
        else:
            prev = self.last_position[track_id]

            dx = center[0] - prev[0]
            dy = center[1] - prev[1]

            dist = (dx * dx + dy * dy) ** 0.5

            self.motion_distance[track_id] += dist
            self.last_position[track_id] = center

        dwell = self.get_dwell_time(track_id)

        movement = self.motion_distance.get(track_id, 0)
        avg_motion = movement / dwell if dwell > 0 else 0

        # LOITERING ALERT
        if (
            dwell > self.LOITER_DWELL_THRESHOLD and
            avg_motion < self.LOITER_MOVEMENT_THRESHOLD and
            track_id not in self.loitering_ids
        ):
            self.loitering_ids.add(track_id)
            self.alert_system.send_loitering_alert(track_id, dwell, self.zone_id)

        # DWELL ALERT
        if dwell > MAX_DWELL_SECONDS and track_id not in self.dwell_alerted_ids:
            self.dwell_alerted_ids.add(track_id)
            self.alert_system.send_dwell_alert(track_id, dwell, self.zone_id)

    def cleanup_lost_tracks(self, current_ids):
        for track_id in list(self.track_history.keys()):
            if track_id not in current_ids:
                if self.track_history[track_id]:
                    self.current_insider = max(0, self.current_insider - 1)

                self.track_history.pop(track_id, None)
                self.last_intrusion_time.pop(track_id, None)
                self.entry_time.pop(track_id, None)
                self.prev_centers.pop(track_id, None)
                self.motion_distance.pop(track_id, None)
                self.last_position.pop(track_id, None)
                self.recent_exit_tracks.pop(track_id, None)

                self.loitering_ids.discard(track_id)
                self.dwell_alerted_ids.discard(track_id)

    def get_dwell_time(self, track_id):
        if track_id in self.entry_time:
            return time.time() - self.entry_time[track_id]
        return 0

    def get_status(self, track_id):
        if not self.track_history.get(track_id, False):
            return "OUTSIDE"

        dwell = self.get_dwell_time(track_id)
        movement = self.motion_distance.get(track_id, 0)

        avg_motion = movement / dwell if dwell > 0 else 0

        if (
            dwell > self.LOITER_DWELL_THRESHOLD and
            avg_motion < self.LOITER_MOVEMENT_THRESHOLD
        ):
            return "LOITERING"

        if dwell > MAX_DWELL_SECONDS:
            return "DWELL"

        return "NORMAL"
    
    





# line-based logic.

# class LineZone:
#     def __init__(self):
#         self.track_history = {}
#         self.last_intrusion_time = {}

#         self.entry_count = 0
#         self.exit_count = 0
#         self.current_insider = 0
#         self.intrusion_count = 0
    
#     def update(self, track_id, center_y):
#         if track_id in self.track_history:
#             prev_y = self.track_history[track_id]

#             # Entry
#             if prev_y < LINE_Y and center_y >= LINE_Y:
#                 self.entry_count += 1
#                 self.current_insider += 1
#                 self._handle_intrusion(track_id)

#             # Exit
#             elif prev_y >= LINE_Y and center_y < LINE_Y:
#                 self.exit_count += 1
#                 self.current_insider = max(0, self.current_insider - 1)

#         self.track_history[track_id] = center_y
    
#     def _handle_intrusion(self, track_id):
#         now = time.time()

#         if (track_id not in self.last_intrusion_time or
#             now - self.last_intrusion_time[track_id] > COOLDOWN_SECONDS):

#             self.intrusion_count += 1
#             self.last_intrusion_time[track_id] = now