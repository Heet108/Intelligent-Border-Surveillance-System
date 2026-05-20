class BehaviorAnalyzer:

    def analyze(self, track_id, track_data):
        zone_history = track_data["zone_history"]

        if len(zone_history) < 2:
            return None

        if zone_history[-2] == "OUTSIDE" and zone_history[-1] == "RESTRICTED":
            return "APPROACH_INTRUSION"

        return None