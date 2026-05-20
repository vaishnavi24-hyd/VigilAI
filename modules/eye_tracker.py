import cv2

class EyeTracker:
    """
    A beginner-friendly class to track and highlight eyes using Face Mesh landmarks.
    """
    def __init__(self):
        # Specific landmark indices for calculating Eye Aspect Ratio (EAR)
        # Order: [p1, p2, p3, p4, p5, p6]
        # p1: corner, p2: top, p3: top, p4: opposite corner, p5: bottom, p6: bottom
        self.right_eye_indices = [33, 160, 158, 133, 153, 144]
        self.left_eye_indices = [362, 385, 387, 263, 373, 380]

    def track_eyes(self, img, face_landmarks):
        """
        Extracts specific eye landmarks, draws them, and returns their coordinates.
        """
        left_eye_coords = []
        right_eye_coords = []
        
        # Ensure we have a face
        if not face_landmarks:
            return img, left_eye_coords, right_eye_coords
            
        # 1. Extract and draw left eye landmarks (6 specific points for EAR)
        for idx in self.left_eye_indices:
            coord = face_landmarks[idx]
            left_eye_coords.append(coord)
            # Highlight left eye with green circles
            cv2.circle(img, (coord[0], coord[1]), 2, (0, 255, 0), -1)
            
        # 2. Extract and draw right eye landmarks (6 specific points for EAR)
        for idx in self.right_eye_indices:
            coord = face_landmarks[idx]
            right_eye_coords.append(coord)
            # Highlight right eye with red circles
            cv2.circle(img, (coord[0], coord[1]), 2, (0, 0, 255), -1)
            
        return img, left_eye_coords, right_eye_coords
