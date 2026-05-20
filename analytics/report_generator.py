import csv
import json
import os
from analytics.insight_engine import generate_insights
from utils.logger import logger

def export_session_reports(summary, history, file_manager):
    """
    Exports session metrics, raw tracking histories, and intelligent safety insights to disk.
    
    Files Created:
    - session_summary.json: Contains aggregated statistics and insights details.
    - session_report.csv: Contains step-by-step frame log history.
    - recommendations.txt: Contains formatted recommendations and fatigue interpretation.
    
    Parameters:
    - summary: dict containing session aggregated stats.
    - history: list of frame log tuples.
    - file_manager: FileManager instance to resolve target destination paths.
    """
    try:
        logger.info("Generating session reports...")
        
        # 1. Run the intelligent insights engine
        insights = generate_insights(summary)
        summary.update(insights)  # Injects: severity, summary, recommendations
        
        logger.info("Saving CSV, JSON, and Recommendations text reports...")
        
        # 2. Save JSON summary report (now including insights metadata)
        json_path = file_manager.get_report_path("session_summary.json")
        with open(json_path, "w") as f:
            json.dump(summary, f, indent=4)
        logger.info(f"Saved session summary details to {json_path}")
            
        # 3. Save CSV raw history report
        csv_path = file_manager.get_report_path("session_report.csv")
        csv_headers = ["Timestamp (s)", "Fatigue Score (%)", "Eyes Closed State", "Yawning State", "Head Tilt State"]
        
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)
            for row in history:
                formatted_row = [f"{row[0]:.2f}", f"{row[1]:.1f}", int(row[2]), int(row[3]), int(row[4])]
                writer.writerow(formatted_row)
        logger.info(f"Saved CSV tracking logs to {csv_path}")
                
        # 4. Save formatted Recommendations text file report
        txt_path = file_manager.get_report_path("recommendations.txt")
        with open(txt_path, "w") as f:
            f.write("SleepGuard AI Fatigue & Rest Recommendations Report\n")
            f.write("==================================================\n")
            f.write(f"Session Date: {summary['date']}\n")
            f.write(f"Session Duration: {summary['duration']:.1f} seconds\n")
            f.write(f"Fatigue Severity Classification: {insights['severity']}\n\n")
            
            f.write("Fatigue Summary:\n")
            f.write(f"{insights['summary']}\n\n")
            
            f.write("Actionable Recommendations:\n")
            for rec in insights['recommendations']:
                f.write(f"- {rec}\n")
                
        logger.info(f"Exported recommendations report to {txt_path}.")
        logger.info("Session reports export complete.")
    except Exception as e:
        logger.error(f"Error occurred during session reports generation: {e}")
