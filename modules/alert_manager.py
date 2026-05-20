import time
from modules.alarm import AlarmManager

class AlertManager:
    """
    Intelligent Alert Management System.
    Handles the alert lifecycle, prevents alarm spam via cooldowns, and
    escalates alerts according to fatigue severity.
    
    Escalation Logic:
    - LOW Fatigue (Score < 20%): No sound, purely visual on-screen telemetry.
    - MEDIUM Fatigue (20% <= Score < 40%): Sounds alarm for a short period
      (e.g., 1.5 seconds) then enters a cooldown (e.g., 5 seconds) to prevent spam.
    - HIGH Fatigue (Score >= 40%): Sounds alarm continuously, overriding cooldowns,
      until fatigue levels return to low.
    """
    def __init__(self, medium_alarm_duration=1.5, cooldown_duration=5.0):
        # Instantiate base AlarmManager for pygame audio playback
        self.alarm_helper = AlarmManager()
        
        # Duration configurations (in seconds)
        self.medium_alarm_duration = medium_alarm_duration
        self.cooldown_duration = cooldown_duration
        
        # Alert state tracking
        self.alert_state = "INACTIVE"  # Can be: "INACTIVE", "ACTIVE", "COOLDOWN"
        self.alert_level = "NONE"      # Can be: "NONE", "LOW", "MEDIUM", "HIGH"
        
        # Timestamp variables
        self.alert_start_time = 0.0
        self.cooldown_start_time = 0.0
        self.last_alert_time = 0.0

    def update_alerts(self, fatigue_score, fatigue_level):
        """
        Processes fatigue telemetry through the state machine and updates
        sound status accordingly.
        
        Parameters:
        - fatigue_score: float (0.0 to 100.0)
        - fatigue_level: str ("LOW FATIGUE", "MEDIUM FATIGUE", "HIGH FATIGUE")
        
        Returns: (alert_state, alert_level)
        """
        current_time = time.time()
        
        # 1. Map fatigue level input to internal alert levels
        if fatigue_level == "LOW FATIGUE":
            self.alert_level = "LOW"
        elif fatigue_level == "MEDIUM FATIGUE":
            self.alert_level = "MEDIUM"
        else:
            self.alert_level = "HIGH"

        # 2. State Machine Transitions (Alert Lifecycle Management)
        if self.alert_state == "COOLDOWN":
            # Escalation: High fatigue overrides active cooldowns immediately
            if self.alert_level == "HIGH":
                self.alert_state = "ACTIVE"
                self.alert_start_time = current_time
                self.alarm_helper.play()
            else:
                # Anti-spam: check if cooldown has completed
                elapsed = current_time - self.cooldown_start_time
                if elapsed >= self.cooldown_duration:
                    self.alert_state = "INACTIVE"
                else:
                    # Maintain silenced state during cooldown period
                    self.alarm_helper.stop()

        elif self.alert_state == "ACTIVE":
            if self.alert_level == "LOW":
                self.alert_state = "INACTIVE"
                self.alarm_helper.stop()
                
            elif self.alert_level == "MEDIUM":
                # Check play duration limit for medium alerts (anti-spam)
                play_elapsed = current_time - self.alert_start_time
                if play_elapsed >= self.medium_alarm_duration:
                    self.alert_state = "COOLDOWN"
                    self.cooldown_start_time = current_time
                    self.alarm_helper.stop()
                else:
                    # Keep playing alarm until duration is met
                    self.alarm_helper.play()
                    
            elif self.alert_level == "HIGH":
                # Continuous alarm for high fatigue states
                self.alarm_helper.play()

        elif self.alert_state == "INACTIVE":
            if self.alert_level == "HIGH":
                self.alert_state = "ACTIVE"
                self.alert_start_time = current_time
                self.alarm_helper.play()
                
            elif self.alert_level == "MEDIUM":
                self.alert_state = "ACTIVE"
                self.alert_start_time = current_time
                self.alarm_helper.play()
                
            else:
                # Keep silenced for low fatigue
                self.alarm_helper.stop()

        # Update last alert timestamp if the audio is actively playing
        if self.alarm_helper.is_playing:
            self.last_alert_time = current_time

        return self.alert_state, self.alert_level

    def get_status_text(self):
        """
        Generates status telemetry text for the screen overlays.
        """
        if self.alert_state == "COOLDOWN":
            current_time = time.time()
            remaining = max(0.0, self.cooldown_duration - (current_time - self.cooldown_start_time))
            return f"ALERT COOLDOWN ({remaining:.1f}s)"
        elif self.alert_state == "ACTIVE":
            return f"ALERT ACTIVE ({self.alert_level})"
        else:
            return "ALERT INACTIVE"

    def is_playing(self):
        """
        Exposes alarm playing state.
        """
        return self.alarm_helper.is_playing

    def stop(self):
        """
        Forced stop to reset alerts.
        """
        self.alert_state = "INACTIVE"
        self.alarm_helper.stop()

    def cleanup(self):
        """
        Releases Pygame mixer resources.
        """
        self.alarm_helper.cleanup()
