import cv2
import time
from datetime import datetime

# Import central settings and professional utilities
from config import settings
from utils.logger import logger
from utils.file_manager import FileManager

# Import modular pipeline components
from modules.face_mesh import FaceMeshDetector
from modules.eye_tracker import EyeTracker
from modules.ear import calculate_ear
from modules.drowsiness import DrowsinessDetector
from modules.yawn_detector import YawnDetector
from modules.head_pose import HeadPoseEstimator
from modules.fatigue_engine import FatigueEngine
from modules.alert_manager import AlertManager

# Import database, analytics, and reporting helper functions
from modules.database import initialize_database, save_session
from analytics.charts import generate_charts
from analytics.report_generator import export_session_reports
from analytics.dashboard import generate_session_dashboard

def main():
    logger.info("Initializing SleepGuard AI application...")

    # 1. Initialize SQLite Database
    initialize_database()

    # 2. Instantiate File Manager to handle report file exports pathing
    file_manager = FileManager()

    # 3. Initialize Webcam Capture (Device Index 0) with error checking
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise IOError("Could not access or open webcam device index 0.")
        logger.info("Webcam interface initialized successfully.")
    except Exception as e:
        logger.error(f"Webcam hardware initialization failure: {e}")
        return

    # 4. Initialize AI pipeline modules using configuration settings parameters
    try:
        detector = FaceMeshDetector(max_num_faces=1)
        eye_tracker = EyeTracker()
        
        # Configure thresholds from settings
        drowsiness_detector = DrowsinessDetector(
            ear_threshold=settings.EAR_THRESHOLD, 
            frame_limit=settings.EAR_FRAME_LIMIT
        )
        yawn_detector = YawnDetector(
            mar_threshold=settings.MAR_THRESHOLD, 
            frame_limit=settings.MAR_FRAME_LIMIT
        )
        head_pose_estimator = HeadPoseEstimator(
            pitch_threshold=settings.PITCH_THRESHOLD, 
            roll_threshold=settings.ROLL_THRESHOLD, 
            frame_limit=settings.TILT_FRAME_LIMIT
        )
        fatigue_engine = FatigueEngine(
            w_eye=settings.WEIGHT_EYES, 
            w_tilt=settings.WEIGHT_TILT, 
            w_yawn=settings.WEIGHT_YAWN, 
            alarm_threshold=settings.ALARM_THRESHOLD
        )
        alert_manager = AlertManager(
            medium_alarm_duration=settings.MEDIUM_ALARM_DURATION, 
            cooldown_duration=settings.COOLDOWN_DURATION
        )
        logger.info("AI pipeline detectors and AlertManager initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize AI tracking pipeline components: {e}")
        cap.release()
        return

    # 5. Session Tracking Statistics variables
    session_start_time = time.time()
    fatigue_event_count = 0  # Tracks when alerts transition to ACTIVE state
    was_alerting = False
    
    # Running averages tracking to calculate average EAR for the entire session
    ear_sum = 0.0
    ear_count = 0

    # Fatigue score tracking statistics
    fatigue_sum = 0.0
    fatigue_count = 0
    peak_fatigue = 0.0

    # Frame history log list
    # Format of elements: (elapsed_seconds, fatigue_score, is_eye_closed_marker, is_yawning_marker, is_tilted_marker)
    session_history = []

    # Time variables for live FPS calculation
    prev_time = 0

    logger.info("Starting SleepGuard AI monitor loop. Press 'q' to quit.")

    # Set up OpenCV window
    window_name = "SleepGuard AI"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    try:
        while cap.isOpened():
            # FRAME PIPELINE - Step 1: Capture frame from webcam (BGR format)
            success, frame = cap.read()
            if not success:
                logger.warning("Failed to grab video frame from webcam stream.")
                break

            # Calculate live FPS
            curr_time = time.time()
            fps = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0.0
            prev_time = curr_time

            # FRAME PIPELINE - Step 2: Run Face Mesh detection (draw=True paints landmarks on BGR frame)
            try:
                frame, faces = detector.find_face_mesh(frame, draw=True)
            except Exception as e:
                logger.warning(f"Error during face mesh detection frame processing: {e}")
                faces = []

            if faces:
                # Get landmark coordinates of the primary detected face
                face_landmarks = faces[0]

                # FRAME PIPELINE - Step 3: Extract and draw eye landmarks (highlights eye borders)
                frame, left_eye, right_eye = eye_tracker.track_eyes(frame, face_landmarks)

                # FRAME PIPELINE - Step 4: Extract and draw mouth landmarks (highlights mouth inner borders)
                is_yawning, yawn_frame_count, mar = yawn_detector.check_yawn(frame, face_landmarks)

                # FRAME PIPELINE - Step 5: Estimate Head Pose angles and render 3D direction vector
                is_tilted, tilt_type, pitch, roll = head_pose_estimator.check_tilt(frame, face_landmarks)

                # Ensure we have successfully tracked all required 6 landmarks per eye
                if len(left_eye) == 6 and len(right_eye) == 6:
                    # FRAME PIPELINE - Step 6: Calculate Eye Aspect Ratio (EAR)
                    left_ear = calculate_ear(left_eye)
                    right_ear = calculate_ear(right_eye)
                    avg_ear = (left_ear + right_ear) / 2.0

                    # Accumulate for overall session EAR statistics
                    ear_sum += avg_ear
                    ear_count += 1

                    # FRAME PIPELINE - Step 7: Check raw eye closure counter (does not trigger alarm directly)
                    _, closed_frame_count = drowsiness_detector.check(avg_ear)

                    # FRAME PIPELINE - Step 8: Calculate overall weighted fatigue confidence score
                    fatigue_score, fatigue_level, level_color = fatigue_engine.compute_fatigue(
                        closed_frame_count, drowsiness_detector.frame_limit,
                        yawn_frame_count, yawn_detector.frame_limit,
                        head_pose_estimator.frame_count, head_pose_estimator.frame_limit
                    )

                    # Update peak and average fatigue statistics
                    peak_fatigue = max(peak_fatigue, fatigue_score)
                    fatigue_sum += fatigue_score
                    fatigue_count += 1

                    # FRAME PIPELINE - Step 9: Process alerts through Intelligent AlertManager lifecycle
                    alert_state, alert_level = alert_manager.update_alerts(fatigue_score, fatigue_level)

                    # SESSION TRACKING - Count fatigue warning instances on ACTIVE transition
                    if alert_state == "ACTIVE":
                        if not was_alerting:
                            fatigue_event_count += 1
                            was_alerting = True
                            logger.warning(f"Fatigue alert triggered state active: Level={alert_level}, Score={fatigue_score:.1f}%")
                    else:
                        was_alerting = False

                    # Record frame timeline telemetry
                    elapsed_seconds = time.time() - session_start_time
                    session_history.append((
                        elapsed_seconds,
                        fatigue_score,
                        1 if closed_frame_count > 0 else 0,
                        1 if yawn_frame_count > 0 else 0,
                        1 if head_pose_estimator.frame_count > 0 else 0
                    ))

                    # Identify active fatigue signals
                    active_signals = []
                    if closed_frame_count > 0:
                        active_signals.append("Eyes Closed")
                    if yawn_frame_count > 0:
                        active_signals.append("Yawning")
                    if head_pose_estimator.frame_count > 0:
                        active_signals.append(tilt_type)
                    signals_text = ", ".join(active_signals) if active_signals else "None"

                    # FRAME PIPELINE - Step 10: Render informational overlays on the frame
                    # Overall Fatigue Score & level
                    cv2.putText(frame, f"FATIGUE: {fatigue_level} ({fatigue_score:.0f}%)", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, level_color, 3)
                    cv2.putText(frame, f"Active Signals: {signals_text}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Eye statistics
                    cv2.putText(frame, f"EAR: {avg_ear:.2f}", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(frame, f"Closed Frames: {closed_frame_count}/{drowsiness_detector.frame_limit}", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
                    
                    # Alert Lifecycle Manager Status
                    alert_status = alert_manager.get_status_text()
                    alert_color = (0, 0, 255) if alert_state == "ACTIVE" else ((0, 165, 255) if alert_state == "COOLDOWN" else (0, 255, 0))
                    cv2.putText(frame, f"ALERT: {alert_status}", (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, alert_color, 2)

                    # Mouth statistics
                    yawn_status_text = "YAWNING" if is_yawning else "NOT YAWNING"
                    yawn_status_color = (0, 0, 255) if is_yawning else (0, 255, 0)
                    cv2.putText(frame, f"YAWN: {yawn_status_text}", (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.8, yawn_status_color, 2)
                    cv2.putText(frame, f"MAR: {mar:.2f}", (20, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(frame, f"Yawn Count: {yawn_detector.yawn_count}", (20, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

                    # Head Pose statistics
                    tilt_status_text = f"TILTED ({tilt_type})" if is_tilted else "HEAD NORMAL"
                    tilt_status_color = (0, 0, 255) if is_tilted else (0, 255, 0)
                    cv2.putText(frame, f"HEAD: {tilt_status_text}", (20, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.8, tilt_status_color, 2)
                    cv2.putText(frame, f"Pitch: {pitch:.1f} | Roll: {roll:.1f}", (20, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(frame, f"Tilt Count: {head_pose_estimator.tilt_event_count}", (20, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

            else:
                # If no face is detected: reset state counters and stop active alert
                drowsiness_detector.check(1.0)
                yawn_detector.check_yawn(None, None)
                head_pose_estimator.check_tilt(None, None)
                alert_manager.stop()
                cv2.putText(frame, "STATUS: No Face Detected", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)

            # Draw FPS overlay
            cv2.putText(frame, f"FPS: {int(fps)}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            # FRAME PIPELINE - Step 11: Render fully annotated BGR frame to screen
            cv2.imshow(window_name, frame)

            # Polling for user events: Press 'q' key to quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("Exit requested by user via keyboard ('q' key).")
                break

            # Polling for OS window close click
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                logger.info("Exit requested by user via window close click.")
                break

    except KeyboardInterrupt:
        logger.info("Application loop interrupted via keyboard (Ctrl+C).")
    except Exception as e:
        logger.error(f"Unexpected runtime failure in monitor loop: {e}")
    finally:
        # SESSION WRITING - Calculate statistics and record them to database on exit
        logger.info("Finalizing session tracking statistics...")
        session_duration = time.time() - session_start_time
        overall_avg_ear = (ear_sum / ear_count) if ear_count > 0 else 0.0
        overall_avg_fatigue = (fatigue_sum / fatigue_count) if fatigue_count > 0 else 0.0
        session_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save session to database only if we gathered any tracking frames
        if ear_count > 0:
            try:
                # 1. Save summary record in SQLite database
                save_session(
                    session_date, 
                    session_duration, 
                    fatigue_event_count, 
                    yawn_detector.yawn_count, 
                    head_pose_estimator.tilt_event_count, 
                    overall_avg_ear,
                    overall_avg_fatigue,
                    peak_fatigue
                )
                
                # 2. Compile python dictionary representation of the session
                summary_data = {
                    "date": session_date,
                    "duration": session_duration,
                    "drowsiness_events": fatigue_event_count,
                    "yawn_events": yawn_detector.yawn_count,
                    "tilt_events": head_pose_estimator.tilt_event_count,
                    "average_fatigue": overall_avg_fatigue,
                    "peak_fatigue": peak_fatigue,
                    "average_ear": overall_avg_ear,
                    "alert_count": fatigue_event_count
                }
                
                # Create timestamped reports subfolder
                logger.info("Creating session folder...")
                file_manager.create_session_folder()

                # 3. Export CSV logs and JSON summaries using central FileManager paths
                logger.info("Exporting reports...")
                export_session_reports(summary_data, session_history, file_manager)
                
                # 4. Generate visual dashboard and timeline analytics using central FileManager paths
                generate_session_dashboard(summary_data, session_history, file_manager)
                
                # 5. Automatically update historical database graphics
                generate_charts()
                
                # 6. Open session directory automatically
                file_manager.open_session_folder()
                
            except Exception as exit_err:
                logger.error(f"Error during final session save or charts generation: {exit_err}")
        else:
            logger.warning("No tracking data captured. Session data will not be saved.")

        # CLEANUP LOGIC - Release all resources safely on shutdown
        logger.info("Cleaning up webcam and audio resources...")
        try:
            cap.release()
            cv2.destroyAllWindows()
            alert_manager.cleanup()
        except Exception as cleanup_err:
            logger.error(f"Failed to cleanly release resources: {cleanup_err}")
        logger.info("Graceful shutdown complete.")

if __name__ == "__main__":
    main()
