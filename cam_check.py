import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera not opened")
else:
    print("Camera opened successfully")

camera.release()

