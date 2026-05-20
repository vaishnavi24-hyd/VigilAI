import os
import pygame
import numpy as np
from scipy.io import wavfile

class AlarmManager:
    """
    A beginner-friendly class to manage playing and stopping the alarm sound.
    Uses pygame to play sound asynchronously without blocking the webcam feed.
    """
    def __init__(self, alarm_file="assets/alarm.wav"):
        self.alarm_file = alarm_file
        # State management variable to prevent multiple overlapping alarms
        self.is_playing = False
        
        # Initialize the pygame mixer for audio playback
        pygame.mixer.init()
        
        # Ensure the assets folder and alarm file exist
        self._ensure_alarm_file()
        
        # Load the sound file into memory
        self.sound = pygame.mixer.Sound(self.alarm_file)
        
    def _ensure_alarm_file(self):
        """
        Helper method to check if the alarm file exists. 
        If it doesn't, it automatically generates a simple beep sound and saves it.
        """
        # Ensure the assets directory exists
        os.makedirs(os.path.dirname(self.alarm_file), exist_ok=True)
        
        # If the file does not exist, create a basic beep sound
        if not os.path.exists(self.alarm_file):
            print(f"Alarm file not found at {self.alarm_file}. Generating a basic beep...")
            
            # Generate a 1-second sine wave at 1000 Hz (standard beep pitch)
            sample_rate = 44100
            t = np.linspace(0, 1, sample_rate, False)
            audio = np.sin(2 * np.pi * 1000 * t)
            
            # Convert to 16-bit PCM format (required for standard WAV files)
            audio_16bit = np.int16(audio * 32767)
            
            # Save it to the specified path
            wavfile.write(self.alarm_file, sample_rate, audio_16bit)
            
    def play(self):
        """
        Plays the alarm sound on a continuous loop if it is not already playing.
        """
        if not self.is_playing:
            # -1 means loop indefinitely
            self.sound.play(-1)
            self.is_playing = True
            
    def stop(self):
        """
        Stops the alarm sound if it is currently playing.
        """
        if self.is_playing:
            self.sound.stop()
            self.is_playing = False
            
    def get_status_text(self):
        """
        Returns the current text status to display on the screen.
        """
        if self.is_playing:
            return "ALARM ACTIVE"
        else:
            return "ALARM STOPPED"
            
    def cleanup(self):
        """
        Gracefully shuts down the alarm manager.
        This stops any active playback and cleanly quits the pygame mixer 
        to ensure no audio threads are left hanging in the background.
        """
        self.stop()
        try:
            pygame.mixer.quit()
        except:
            pass
