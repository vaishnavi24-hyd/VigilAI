import sqlite3
import os
from config.settings import DB_PATH
from utils.logger import logger

def initialize_database():
    """
    Initializes the SQLite database and creates the sessions table if it doesn't exist.
    """
    try:
        # Ensure parent directory of database exists
        db_dir = os.path.dirname(DB_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create the sessions table (including yawn_events, tilt_events, avg_fatigue, peak_fatigue columns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT NOT NULL,
                duration REAL NOT NULL,
                drowsiness_events INTEGER NOT NULL,
                yawn_events INTEGER NOT NULL DEFAULT 0,
                tilt_events INTEGER NOT NULL DEFAULT 0,
                avg_ear REAL NOT NULL,
                avg_fatigue REAL NOT NULL DEFAULT 0.0,
                peak_fatigue REAL NOT NULL DEFAULT 0.0
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized successfully at {DB_PATH}.")
    except Exception as e:
        logger.error(f"Database initialization failure at {DB_PATH}: {e}")

def save_session(session_date, duration, drowsiness_events, yawn_events, tilt_events, avg_ear, avg_fatigue, peak_fatigue):
    """
    Saves a completed monitoring session to the SQLite database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (session_date, duration, drowsiness_events, yawn_events, tilt_events, avg_ear, avg_fatigue, peak_fatigue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_date, duration, drowsiness_events, yawn_events, tilt_events, avg_ear, avg_fatigue, peak_fatigue))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved session data to SQLite: Date={session_date}, Duration={duration:.1f}s, Avg Fatigue={avg_fatigue:.1f}%, Peak Fatigue={peak_fatigue:.1f}%")
    except Exception as e:
        logger.error(f"Failed to save session data to SQLite database: {e}")

def get_all_sessions():
    """
    Retrieves all session data from the database.
    Returns a list of tuples.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT session_date, duration, drowsiness_events, yawn_events, tilt_events, avg_ear, avg_fatigue, peak_fatigue FROM sessions ORDER BY id ASC")
        rows = cursor.fetchall()
        
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Failed to query session records from SQLite database: {e}")
        return []
