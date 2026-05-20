import os
import matplotlib
matplotlib.use('Agg')  # Headless mode to avoid graphical conflicts with OpenCV windows
import matplotlib.pyplot as plt
from modules.database import get_all_sessions
from config.settings import BASE_REPORTS_DIR
from utils.logger import logger

def generate_charts():
    """
    Retrieves all sessions from the database and generates an updated
    session analytics dashboard showing drowsiness, yawn, and head tilt correlation.
    """
    try:
        sessions = get_all_sessions()
        if not sessions:
            logger.warning("No session records found in the database. Charts will not be generated.")
            return

        # Extract metrics
        dates = [row[0] for row in sessions]
        durations = [row[1] for row in sessions]
        drowsy_counts = [row[2] for row in sessions]
        yawn_counts = [row[3] for row in sessions]
        tilt_counts = [row[4] for row in sessions]
        avg_ears = [row[5] for row in sessions]

        # Convert durations to minutes for cleaner graphs
        durations_minutes = [d / 60.0 for d in durations]

        # Format dates to strip out year for clean labels
        formatted_dates = []
        for d in dates:
            try:
                parts = d.split(" ")
                if len(parts) >= 2:
                    date_part = parts[0][5:]  # MM-DD
                    time_part = parts[1][:5]  # HH:MM
                    formatted_dates.append(f"{date_part}\n{time_part}")
                else:
                    formatted_dates.append(d)
            except:
                formatted_dates.append(d)

        fig, axs = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle("SleepGuard AI - Session Fatigue Dashboard", fontsize=16, fontweight='bold', color='#2C3E50')

        # Chart 1: Drowsiness, Yawn, and Head Tilt Trends (Triple Line Plot for fatigue correlation)
        axs[0].plot(formatted_dates, drowsy_counts, marker='o', color='#E74C3C', linewidth=2, label='Drowsy Warnings')
        axs[0].plot(formatted_dates, yawn_counts, marker='^', color='#F39C12', linewidth=2, linestyle='-.', label='Yawns')
        axs[0].plot(formatted_dates, tilt_counts, marker='s', color='#9B59B6', linewidth=2, linestyle=':', label='Head Tilts')
        axs[0].set_title("Fatigue Event Correlation", fontsize=12, fontweight='bold')
        axs[0].set_xlabel("Sessions")
        axs[0].set_ylabel("Event Count")
        axs[0].grid(True, linestyle='--', alpha=0.6)
        axs[0].tick_params(axis='x', rotation=45)
        axs[0].legend()
        for i in range(len(sessions)):
            axs[0].annotate(str(drowsy_counts[i]), (formatted_dates[i], drowsy_counts[i]), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=9, color='#C0392B')
            axs[0].annotate(str(yawn_counts[i]), (formatted_dates[i], yawn_counts[i]), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=9, color='#D35400')
            axs[0].annotate(str(tilt_counts[i]), (formatted_dates[i], tilt_counts[i]), textcoords="offset points", xytext=(0, -25), ha='center', fontsize=9, color='#8E44AD')

        # Chart 2: Session Durations (Bar Chart)
        axs[1].bar(formatted_dates, durations_minutes, color='#3498DB', alpha=0.85, width=0.5, edgecolor='#2980B9')
        axs[1].set_title("Session Durations (Minutes)", fontsize=12, fontweight='bold')
        axs[1].set_xlabel("Sessions")
        axs[1].set_ylabel("Duration (Min)")
        axs[1].grid(True, linestyle='--', alpha=0.6)
        axs[1].tick_params(axis='x', rotation=45)
        for i, txt in enumerate(durations_minutes):
            axs[1].annotate(f"{txt:.1f}", (formatted_dates[i], durations_minutes[i]), textcoords="offset points", xytext=(0, 5), ha='center', fontsize=9)

        # Chart 3: Fatigue Severity - Average EAR (Line Plot with threshold line)
        axs[2].plot(formatted_dates, avg_ears, marker='s', color='#2ECC71', linewidth=2, linestyle='--')
        axs[2].axhline(y=0.25, color='#E74C3C', linestyle=':', label='Threshold (0.25)')
        axs[2].set_title("Average EAR per Session (Eye Closure)", fontsize=12, fontweight='bold')
        axs[2].set_xlabel("Sessions")
        axs[2].set_ylabel("Avg Eye Aspect Ratio")
        axs[2].set_ylim(0, 0.4)
        axs[2].grid(True, linestyle='--', alpha=0.6)
        axs[2].tick_params(axis='x', rotation=45)
        axs[2].legend(loc='lower left')
        for i, txt in enumerate(avg_ears):
            axs[2].annotate(f"{txt:.2f}", (formatted_dates[i], avg_ears[i]), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=9, color='#27AE60')

        plt.tight_layout()

        os.makedirs(BASE_REPORTS_DIR, exist_ok=True)
        save_path = os.path.join(BASE_REPORTS_DIR, "session_analytics.png")
        plt.savefig(save_path, dpi=100)
        plt.close()
        
        logger.info(f"Historical analytics dashboard successfully saved to {save_path}.")
    except Exception as e:
        logger.error(f"Error compiling historical analytics dashboard: {e}")
