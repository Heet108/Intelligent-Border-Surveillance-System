from ultralytics import YOLO
from config.setting import MODEL_PATH, CONF_THRESHOLD

class PersonDetector:
    def __init__(self):
        self.model = YOLO(MODEL_PATH)

    def detect(self, frame):
        results = self.model.track(
            frame,
            persist=True,
            tracker='bytetrack.yaml',
            conf=CONF_THRESHOLD,
            classes=[0]
        )
        return results[0].boxes