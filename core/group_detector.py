class GroupDetector:

    # threshold=3 means this many persons should be inside the restricted zone.
    def __init__(self, threshold=3):      
        self.threshold = threshold
        self.group_active = False

    def detect(self, count_inside):

        # group forms
        if count_inside >= self.threshold and not self.group_active:
            self.group_active = True
            return True

        # group disperses
        if count_inside < self.threshold:
            self.group_active = False

        return False