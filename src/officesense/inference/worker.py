from datetime import datetime

from officesense.inference.registry import ModelRegistry
from officesense.ingestion.video_source import read_video_frames
from officesense.storage.database import (
    create_mongo_client,
    get_database,
    save_frame_result,
)


def run_inference(video_path, camera_id):
    """Process sampled video frames and store their detections."""

    # Load the enabled model plug-in
    registry = ModelRegistry()

    detector = registry.load(
        "person_detector",
        model_path="yolo26n.pt",
        confidence=0.25
    )

    # Connect to MongoDB
    client = create_mongo_client()
    db = get_database(client)

    processed_frames = 0
    total_people = 0

    try:
        # Receive frames from the ingestion service
        for frame_data in read_video_frames(
            video_path=video_path,
            camera_id=camera_id,
            frame_stride=25
        ):
            frame = frame_data["frame"]

            # Run person detection
            detections = detector.process(frame)

            # Convert timestamp string into a datetime object
            timestamp = datetime.fromisoformat(
                frame_data["ts"]
            )

            # Prepare the MongoDB document
            frame_result = {
                "camera_id": frame_data["camera_id"],
                "ts": timestamp,
                "frame_no": frame_data["frame_no"],
                "models": {
                    "person_detector": detector.model_name
                },
                "detections": detections
            }

            # Store the result
            save_frame_result(db, frame_result)

            processed_frames += 1
            total_people += len(detections)

            print(
                f"Frame {frame_data['frame_no']} | "
                f"People detected: {len(detections)} | "
                f"Stored in MongoDB"
            )

        print("\nInference completed!")
        print(f"Frames processed: {processed_frames}")
        print(f"Total detections across frames: {total_people}")

    finally:
        client.close()


if __name__ == "__main__":
    run_inference(
        video_path="data/videos/office_video2.mp4",
        camera_id="test-camera-01"
    )
