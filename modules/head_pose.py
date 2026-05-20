import cv2
import numpy as np

class HeadPoseEstimator:
    """
    A beginner-friendly class to estimate head pose (pitch, yaw, roll) and detect head tilt/nodding off
    using MediaPipe FaceMesh landmarks and a 3D PnP solver.
    """
    def __init__(self, pitch_threshold=-15.0, roll_threshold=15.0, frame_limit=25):
        # Configurable thresholds for tilt (in degrees)
        self.pitch_threshold = pitch_threshold  # Negative means downward tilt (nodding off)
        self.roll_threshold = roll_threshold    # Left/right tilt
        
        # Consecutive frame count threshold to avoid false positives from natural motion
        self.frame_limit = frame_limit
        self.frame_count = 0
        
        # Current head states
        self.is_tilted = False
        self.tilt_type = "NORMAL"  # Can be: "NORMAL", "DOWNWARD TILT", "SIDE TILT"
        
        # Event tracking
        self.tilt_event_count = 0
        self.was_tilted = False

        # Landmark indices for pose estimation:
        # 1: Nose tip
        # 152: Chin
        # 33: Left eye left corner
        # 263: Right eye right corner
        # 61: Left mouth corner
        # 291: Right mouth corner
        self.pose_indices = [1, 152, 33, 263, 61, 291]
        
        # 3D generic facial model coordinates
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype=np.float32)

    def estimate_pose(self, img, face_landmarks):
        """
        Calculates head orientation angles (pitch, yaw, roll) and visualizes the pose.
        
        Returns: (pitch, yaw, roll, nose_end_point2D_tuple, nose_tip_tuple)
        """
        img_h, img_w, _ = img.shape
        
        # Extract 2D coordinates for the 6 landmark points
        image_points = []
        for idx in self.pose_indices:
            pt = face_landmarks[idx]
            image_points.append([pt[0], pt[1]])
        image_points = np.array(image_points, dtype=np.float32)

        # Camera matrix approximation
        focal_length = img_w
        center = (img_w / 2, img_h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float32)

        # Lens distortion approximation (assume zero distortion)
        dist_coeffs = np.zeros((4, 1), dtype=np.float32)

        # Solve Perspective-n-Point (PnP) problem
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return 0.0, 0.0, 0.0, None, None

        # Project a 3D point (axis out from nose tip) onto the 2D image plane to draw the vector line
        axis_3d = np.array([(0.0, 0.0, 200.0)], dtype=np.float32)
        nose_end_point2D, _ = cv2.projectPoints(
            axis_3d, rotation_vector, translation_vector, camera_matrix, dist_coeffs
        )

        # Extract Euler angles from rotation matrix
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        
        # Euler decomposition
        r = rotation_matrix
        sy = np.sqrt(r[0, 0] * r[0, 0] + r[1, 0] * r[1, 0])
        singular = sy < 1e-6

        if not singular:
            pitch = np.arctan2(r[2, 1], r[2, 2])
            yaw = np.arctan2(-r[2, 0], sy)
            roll = np.arctan2(r[1, 0], r[0, 0])
        else:
            pitch = np.arctan2(-r[1, 2], r[1, 1])
            yaw = np.arctan2(-r[2, 0], sy)
            roll = 0.0

        # Convert to degrees
        pitch = np.degrees(pitch)
        yaw = np.degrees(yaw)
        roll = np.degrees(roll)

        # Draw a line from the nose tip along the face direction vector
        p1 = (int(image_points[0][0]), int(image_points[0][1]))
        p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
        
        # Keep endpoints within reasonable image boundaries
        p2 = (max(0, min(p2[0], img_w)), max(0, min(p2[1], img_h)))
        
        # Draw visualization line and circles
        cv2.line(img, p1, p2, (255, 0, 255), 2)  # Pink direction vector line
        cv2.circle(img, p1, 3, (0, 0, 255), -1)  # Red dot on nose tip
        
        return pitch, yaw, roll, p2, p1

    def check_tilt(self, img, face_landmarks):
        """
        Analyzes head pose, tracks consecutive frames, and triggers alerts if
        tilted or nodding off.
        
        Returns: (is_tilted, tilt_type, pitch, roll)
        """
        if not face_landmarks:
            return self.is_tilted, self.tilt_type, 0.0, 0.0
            
        pitch, yaw, roll, _, _ = self.estimate_pose(img, face_landmarks)
        
        # Determine if head is tilted past thresholds
        # Pitch: Negative means looking down (e.g. nodding off)
        # Roll: Left/right tilt deviation
        is_nodding_off = pitch < self.pitch_threshold
        is_sideways_tilted = abs(roll) > self.roll_threshold

        if is_nodding_off or is_sideways_tilted:
            self.frame_count += 1
            if self.frame_count >= self.frame_limit:
                self.is_tilted = True
                
                # Classify tilt type
                if is_nodding_off:
                    self.tilt_type = "DOWNWARD TILT"
                else:
                    self.tilt_type = "SIDE TILT"
                
                # Check for state transition to count events
                if not self.was_tilted:
                    self.tilt_event_count += 1
                    self.was_tilted = True
        else:
            self.frame_count = 0
            self.is_tilted = False
            self.tilt_type = "NORMAL"
            self.was_tilted = False

        return self.is_tilted, self.tilt_type, pitch, roll
