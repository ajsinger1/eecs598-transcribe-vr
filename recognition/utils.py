import numpy as np
from typing import Tuple

class Coordinates:
    def __init__(self, coordinates):
        self.x: int
        self.y: int
        self.w: int
        self.h: int
        self.x, self.y, self.w, self.h = coordinates
        self.tup: Tuple[int, int, int, int] = coordinates

    def center(self):
        return (self.x + 0.5 * self.w, self.y + 0.5 * self.h)

def mouth_aspect_ratio(mouth_points):
    A = np.linalg.norm(mouth_points[2] - mouth_points[10])  # Distance between 51 - 59
    B = np.linalg.norm(mouth_points[4] - mouth_points[8])   # Distance between 53 - 57
    # C = np.linalg.norm(mouth_points[0] - mouth_points[6])   # Distance between 49 - 55
    # mar = (A + B) / (2.0 * C)
    mar = A + B
    return mar

def distance(point1: tuple, point2: tuple):
    return (point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2
