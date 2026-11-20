
import os

import cv2
from ultralytics import YOLO

# Configuration
INPUT_VIDEO = r"C:/Users/niranjana.balachandr/officesense/data/videos/office_video2.mp4"
OUTPUT_VIDEO = r"C:/Users/niranjana.balachandr/officesense/outputs/annotated_output.mp4"
MODEL_PATH = r"C:/Users/niranjana.balachandr/officesense/yolo26n.pt"

CONFIDENCE = 0.25
IMAGE_SIZE = 960
FRAME_STRIDE = 2
OUTPUT_WIDTH = 1920

print("Loading YOLO model...")
model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(INPUT_VIDEO)

if not cap.isOpened():
    raise ValueError(f"Could not open video: {INPUT_VIDEO}")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Calculate output dimensions while preserving aspect ratio
scale = min(1, OUTPUT_WIDTH / width)
output_width = int(width * scale)
output_height = int(height * scale)

# Ensure dimensions are even
output_width -= output_width % 2
output_height -= output_height % 2

output_fps = fps / FRAME_STRIDE

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

out = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    output_fps,
    (output_width, output_height)
)

if not out.isOpened():
    cap.release()
    raise RuntimeError("Could not create output video.")

print("Processing video...")

frame_count = 0
processed_frames = 0

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        # Process every second frame
        if (frame_count - 1) % FRAME_STRIDE != 0:
            continue

        resized_frame = cv2.resize(
            frame,
            (output_width, output_height),
            interpolation=cv2.INTER_AREA
        )

        results = model.predict(
            source=resized_frame,
            conf=CONFIDENCE,
            imgsz=IMAGE_SIZE,
            classes=[0],
            verbose=False
        )

        annotated_frame = results[0].plot()
        out.write(annotated_frame)

        processed_frames += 1

        if processed_frames % 20 == 0:
            print(
                f"Processed {frame_count}/{total_frames} "
                f"source frames"
            )

finally:
    cap.release()
    out.release()

print("\nVideo processing complete!")
print(f"Frames processed: {processed_frames}")
print(f"Output saved: {os.path.abspath(OUTPUT_VIDEO)}")
