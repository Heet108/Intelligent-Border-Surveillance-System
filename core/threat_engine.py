import time


class ThreatEngine:

    def __init__(self):
        self.scores = {}            # track_id -> smoothed score
        self.last_alert_time = {}   # track_id -> timestamp
        self.cooldown = 10          # seconds

    def evaluate(self, track_id, zone_type, dwell, status, event):
        # Get previous score (default = 0)
        previous_score = self.scores.get(track_id, 0)

        # Compute current frame score
        current_score = 0

        # Base intrusion score
        if zone_type == "RESTRICTED":
            current_score += 3

        # Suspicious stay
        if dwell > 3:
            current_score += 2

        # Serious loitering
        if status == "LOITERING":
            current_score += 3

        # Border-approach movement
        if event == "APPROACH_INTRUSION":
            current_score += 2

        # Temporal smoothing (decay + accumulation)
        score = previous_score * 0.8 + current_score

        # Store updated score
        self.scores[track_id] = score

        return score

    def get_level(self, score):
        if score >= 7:
            return "HIGH"
        elif score >= 5:
            return "MEDIUM"
        elif score >= 3:
            return "LOW"
        return "NONE"

    def can_alert(self, track_id):
        now = time.time()

        last_time = self.last_alert_time.get(track_id, 0)

        if now - last_time > self.cooldown:
            self.last_alert_time[track_id] = now
            return True

        return False