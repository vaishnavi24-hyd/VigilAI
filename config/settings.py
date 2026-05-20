import os

# Base Application Directory Settings
# All application data, databases, reports, and logs will be written here
APP_DIR_NAME = "SleepGuardAI"
BASE_REPORTS_DIR = os.path.join(os.path.expanduser("~"), "Documents", APP_DIR_NAME)
SESSIONS_DIR = os.path.join(BASE_REPORTS_DIR, "Sessions")
DB_PATH = os.path.join(BASE_REPORTS_DIR, "sleepguard.db")

# AI Detection Parameters - Eye Aspect Ratio (EAR)
EAR_THRESHOLD = 0.25
EAR_FRAME_LIMIT = 20

# AI Detection Parameters - Mouth Aspect Ratio (MAR)
MAR_THRESHOLD = 0.6
MAR_FRAME_LIMIT = 15

# AI Detection Parameters - Head Tilt Pose Angles
PITCH_THRESHOLD = -15.0
ROLL_THRESHOLD = 15.0
TILT_FRAME_LIMIT = 25

# Fatigue Engine Configuration - Weights & Thresholds
WEIGHT_EYES = 0.5
WEIGHT_TILT = 0.3
WEIGHT_YAWN = 0.2
ALARM_THRESHOLD = 40.0

# Alert Management Parameters - Timers (Seconds)
MEDIUM_ALARM_DURATION = 1.5
COOLDOWN_DURATION = 5.0
