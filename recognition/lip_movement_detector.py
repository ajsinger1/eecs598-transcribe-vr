import numpy as np

class LipMovementDetector:
    def __init__(self, num_frames_to_analyze=5, dynamic_threshold_factor=1.5):
        self.previous_mar_values = []
        self.num_frames_to_analyze = num_frames_to_analyze
        self.dynamic_threshold_factor = dynamic_threshold_factor
        self.baseline_mar = None  # You may need to calculate this for each person individually
    
    def calculate_mar(self, landmarks):
        # Points 51 and 57 are the top and bottom of the inner mouth.
        top_lip_point = np.array([landmarks.part(51).x, landmarks.part(51).y])
        bottom_lip_point = np.array([landmarks.part(57).x, landmarks.part(57).y])
        mar = np.linalg.norm(top_lip_point - bottom_lip_point)
        return mar
    
    def update_baseline(self, mar_value):
        if self.baseline_mar is None:
            self.baseline_mar = mar_value
        else:
            # Adjust the baseline MAR value based on new observations
            self.baseline_mar = (self.baseline_mar + mar_value) / 2
    
    def is_talking(self, mar_value):
        if len(self.previous_mar_values) < self.num_frames_to_analyze:
            # Not enough data yet
            return False
        
        # Calculate the average of the previous MAR values
        avg_previous_mar = np.mean(self.previous_mar_values)
        
        # Define a dynamic threshold based on the baseline MAR and a factor
        threshold = self.dynamic_threshold_factor * self.baseline_mar
        
        # Check if the current MAR has significantly deviated from the average
        return abs(mar_value - avg_previous_mar) > threshold
    
    def add_mar_value(self, mar_value):
        # Add the current MAR value to the list, maintaining the list size
        self.previous_mar_values.append(mar_value)
        if len(self.previous_mar_values) > self.num_frames_to_analyze:
            self.previous_mar_values.pop(0)
