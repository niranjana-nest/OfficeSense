import cv2

video = cv2.VideoCapture("office_video.mp4")

if not video.isOpened():
    print("Could not open video!")
    exit()

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

# import cv2

# video = cv2.VideoCapture("office_video.mp4")

# if not video.isOpened():
#     print("Could not open video!")
#     exit()

# print("Video opened successfully!")

# while True:
#     ret, frame = video.read()

#     if not ret:
#         break

#     # Resize frame for easier viewing
#     resized = cv2.resize(frame, (960, 540))

#     # Display the frame
#     cv2.imshow("OfficeSense - Video Preview", resized)

#     # Wait 40 milliseconds between frames
#     if cv2.waitKey(40) & 0xFF == ord('q'):
#         break

# video.release()
# cv2.destroyAllWindows()

# print("Video processing finished!")
