from scipy.spatial import distance as dist

def calculate_ear(eye):
    """
    Calculates the Eye Aspect Ratio (EAR) for a single eye.
    The eye is a list of 6 coordinates [p1, p2, p3, p4, p5, p6].
    """
    # Compute the euclidean distances between the two sets of 
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    
    # Compute the euclidean distance between the horizontal 
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    
    # Calculate EAR
    ear = (A + B) / (2.0 * C)
    
    return ear
