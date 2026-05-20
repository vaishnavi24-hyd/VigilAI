import cv2
from scipy.spatial import distance as dist

class YawnDetector:
    """
    A beginner-friendly class to detect yawning by monitoring the Mouth Aspect Ratio (MAR)
    using MediaPipe FaceMesh landmarks.
    """
    def __init__(self, mar_threshold=0.6, frame_limit=15):
        # The ratio threshold above which the mouth is considered open wide
        self.mar_threshold = mar_threshold
        
        # The number of consecutive frames the mouth must be open to trigger a Yawn event
        self.frame_limit = frame_limit
        
        # Frame counter for consecutive frames where MAR is above threshold
        self.frame_count = 0
        
        # Current state: True = Yawning, False = Not Yawning
        self.is_yawning = False
        
        # Total yawn events count for the session
        self.yawn_count = 0
        
        # Tracking state to detect transitions (NOT YAWNING -> YAWNING)
        self.was_yawning = False
        
        # Specific landmark indices representing the inner boundary of the mouth
        # Format mirrors the EAR structure: [p1, p2, p3, p4, p5, p6]
        # p1, p4: horizontal corners (78, 308)
        # p2, p3: upper inner lip (81, 311)
        # p5, p6: lower inner lip (317, 87)
        self.mouth_indices = [78, 81, 311, 308, 317, 87]

    def calculate_mar(self, mouth_coords):
        """
        Calculates the Mouth Aspect Ratio (MAR) using 6 coordinates.
        Formula: (dist(p2, p6) + dist(p3, p5)) / (2.0 * dist(p1, p4))
        """
        # Compute vertical Euclidean distances
        A = dist.euclidean(mouth_coords[1], mouth_coords[5])  # 81 to 87
        B = dist.euclidean(mouth_coords[2], mouth_coords[4])  # 311 to 317
        
        # Compute horizontal Euclidean distance
        C = dist.euclidean(mouth_coords[0], mouth_coords[3])  # 78 to 308
        
        # Avoid division by zero
        if C == 0:
            return 0.0
            
        # Calculate Mouth Aspect Ratio
        mar = (A + B) / (2.0 * C)
        return mar

    def check_yawn(self, img, face_landmarks):
        """
        Extracts mouth landmarks, draws them on the image, computes MAR,
        and runs consecutive frame logic to identify yawn events.
        
        Returns: (is_yawning, frame_count, mar)
        """
        mouth_coords = []
        
        # Ensure face landmarks are present
        if not face_landmarks:
            return self.is_yawning, self.frame_count, 0.0
            
        # 1. Extract coordinates and draw mouth landmarks (yellow dots)
        for idx in self.mouth_indices:
            coord = face_landmarks[idx]
            mouth_coords.append(coord)
            cv2.circle(img, (coord[0], coord[1]), 2, (0, 255, 255), -1)

        # 2. Calculate MAR
        mar = self.calculate_mar(mouth_coords)

        # 3. Yawn detection with threshold and frame counter
        if mar > self.mar_threshold:
            self.frame_count += 1
            
            # If open wide for enough frames, set state to Yawning
            if self.frame_count >= self.frame_limit:
                self.is_yawning = True
                
                # Increment event count only on state transition (awake/not yawning -> yawning)
                if not self.was_yawning:
                    self.yawn_count += 1
                    self.was_yawning = True
        else:
            # Reset frame count and state
            self.frame_count = 0
            self.is_yawning = False
            self.was_yawning = False
            
        return self.is_yawning, self.frame_count, mar
