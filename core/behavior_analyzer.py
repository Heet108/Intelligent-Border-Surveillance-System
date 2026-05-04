class BehaviorAnalyzer:

    def analyze(self, track_id, track_data):
        zone_history = track_data["zone_history"]

        if len(zone_history) < 2:
            return None

        if zone_history[-2] == "OUTSIDE" and zone_history[-1] == "RESTRICTED":
            return "APPROACH_INTRUSION"

        return None






# class BehaviorAnalyzer:

#     def __init__(self):
#         self.approach_tracks = set()

#     def analyze(self, track_id, track_data):

#         zone_history = track_data["zone_history"]

#         if track_id in self.approach_tracks:
#             return None

#         if len(zone_history) < 3:
#             return None

#         if (
#             zone_history[-1] == "RESTRICTED"
#             and "WARNING" in zone_history
#             and "SAFE" in zone_history
#         ):
#             self.approach_tracks.add(track_id)
#             return "APPROACH_INTRUSION"

#         print(track_id, zone_history)

#         return None