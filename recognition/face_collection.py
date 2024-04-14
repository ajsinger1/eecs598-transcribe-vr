from collections import deque
from typing import List, Optional
from utils import Coordinates, distance
from cv import FaceClassifier

class Face:
    def __init__(self, coordinates: Coordinates, mar_deque_length: int, talk_threshold: float):
        self.coordinates: Coordinates = coordinates
        self.prev_mar: int = None
        self.diffs: deque = deque([0] * mar_deque_length)
        self.talk_score: float = 0
        self.scaled_talk_threshold = mar_deque_length * talk_threshold

    def update_coordinates(self, coordinates: Coordinates) -> None:
        self.coordinates = coordinates

    def push_mar(self, mar) -> None:
        if not self.prev_mar:
            self.prev_mar = mar
            return
        self.talk_score -= self.diffs.popleft()
        current_diff = abs(mar - self.prev_mar)
        self.talk_score += current_diff
        self.diffs.append(current_diff)
        self.prev_mar = mar
    
    def is_talking(self) -> bool:
        return self.talk_score > self.scaled_talk_threshold


class FaceCollection:
    def __init__(self, mar_deque_length: int, talk_threshold: float) -> None:
        self.faces: List[Face] = []
        self.mar_deque_length = mar_deque_length
        self.talk_threshold = talk_threshold
        self.classifier = FaceClassifier()
    
    def update(self, video_frame) -> None:
        face_coordinates = self.classifier.detect_face_coordinates(video_frame)
        self._update_faces(face_coordinates)
        for face in self.faces:
            mar = self.classifier.detect_mar(video_frame, face.coordinates)
            face.push_mar(mar)
    
    def get_speaker(self) -> Optional[Face]:
        if len(self.faces) == 0:
            return None
        return max(self.faces, key=lambda face: face.talk_score)

    def _update_faces(self, coordinates: List[Coordinates]) -> None:
        distances = []
        for updated_center in [coord.center() for coord in coordinates]:
            this_dists = []
            for face in self.faces:
                old_center = face.coordinates.center()
                this_dists.append(distance(updated_center, old_center))
            distances.append(this_dists)

        faces_not_chosen = set(self.faces)
        coords_not_chosen = set(range(len(coordinates)))
        while len(coords_not_chosen) > 0 and len(faces_not_chosen) > 0:
            mins = []
            for coord_idx in range(len(coordinates)):
                if coord_idx not in coords_not_chosen:
                    mins.append((float("inf"), -1))
                    continue
                face_idx, min_dist = min(
                    enumerate(distances[coord_idx]),
                    key=lambda i: (
                        i[1] if self.faces[i[0]] in faces_not_chosen else float("inf")
                    ),
                )
                mins.append((min_dist, face_idx))

            coord_idx, (_, face_idx) = min(enumerate(mins), key=lambda i: i[1][0])

            assert self.faces[face_idx] in faces_not_chosen

            faces_not_chosen.remove(self.faces[face_idx])
            coords_not_chosen.remove(coord_idx)
            self.faces[face_idx].update_coordinates(coordinates[coord_idx])

        for coord_idx in coords_not_chosen:
            self.faces.append(Face(coordinates[coord_idx], self.mar_deque_length, self.talk_threshold))

        for face in faces_not_chosen:
            self.faces.remove(face)
