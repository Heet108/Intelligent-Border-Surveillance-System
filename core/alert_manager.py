import json
from datetime import datetime
import time


class AlertSystem:
    def __init__(self, file_path="alerts.json"):
        self.file_path = file_path
        self.last_alert_time = {}  # (type, track_id) → timestamp

        # different cooldowns per alert type
        self.cooldowns = {
            "intrusion": 2,
            "loitering": 5,
            "dwell": 5
        }

    def _should_write(self, alert_type, track_id):
        key = (alert_type, track_id)
        now = time.time()

        cooldown = self.cooldowns.get(alert_type, 2)

        if key in self.last_alert_time:
            if now - self.last_alert_time[key] < cooldown:
                return False

        self.last_alert_time[key] = now
        return True

    def _write_alert(self, data):
        if not self._should_write(data["type"], data["track_id"]):
            return  # 🚫 skip duplicate

        with open(self.file_path, "a") as f:
            json.dump(data, f)
            f.write("\n")

    def send_intrusion_alert(self, track_id, zone_id):
        alert = {
            "type": "intrusion",
            "track_id": int(track_id),
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high",
            "zone_id": zone_id
        }
        self._write_alert(alert)

    def send_loitering_alert(self, track_id, dwell, zone_id):
        alert = {
            "type": "loitering",
            "track_id": int(track_id),
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high",
            "zone_id": zone_id,
            "dwell_time": round(dwell, 2)
        }
        self._write_alert(alert)

    def send_dwell_alert(self, track_id, dwell, zone_id):
        alert = {
            "type": "dwell",
            "track_id": int(track_id),
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "medium",
            "zone_id": zone_id,
            "dwell_time": round(dwell, 2)
        }
        self._write_alert(alert)