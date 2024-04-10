import numpy as np
import dlib
import cv2

# initialize the face classifier and the facial landmarks predictor
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# start video capture
video_capture = cv2.VideoCapture(1)

# draw bounding boxes around detected faces
def detect_bounding_box(vid):
    gray_image = cv2.cvtColor(vid, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
    for (x, y, w, h) in faces:
        cv2.rectangle(vid, (x, y), (x + w, y + h), (0, 255, 0), 4)
    return faces

# calculate the Mouth Aspect Ratio (MAR)
def mouth_aspect_ratio(mouth_points):
    A = np.linalg.norm(mouth_points[2] - mouth_points[10])  # Distance between 51 - 59
    B = np.linalg.norm(mouth_points[4] - mouth_points[8])   # Distance between 53 - 57
    C = np.linalg.norm(mouth_points[0] - mouth_points[6])   # Distance between 49 - 55
    mar = (A + B) / (2.0 * C)
    return mar

# global variables for tracking mouth movement
prev_mar = None

# detect lip movement and highlight speaking
def detect_lips_speaking(video_frame, faces):
    global prev_mar
    for (x, y, w, h) in faces:
        dlib_rect = dlib.rectangle(left=int(x), top=int(y), right=int(x+w), bottom=int(y+h))
        landmarks = predictor(image=cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY), box=dlib_rect)
        lip_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(48, 68)])
        cv2.polylines(video_frame, [lip_points[0:12]], isClosed=True, color=(0, 255, 0), thickness=2)
        
        mar = mouth_aspect_ratio(lip_points)
        
        if prev_mar is not None and abs(mar - prev_mar) > 0.1:  # Threshold for detecting speaking
            cv2.polylines(video_frame, [lip_points[0:12]], isClosed=True, color=(0, 0, 255), thickness=2)
        
        prev_mar = mar

# Main loop
while True:
    result, video_frame = video_capture.read()
    if not result:
        break

    faces = detect_bounding_box(video_frame)
    detect_lips_speaking(video_frame, faces)
    cv2.imshow("My Face Detection Project", video_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
