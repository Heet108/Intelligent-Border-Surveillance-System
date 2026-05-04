import time

class FPS:
    def __init__(self):
        self.prev_time = 0

    def update(self):
        current = time.time()
        fps = 1 / (current - self.prev_time) if self.prev_time else 0
        self.prev_time = current
        return int(fps)
