#!/usr/bin/env python3
import numpy as np
import dlib
import cv2
from collections import deque
from typing import List, Tuple

DEBUG = True
MAR_DEQUE_LENGTH = 10
TALK_THRESHOLD = 0.05
SCALED_TALK_THRESHOLD = MAR_DEQUE_LENGTH * TALK_THRESHOLD

# initialize the face classifier and the facial landmarks predictor
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# start video capture
video_capture = cv2.VideoCapture(0)


class Coordinates:
        def __init__(self, coordinates):
            self.x: int
            self.y: int
            self.w: int
            self.h: int
            self.x, self.y, self.w, self.h = coordinates
            self.tup: Tuple[int, int, int, int] = coordinates
            
        def center(self):
            return (self.x + 0.5*self.w, self.y + 0.5*self.h)
        
class Face:
    def __init__(self, coordinates: Coordinates):
        # New face
        self.coordinates: Coordinates = coordinates
        self.prev_mar: int = None
        self.diffs: deque = deque([0]*MAR_DEQUE_LENGTH)
        self.talk_score: float = 0

    def update_coordinates(self, coordinates: Coordinates):
        self.coordinates = coordinates
    
    def push_mar(self, mar):
        if not self.prev_mar:
            self.prev_mar = mar
            return
        self.talk_score -= (self.diffs.popleft()) 
        current_diff = abs(mar - self.prev_mar)
        self.talk_score += current_diff 
        self.diffs.append(current_diff)
        self.prev_mar = mar

def dist(point1: tuple, point2: tuple):
    return (point2[0] - point1[0])**2 + (point2[1] - point1[1])**2
    

class FaceCollection:
    def __init__(self):
        self.faces: List[Face] = []

    
    def update_faces(self, coordinates: List[Coordinates]):
        distances = []
        for updated_center in [coord.center() for coord in coordinates]:
            this_dists = []
            for face in self.faces: 
                old_center = face.coordinates.center()
                this_dists.append(dist(updated_center, old_center))
            distances.append(this_dists)
        
        faces_not_chosen = set(self.faces)
        coords_not_chosen = set([i for i in range(len(coordinates))])
        while len(coords_not_chosen) > 0 and len(faces_not_chosen) > 0:
            mins = []
            for coord_idx in range(len(coordinates)):
                if coord_idx not in coords_not_chosen:
                    mins.append((float('inf'), -1))
                    continue
                face_idx, min_dist  = min(enumerate(distances[coord_idx]), key=lambda i: i[1] if self.faces[i[0]] in faces_not_chosen else float('inf'))
                mins.append((min_dist, face_idx))

            coord_idx, (_, face_idx) = min(enumerate(mins), key= lambda i: i[1][0])

            assert(self.faces[face_idx] in faces_not_chosen)

            faces_not_chosen.remove(self.faces[face_idx])
            coords_not_chosen.remove(coord_idx)
            self.faces[face_idx].update_coordinates(coordinates[coord_idx])

        for coord_idx in coords_not_chosen:
            self.faces.append(Face(coordinates[coord_idx]))
        
        for face in faces_not_chosen:
            self.faces.remove(face)

        

    # more functions to make this iterable

face_collection = FaceCollection()



# everything below is old 
# everything above is new method


# draw bounding boxes around detected faces
def detect_bounding_box(vid) -> List[Coordinates]:
    gray_image = cv2.cvtColor(vid, cv2.COLOR_BGR2GRAY)
    face_numpy_coordinates = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
    return [Coordinates(c) for c in face_numpy_coordinates]

# calculate the Mouth Aspect Ratio (MAR)
def mouth_aspect_ratio(mouth_points):
    A = np.linalg.norm(mouth_points[2] - mouth_points[10])  # Distance between 51 - 59
    B = np.linalg.norm(mouth_points[4] - mouth_points[8])   # Distance between 53 - 57
    C = np.linalg.norm(mouth_points[0] - mouth_points[6])   # Distance between 49 - 55
    mar = (A + B) / (2.0 * C)
    return mar


# detect lip movement and highlight speaking
def update_face_mars(video_frame):
    for face in face_collection.faces:
        x, y, w, h = face.coordinates.tup
        dlib_rect = dlib.rectangle(left=int(x), top=int(y), right=int(x+w), bottom=int(y+h))
        landmarks = predictor(image=cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY), box=dlib_rect)
        lip_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(48, 68)])
        cv2.polylines(video_frame, [lip_points[0:12]], isClosed=True, color=(0, 255, 0), thickness=2)
        
        mar = mouth_aspect_ratio(lip_points)
        if DEBUG:
            render_lips(video_frame, lip_points)
            render_box(video_frame, x, y, w, h)
        face.push_mar(mar)
        
def render_lips(video_frame, lip_points):
     cv2.polylines(video_frame, [lip_points[0:12]], isClosed=True, color=(0, 0, 255), thickness=2)

def render_box(video_frame, x, y, w, h):
    cv2.rectangle(video_frame, (x, y), (x + w, y + h), (0, 255, 0), 4)


def render_talking(video_frame):
     if len(face_collection.faces) > 0:
        face = max(face_collection.faces, key=lambda face: face.talk_score)
        print(face.talk_score)
        cv2.putText(video_frame, "Talking" if face.talk_score > SCALED_TALK_THRESHOLD else "Not Taking", (face.coordinates.x, face.coordinates.y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        


# Main loop
while True:
    result, video_frame = video_capture.read()
    if not result:
        break

    face_collection.update_faces(detect_bounding_box(video_frame))
    update_face_mars(video_frame)
    render_talking(video_frame)
    cv2.imshow("My Face Detection Project", video_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
