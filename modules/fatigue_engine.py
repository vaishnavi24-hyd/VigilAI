class FatigueEngine:
    """
    Advanced Fatigue Confidence Scoring Engine.
    Combines multiple fatigue markers (eye closure, yawning, head tilt) using
    weighted math to produce a single fatigue score between 0% and 100%.
    
    This reduces false alarms from single temporary indicators (like looking down
    at the dashboard or speaking/laughing) while maintaining high safety for
    genuine fatigue conditions.
    """
    def __init__(self, w_eye=0.5, w_tilt=0.3, w_yawn=0.2, alarm_threshold=40.0):
        # Configurable weights (should sum up to 1.0)
        self.w_eye = w_eye
        self.w_tilt = w_tilt
        self.w_yawn = w_yawn
        
        # Total fatigue score threshold to activate alarm
        self.alarm_threshold = alarm_threshold

    def compute_fatigue(self, closed_frames, eye_limit, yawn_frames, yawn_limit, tilt_frames, tilt_limit):
        """
        Calculates individual scores, weights them, and classifies overall fatigue level.
        
        Parameters:
        - closed_frames: current consecutive frames of closed eyes.
        - eye_limit: total frame limit for eyes closed alert.
        - yawn_frames: current consecutive frames of mouth open.
        - yawn_limit: total frame limit for yawn alert.
        - tilt_frames: current consecutive frames of head tilt.
        - tilt_limit: total frame limit for head tilt alert.
        
        Returns: (fatigue_score, level_text, BGR_color_tuple)
        """
        # Calculate raw percentage contributions (0 to 100) from each tracking module
        eye_score = min(100.0, (closed_frames / eye_limit) * 100.0) if eye_limit > 0 else 0.0
        yawn_score = min(100.0, (yawn_frames / yawn_limit) * 100.0) if yawn_limit > 0 else 0.0
        tilt_score = min(100.0, (tilt_frames / tilt_limit) * 100.0) if tilt_limit > 0 else 0.0

        # Calculate final weighted score (0 to 100%)
        fatigue_score = (eye_score * self.w_eye) + (tilt_score * self.w_tilt) + (yawn_score * self.w_yawn)

        # Categorize confidence levels and assign BGR color codes
        if fatigue_score < 20.0:
            level = "LOW FATIGUE"
            color = (0, 255, 0)      # Green (BGR)
        elif fatigue_score < self.alarm_threshold:
            level = "MEDIUM FATIGUE"
            color = (0, 165, 255)    # Orange (BGR)
        else:
            level = "HIGH FATIGUE"
            color = (0, 0, 255)      # Red (BGR)

        return fatigue_score, level, color
