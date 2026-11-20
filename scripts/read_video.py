import sys

import cv2

video = cv2.VideoCapture("office_video.mp4")

if not video.isOpened():
    print("Could not open video!")
    sys.exit()

# Read one frame
ret, frame = video.read()

if ret:
    print("Frame captured successfully!")
    print("Frame dimensions:", frame.shape)

    # Save the frame as an image
    cv2.imwrite("first_frame.jpg", frame)
else:
    print("Could not read frame!")

video.release()
