import csv
import os
import datetime


class EventLogger:

    def __init__(self, log_file="logs/events.csv"):

        self.log_file = log_file

        os.makedirs("logs", exist_ok=True)

        # create file if not exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "track_id", "event", "score"])

    def log(self, track_id, event, score):

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, track_id, event, score])