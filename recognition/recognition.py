import cv2
import dlib
import numpy as np
from lip_movement_detector import LipMovementDetector

# Initialize the face detector and facial landmarks predictor
face_detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Initialize the video capture
video_capture = cv2.VideoCapture(1)

# Initialize the lip movement detector
lip_detector = LipMovementDetector(dynamic_threshold_factor=1, num_frames_to_analyze=3)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    if not ret:
        break

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the grayscale frame
    faces = face_detector(gray, 0)

    for face in faces:
        # Get the landmarks/parts for the face in box
        landmarks = predictor(gray, face)
        
        # Calculate the MAR for the detected face
        mar = lip_detector.calculate_mar(landmarks)
        
        # Update the baseline MAR if needed and add the current MAR to the detector
        lip_detector.update_baseline(mar)
        lip_detector.add_mar_value(mar)

        # Determine if the person is talking
        talking = lip_detector.is_talking(mar)

        # Draw a rectangle around the face and indicate if talking
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, "Talking" if talking else "Not Talking", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if talking else (0, 0, 255), 2)

    # Display the resulting frame
    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
video_capture.release()
cv2.destroyAllWindows()
