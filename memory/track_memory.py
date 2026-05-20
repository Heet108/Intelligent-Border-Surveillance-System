import time

class TrackMemory:

    def __init__(self):
        self.tracks = {}
        self.MAX_HISTORY = 30

    def update(self, track_id, center, zone):
        now = time.time()

        if track_id not in self.tracks:
            self.tracks[track_id] = {
                "first_seen": now,
                "last_seen": now,
                "positions": [center],
                "zone_history": [zone],
                "distance": 0
            }
            return
        
        track = self.tracks[track_id]

        prev = track["positions"][-1]

        dx = center[0] - prev[0]
        dy = center[1] - prev[1]

        dist = (dx * dx + dy * dy) ** 0.5

        track["distance"] += dist
        track["positions"].append(center)
        track["last_seen"] = now

        # Append zone only if changed
        if track["zone_history"][-1] != zone:
            track["zone_history"].append(zone)

        # Keep only recent history
        if len(track["positions"]) > self.MAX_HISTORY:
            track["positions"] = track["positions"][-self.MAX_HISTORY:]

        if len(track["zone_history"]) > self.MAX_HISTORY:
            track["zone_history"] = track["zone_history"][-self.MAX_HISTORY:]

    def get_track(self, track_id):
        return self.tracks.get(track_id)
    
    def cleanup_lost_tracks(self, current_ids):
        for track_id in list(self.tracks.keys()):
            if track_id not in current_ids:
                del self.tracks[track_id]