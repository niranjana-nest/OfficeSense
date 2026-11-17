
import cv2
import os
import subprocess
import imageio_ffmpeg
import tempfile
from ultralytics import YOLO

model = YOLO("yolo26n.pt")


def convert_to_mp4(input_path, output_path):
    """Convert a video into browser-friendly H.264 MP4."""

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-an",
        output_path
    ]

    subprocess.run(command, check=True, capture_output=True)


def process_video(input_path, output_path):

    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        raise ValueError("Could not open uploaded video.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    # Resize output to reduce file size
    scale = min(1, 1280 / width)
    output_width = int(width * scale)
    output_height = int(height * scale)

    # Ensure even dimensions for video encoding
    output_width -= output_width % 2
    output_height -= output_height % 2

    output_fps = max(fps / 5, 1)

    # Temporary AVI file for annotated frames
    temp_avi = output_path.replace(".mp4", "_temp.avi")

    writer = cv2.VideoWriter(
        temp_avi,
        cv2.VideoWriter_fourcc(*"XVID"),
        output_fps,
        (output_width, output_height)
    )

    if not writer.isOpened():
        raise RuntimeError("Could not create temporary video.")

    results = model.predict(
        source=input_path,
        conf=0.5,
        imgsz=640,
        vid_stride=5,
        stream=True
    )

    total_people = 0
    total_objects = 0
    processed_frames = 0

    try:
        for result in results:

            frame = result.plot()

            frame = cv2.resize(
                frame,
                (output_width, output_height)
            )

            writer.write(frame)

            classes = result.boxes.cls.tolist()

            total_people += sum(
                1 for c in classes if int(c) == 0
            )
            total_objects += len(classes)
            processed_frames += 1

    finally:
        writer.release()

    try:
        # Convert annotated video to H.264 MP4
        convert_to_mp4(temp_avi, output_path)
    finally:
        if os.path.exists(temp_avi):
            os.remove(temp_avi)

    return {
        "frames": processed_frames,
        "people": total_people,
        "objects": total_objects
    }
