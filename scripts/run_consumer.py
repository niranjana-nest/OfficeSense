import os
import uuid
from datetime import datetime

from officesense.inference.registry import ModelRegistry
from officesense.ingestion.redis_stream import (
    acknowledge_frame,
    get_redis_client,
    read_frames,
)
from officesense.rules.crowding import CrowdingRule
from officesense.storage.database import (
    create_mongo_client,
    create_ttl_index,
    get_database,
    save_frame_result,
)

MODEL_PATH = os.getenv("MODEL_PATH", "yolo26n.pt")
CONFIDENCE = float(os.getenv("CONFIDENCE", "0.25"))

MAX_PEOPLE = int(os.getenv("MAX_PEOPLE", "6"))
MIN_DURATION_S = float(os.getenv("MIN_DURATION_S", "8"))


def main():
    redis_client = get_redis_client()
    consumer_name = f"worker-{uuid.uuid4().hex[:8]}"

    registry = ModelRegistry()
    detector = registry.load(
        "person_detector",
        model_path=MODEL_PATH,
        confidence=CONFIDENCE
    )

    crowding_rule = CrowdingRule(
        max_people=MAX_PEOPLE,
        min_duration_s=MIN_DURATION_S
    )

    mongo_client = create_mongo_client()
    db = get_database(mongo_client)

    create_ttl_index(db)

    processed = 0
    total_people = 0
    events_created = 0

    print(f"Consumer started: {consumer_name}")
    print(f"Model: {MODEL_PATH}")
    print(f"Confidence: {CONFIDENCE}")
    print(f"Crowding limit: {MAX_PEOPLE}")
    print(f"Crowding duration: {MIN_DURATION_S}s")
    print("Waiting for Redis messages...\n")

    try:
        for message_id, frame_data in read_frames(
            redis_client, consumer_name
        ):
            detections = detector.process(frame_data["frame"])
            people_count = len(detections)

            event_ts = datetime.fromisoformat(frame_data["ts"])

            event = crowding_rule.evaluate(
                camera_id=frame_data["camera_id"],
                people_count=people_count,
                video_time_s=frame_data["video_time_s"],
                event_ts=event_ts
            )

            frame_result = {
                "camera_id": frame_data["camera_id"],
                "ts": event_ts,
                "frame_no": frame_data["frame_no"],
                "models": {
                    "person_detector": detector.model_name
                },
                "people_count": people_count,
                "detections": detections
            }

            save_frame_result(db, frame_result)

            if event is not None:
                db["events"].insert_one(event)
                events_created += 1

                print("\n*** CROWDING EVENT CREATED ***")
                print(f"Camera: {event['camera_id']}")
                print(f"People: {event['details']['count']}")
                print(
                    f"Duration: "
                    f"{event['details']['duration_s']} seconds"
                )
                print("Stored in MongoDB events collection.\n")

            acknowledge_frame(redis_client, message_id)

            processed += 1
            total_people += people_count

            print(
                f"Frame {frame_data['frame_no']} | "
                f"Video time: {frame_data['video_time_s']:.1f}s | "
                f"People: {people_count} | "
                f"Stored in MongoDB"
            )

    except KeyboardInterrupt:
        print("\nConsumer stopped.")

    finally:
        redis_client.close()
        mongo_client.close()

        print(f"\nFrames processed: {processed}")
        print(f"Total detections: {total_people}")
        print(f"Crowding events created: {events_created}")


if __name__ == "__main__":
    main()
