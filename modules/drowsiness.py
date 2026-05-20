class DrowsinessDetector:
    """
    A beginner-friendly class to detect drowsiness by monitoring Eye Aspect Ratio (EAR)
    over consecutive frames. This prevents normal blinking from triggering false alarms.
    """
    def __init__(self, ear_threshold=0.25, frame_limit=20):
        # The threshold below which eyes are considered closed
        self.ear_threshold = ear_threshold
        
        # The number of consecutive frames eyes must be closed to trigger 'DROWSY'
        self.frame_limit = frame_limit
        
        # Counter for consecutive frames where EAR is below threshold
        self.frame_count = 0
        
        # Current state: False = Awake, True = Drowsy
        self.is_drowsy = False

    def check(self, avg_ear):
        """
        Takes the current EAR value, updates the frame counter, 
        and determines if the user is drowsy.
        Returns the drowsiness state and current frame count.
        """
        # If EAR is below the threshold, the eyes are closed
        if avg_ear < self.ear_threshold:
            self.frame_count += 1
            
            # If eyes have been closed for enough frames, set state to Drowsy
            if self.frame_count >= self.frame_limit:
                self.is_drowsy = True
        else:
            # If EAR is above the threshold, eyes are open
            # Reset frame count and state
            self.frame_count = 0
            self.is_drowsy = False
            
        return self.is_drowsy, self.frame_count
