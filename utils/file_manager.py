import os
from datetime import datetime
from config.settings import BASE_REPORTS_DIR, SESSIONS_DIR
from utils.logger import logger

class FileManager:
    """
    Handles timestamped session folder creations and path resolutions
    for reports, charts, and summaries.
    """
    def __init__(self):
        self.base_dir = BASE_REPORTS_DIR
        self.sessions_dir = SESSIONS_DIR
        
        # Ensure base directories exist
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            os.makedirs(self.sessions_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Could not create base directories at {self.base_dir}: {e}")
            
        # Session folder details
        self.session_dir = None
        
    def create_session_folder(self):
        """
        Creates a unique timestamped folder for the current monitoring session.
        Example: ~/Documents/SleepGuardAI/Sessions/Session_2026_05_20_10_30/
        """
        timestamp = datetime.now().strftime("Session_%Y_%m_%d_%H_%M")
        self.session_dir = os.path.join(self.sessions_dir, timestamp)
        
        # Avoid collisions if starting twice within the same minute
        if os.path.exists(self.session_dir):
            timestamp_sec = datetime.now().strftime("Session_%Y_%m_%d_%H_%M_%S")
            self.session_dir = os.path.join(self.sessions_dir, timestamp_sec)
            
        try:
            logger.info("Creating session folder...")
            os.makedirs(self.session_dir, exist_ok=True)
            logger.info(f"Created session folder successfully at {self.session_dir}")
            return self.session_dir
        except Exception as e:
            # Fallback to local reports directory in workspace in case of permissions error
            fallback_dir = os.path.join("reports", timestamp)
            logger.warning(f"Could not create session folder at {self.session_dir} due to: {e}. Falling back to workspace reports folder: {fallback_dir}")
            self.session_dir = fallback_dir
            os.makedirs(self.session_dir, exist_ok=True)
            return self.session_dir

    def get_report_path(self, filename):
        """
        Resolves the absolute path for a report file inside the current session folder.
        """
        if not self.session_dir:
            self.create_session_folder()
        return os.path.join(self.session_dir, filename)

    def open_session_folder(self):
        """
        Opens the generated session folder automatically in Finder (macOS),
        File Explorer (Windows), or default file manager (Linux).
        """
        if not self.session_dir or not os.path.exists(self.session_dir):
            logger.warning("No session folder exists to open.")
            return
            
        logger.info("Opening reports directory...")
        try:
            import platform
            import subprocess
            
            system_name = platform.system()
            if system_name == "Darwin":  # macOS
                subprocess.run(["open", self.session_dir], check=True)
            elif system_name == "Windows":
                os.startfile(self.session_dir)
            else:  # Linux / Unix
                subprocess.run(["xdg-open", self.session_dir], check=True)
            logger.info("Opened reports directory successfully.")
        except Exception as e:
            logger.error(f"Failed to open reports directory: {e}")

    def get_base_dir(self):
        return self.base_dir
