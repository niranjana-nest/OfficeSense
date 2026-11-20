import os

from officesense.ingestion.redis_stream import get_redis_client, publish_frame
from officesense.ingestion.video_source import read_video_frames

VIDEO_PATH = os.getenv(
    "VIDEO_PATH",
    "data/videos/office_video5.mp4"
)

CAMERA_ID = os.getenv(
    "CAMERA_ID",
    "test-camera-01"
)

FRAME_STRIDE = int(os.getenv("FRAME_STRIDE", "25"))


def main():
    redis_client = get_redis_client()

    print("Connected to Redis!")
    print(f"Video: {VIDEO_PATH}")
    print(f"Camera: {CAMERA_ID}")
    print(f"Frame stride: {FRAME_STRIDE}")
    print("\nPublishing video frames...\n")

    published = 0

    try:
        for frame_data in read_video_frames(
            video_path=VIDEO_PATH,
            camera_id=CAMERA_ID,
            frame_stride=FRAME_STRIDE
        ):
            message_id = publish_frame(redis_client, frame_data)
            published += 1

            print(
                f"Published frame {frame_data['frame_no']} "
                f"| Redis ID: {message_id}"
            )

        print(f"\nPublishing complete! Frames sent: {published}")

    finally:
        redis_client.close()


if __name__ == "__main__":
    main()
