from ultralytics import YOLO

model = YOLO("yolo26n.pt")

model.predict(
    source="office_video2.mp4",
    save=True,
    conf=0.25,
    imgsz=640,
    vid_stride=1,
    classes=[0]
)

print("Video processing complete!")

# from ultralytics import YOLO

# model = YOLO("yolo26n.pt")

# results = model("first_frame.jpg")

# # Draw bounding boxes on the image
# annotated_image = results[0].plot()

# # Save the image
# import cv2
# cv2.imwrite("detected_frame.jpg", annotated_image)

# print("Detection image saved!")
