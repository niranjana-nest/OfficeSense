import cv2
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def read_video_frames(video_path, camera_id, frame_stride=25):
    video_path = Path(video_path)

    if not video_path.is_absolute():
        video_path = PROJECT_ROOT / video_path

    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        cap.release()
        raise RuntimeError("Could not determine video FPS")

    frame_no = 0
    session_start = datetime.now(timezone.utc)

    try:
        while True:
            success, frame = cap.read()

            if not success:
                break

            if frame_no % frame_stride == 0:
                video_time_s = frame_no / fps

                frame_data = {
                    "camera_id": camera_id,
                    "ts": (
                        session_start
                        + __import__("datetime").timedelta(
                            seconds=video_time_s
                        )
                    ).isoformat(timespec="milliseconds"),
                    "frame_no": frame_no,
                    "video_time_s": video_time_s,
                    "frame": frame
                }

                yield frame_data

            frame_no += 1

    finally:
        cap.release()
