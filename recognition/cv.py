from utils import Coordinates, mouth_aspect_ratio
import cv2
import dlib
from typing import List
import numpy as np
import logging

class FaceClassifier:
    def __init__(self) -> None:
        self.classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    def detect_face_coordinates(self, video_frame) -> List[Coordinates]:
        gray_image = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
        face_numpy_coordinates = self.classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
        return [Coordinates(c) for c in face_numpy_coordinates]
    
    def detect_mar(self, video_frame, coordinates: Coordinates) -> float:
        x, y, w, h = coordinates.tup
        dlib_rect = dlib.rectangle(left=int(x), top=int(y), right=int(x+w), bottom=int(y+h))
        landmarks = self.predictor(image=cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY), box=dlib_rect)
        lip_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(48, 68)])
        cv2.polylines(video_frame, [lip_points[0:12]], isClosed=True, color=(0, 255, 0), thickness=2)

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            self._render_box(video_frame, coordinates)
            self._render_lips(video_frame, lip_points)
        
        return mouth_aspect_ratio(lip_points)
    
    def _render_box(self, video_frame, coordinates: Coordinates) -> None:
        x, y, w, h = coordinates.tup
        cv2.rectangle(video_frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
    
    def _render_lips(self, video_frame, lip_points) -> None:
        cv2.polylines(video_frame, [lip_points[0:12]], isClosed=True, color=(0, 0, 255), thickness=2)