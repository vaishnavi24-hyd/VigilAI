import logging
import os
import sys
from config.settings import BASE_REPORTS_DIR

def setup_logger():
    """
    Sets up a standard Python logging configuration.
    Logs to both console and a log file in the base reports directory.
    """
    os.makedirs(BASE_REPORTS_DIR, exist_ok=True)
    log_file = os.path.join(BASE_REPORTS_DIR, "sleepguard.log")
    
    logger = logging.getLogger("SleepGuardAI")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # If writing to ~/Documents/ fails, log to stdout only and print error
            print(f"WARNING: Could not create log file at {log_file} due to: {e}. Console logging only.")
            
    return logger

# Global logger instance
logger = setup_logger()
