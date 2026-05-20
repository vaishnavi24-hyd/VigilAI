import os
import matplotlib
matplotlib.use('Agg')  # Headless mode to avoid graphical conflicts with OpenCV windows
import matplotlib.pyplot as plt
import numpy as np
from utils.logger import logger

def generate_session_dashboard(summary, history, file_manager):
    """
    Generates professional session analytics and reporting charts.
    
    Creates:
    - fatigue_trend.png: Line plot tracing fatigue score (%) over elapsed seconds.
    - drowsiness_chart.png: Steps-post plots showing timing of active fatigue alerts.
    - dashboard_summary.png: Multi-panel dashboard summarizing metrics.
    
    Parameters:
    - summary: dict containing session aggregated stats.
    - history: list of frame logs.
    - file_manager: FileManager instance to resolve target destination paths.
    """
    try:
        if not history:
            logger.warning("History data is empty. Cannot generate session charts.")
            return

        logger.info("Plotting session dashboard charts...")

        # Extract timeline lists
        timestamps = [row[0] for row in history]
        fatigue_scores = [row[1] for row in history]
        eye_closed = [row[2] for row in history]
        yawning = [row[3] for row in history]
        tilted = [row[4] for row in history]

        # --- Plot 1: fatigue_trend.png (Fatigue Confidence Score Timeline) ---
        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, fatigue_scores, color='#3498DB', linewidth=2.5, label='Fatigue Score (%)')
        plt.fill_between(timestamps, fatigue_scores, color='#3498DB', alpha=0.15)
        plt.axhline(y=40.0, color='#E74C3C', linestyle='--', linewidth=1.5, label='Alarm Threshold (40%)')
        plt.title('Fatigue Confidence Score Timeline', fontsize=14, fontweight='bold', color='#2C3E50')
        plt.xlabel('Elapsed Time (Seconds)', fontsize=11)
        plt.ylabel('Fatigue Confidence (%)', fontsize=11)
        plt.ylim(0, 105)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(loc='upper left')
        plt.tight_layout()
        trend_path = file_manager.get_report_path('fatigue_trend.png')
        plt.savefig(trend_path, dpi=100)
        plt.close()
        logger.info(f"Saved fatigue trend chart to {trend_path}.")

        # --- Plot 2: drowsiness_chart.png (Fatigue Warning Signals Timeline) ---
        fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        
        # Eyes closed
        axs[0].plot(timestamps, eye_closed, color='#E74C3C', linewidth=2, drawstyle='steps-post')
        axs[0].fill_between(timestamps, eye_closed, color='#E74C3C', alpha=0.2, step='post')
        axs[0].set_ylabel('Eyes Closed', fontsize=10, fontweight='bold')
        axs[0].set_ylim(-0.1, 1.1)
        axs[0].set_yticks([0, 1])
        axs[0].set_yticklabels(['Open', 'Closed'])
        axs[0].grid(True, linestyle=':', alpha=0.6)
        
        # Yawning
        axs[1].plot(timestamps, yawning, color='#F39C12', linewidth=2, drawstyle='steps-post')
        axs[1].fill_between(timestamps, yawning, color='#F39C12', alpha=0.2, step='post')
        axs[1].set_ylabel('Yawning', fontsize=10, fontweight='bold')
        axs[1].set_ylim(-0.1, 1.1)
        axs[1].set_yticks([0, 1])
        axs[1].set_yticklabels(['No', 'Yes'])
        axs[1].grid(True, linestyle=':', alpha=0.6)
        
        # Head Tilt
        axs[2].plot(timestamps, tilted, color='#9B59B6', linewidth=2, drawstyle='steps-post')
        axs[2].fill_between(timestamps, tilted, color='#9B59B6', alpha=0.2, step='post')
        axs[2].set_ylabel('Head Tilted', fontsize=10, fontweight='bold')
        axs[2].set_ylim(-0.1, 1.1)
        axs[2].set_yticks([0, 1])
        axs[2].set_yticklabels(['Upright', 'Tilted'])
        axs[2].grid(True, linestyle=':', alpha=0.6)
        
        plt.xlabel('Elapsed Time (Seconds)', fontsize=11)
        fig.suptitle('Fatigue Warning Signals Timeline', fontsize=14, fontweight='bold', color='#2C3E50')
        plt.tight_layout()
        signals_path = file_manager.get_report_path('drowsiness_chart.png')
        plt.savefig(signals_path, dpi=100)
        plt.close()
        logger.info(f"Saved signals timeline chart to {signals_path}.")

        # --- Plot 3: dashboard_summary.png (Session Summary Dashboard Panels) ---
        fig, axs = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Session Summary Dashboard', fontsize=16, fontweight='bold', color='#2C3E50')

        # Panel 1: Metrics Text Box
        axs[0].axis('off')
        metrics_text = (
            f"Session Date: {summary['date']}\n\n"
            f"Duration: {summary['duration']:.1f} seconds\n\n"
            f"Avg Fatigue: {summary['average_fatigue']:.1f}%\n\n"
            f"Peak Fatigue: {summary['peak_fatigue']:.1f}%\n\n"
            f"Total Alerts Fired: {summary['alert_count']}\n\n"
            f"Avg Eye Aspect Ratio: {summary['average_ear']:.3f}\n"
        )
        axs[0].text(0.1, 0.9, "Key Session Metrics", fontsize=14, fontweight='bold', color='#2C3E50')
        axs[0].text(0.1, 0.2, metrics_text, fontsize=12, family='sans-serif',
                    bbox=dict(facecolor='#ECF0F1', alpha=0.8, boxstyle='round,pad=1.5'))

        # Panel 2: Events Bar Chart
        event_labels = ['Drowsy Warns', 'Yawns', 'Head Tilts']
        event_counts = [summary['drowsiness_events'], summary['yawn_events'], summary['tilt_events']]
        axs[1].bar(event_labels, event_counts, color=['#E74C3C', '#F39C12', '#9B59B6'], width=0.4)
        axs[1].set_title('Fatigue Event Distribution', fontsize=14, fontweight='bold')
        axs[1].set_ylabel('Total Count')
        axs[1].grid(True, linestyle='--', alpha=0.5)
        for i, v in enumerate(event_counts):
            axs[1].text(i, v + 0.1, str(v), ha='center', fontweight='bold')

        # Panel 3: Exposure Pie Chart
        scores_array = np.array(fatigue_scores)
        low_frames = np.sum(scores_array < 20.0)
        med_frames = np.sum((scores_array >= 20.0) & (scores_array < 40.0))
        high_frames = np.sum(scores_array >= 40.0)
        
        exposure_slices = [low_frames, med_frames, high_frames]
        exposure_labels = ['Low (<20%)', 'Medium (20-40%)', 'High (>=40%)']
        exposure_colors = ['#2ECC71', '#F39C12', '#E74C3C']
        
        # Filter empty slices
        filtered_slices = []
        filtered_labels = []
        filtered_colors = []
        for s, l, c in zip(exposure_slices, exposure_labels, exposure_colors):
            if s > 0:
                filtered_slices.append(s)
                filtered_labels.append(l)
                filtered_colors.append(c)

        if filtered_slices:
            axs[2].pie(filtered_slices, labels=filtered_labels, colors=filtered_colors, autopct='%1.1f%%', startangle=90)
        else:
            axs[2].text(0.5, 0.5, 'No fatigue data recorded', ha='center', va='center')
        axs[2].set_title('Exposure Time by Fatigue Level', fontsize=14, fontweight='bold')

        plt.tight_layout()
        summary_path = file_manager.get_report_path('dashboard_summary.png')
        plt.savefig(summary_path, dpi=100)
        plt.close()
        
        logger.info(f"Saved dashboard summary panels to {summary_path}.")
    except Exception as e:
        logger.error(f"Error occurred during session dashboard generation: {e}")
