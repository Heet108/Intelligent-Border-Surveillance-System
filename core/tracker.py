import math
import time
from scipy.optimize import linear_sum_assignment
import numpy as np

class Tracker:
    def __init__(self):
        self.next_id = 0
        self.objects = {}        
        self.last_seen = {}      

        self.max_lost_time = 3.0
        self.distance_thresh = 120

        # safety thresholds
        self.max_distance_limit = 300   # reject impossible matches
        self.min_iou_match = 0.1        # avoid weak overlaps

    def _distance(self, boxA, boxB):
        cxA = (boxA[0] + boxA[2]) // 2
        cyA = (boxA[1] + boxA[3]) // 2

        cxB = (boxB[0] + boxB[2]) // 2
        cyB = (boxB[1] + boxB[3]) // 2

        return math.hypot(cxA - cxB, cyA - cyB)

    def _iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)

        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        union = boxAArea + boxBArea - interArea

        if union == 0:
            return 0

        return interArea / union

    def update(self, boxes):
        now = time.time()

        new_objects = {}
        used_ids = set()
        used_boxes = set()

        if len(self.objects) == 0:
            for box in boxes:
                new_objects[self.next_id] = box
                self.last_seen[self.next_id] = now
                self.next_id += 1

        else:
            object_ids = list(self.objects.keys())
            object_boxes = list(self.objects.values())

            if len(boxes) > 0 and len(object_boxes) > 0:

                cost_matrix = np.zeros((len(object_boxes), len(boxes)), dtype=np.float32)

                for i, obj_box in enumerate(object_boxes):
                    for j, box in enumerate(boxes):
                        dist = self._distance(obj_box, box)
                        iou = self._iou(obj_box, box)

                        # HYBRID COST
                        cost_matrix[i][j] = dist - (iou * 100)

                row_ind, col_ind = linear_sum_assignment(cost_matrix)

                for r, c in zip(row_ind, col_ind):
                    dist = self._distance(object_boxes[r], boxes[c])
                    iou = self._iou(object_boxes[r], boxes[c])

                    # HARD GATING
                    if dist > self.max_distance_limit:
                        continue

                    # reject very weak matches
                    if iou < self.min_iou_match and dist > self.distance_thresh:
                        continue

                    # Existing condition (unchanged)
                    if dist < self.distance_thresh or iou > 0.3:
                        obj_id = object_ids[r]

                        new_objects[obj_id] = boxes[c]
                        self.last_seen[obj_id] = now

                        used_ids.add(obj_id)
                        used_boxes.add(c)

            for obj_id in self.objects:
                if obj_id not in used_ids:
                    if now - self.last_seen.get(obj_id, 0) <= self.max_lost_time:
                        new_objects[obj_id] = self.objects[obj_id]
                    else:
                        self.last_seen.pop(obj_id, None)

            for i, box in enumerate(boxes):
                if i not in used_boxes:
                    new_objects[self.next_id] = box
                    self.last_seen[self.next_id] = now
                    self.next_id += 1

        self.objects = new_objects

        return [(box, obj_id) for obj_id, box in self.objects.items()]