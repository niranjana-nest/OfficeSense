import os

import redis
import cv2
import numpy as np


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

STREAM_NAME = "officesense:frames:v4"
GROUP_NAME = "officesense:inference-group-v4"


def get_redis_client():
    """Connect to Redis."""

    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=False
    )

    client.ping()
    return client


def publish_frame(client, frame_data):
    success, encoded_frame = cv2.imencode(
        ".jpg",
        frame_data["frame"],
        [cv2.IMWRITE_JPEG_QUALITY, 85]
    )

    if not success:
        raise RuntimeError("Could not encode video frame")

    message = {
        "camera_id": frame_data["camera_id"],
        "ts": frame_data["ts"],
        "frame_no": str(frame_data["frame_no"]),
        "video_time_s": str(frame_data["video_time_s"]),
        "frame": encoded_frame.tobytes()
    }

    return client.xadd(
        STREAM_NAME,
        message,
        maxlen=1000,
        approximate=True
    )


def create_consumer_group(client):
    """Create the consumer group if it does not already exist."""

    try:
        client.xgroup_create(
            STREAM_NAME,
            GROUP_NAME,
            id="0-0",
            mkstream=True
        )
        print(f"Created Redis consumer group: {GROUP_NAME}")

    except redis.exceptions.ResponseError as error:
        if "BUSYGROUP" in str(error):
            print(f"Using existing consumer group: {GROUP_NAME}")
        else:
            raise


def decode_message(fields):
    frame_array = np.frombuffer(
        fields[b"frame"],
        dtype=np.uint8
    )

    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

    if frame is None:
        raise RuntimeError("Could not decode Redis frame")

    return {
        "camera_id": fields[b"camera_id"].decode(),
        "ts": fields[b"ts"].decode(),
        "frame_no": int(fields[b"frame_no"]),
        "video_time_s": float(fields[b"video_time_s"]),
        "frame": frame
    }


def read_frames(client, consumer_name):
    """
    Read frames through a consumer group.

    First attempts to recover messages that have been
    pending for at least 60 seconds. Then reads new messages.
    """

    create_consumer_group(client)

    while True:

        # Recover abandoned messages
        next_id, pending_messages, deleted_ids = client.xautoclaim(
            STREAM_NAME,
            GROUP_NAME,
            consumer_name,
            min_idle_time=60000,
            start_id="0-0",
            count=10
        )

        for message_id, fields in pending_messages:
            yield message_id, decode_message(fields)

        # Read new messages
        messages = client.xreadgroup(
            GROUP_NAME,
            consumer_name,
            {STREAM_NAME: ">"},
            count=1,
            block=1000
        )

        if not messages:
            continue

        for stream, entries in messages:
            for message_id, fields in entries:
                yield message_id, decode_message(fields)


def acknowledge_frame(client, message_id):
    """Acknowledge a message after successful processing."""

    return client.xack(
        STREAM_NAME,
        GROUP_NAME,
        message_id
    )
