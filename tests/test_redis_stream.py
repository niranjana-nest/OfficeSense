from itertools import islice

import numpy as np
import pytest
import redis

from officesense.ingestion import redis_stream


def test_get_redis_client_connects(monkeypatch):
    class FakeRedis:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def ping(self):
            return True

    monkeypatch.setattr(redis_stream.redis, "Redis", FakeRedis)

    client = redis_stream.get_redis_client()

    assert client.kwargs["decode_responses"] is False


def test_publish_frame_encodes_and_publishes():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)

    frame_data = {
        "camera_id": "camera-01",
        "ts": "2026-11-20T10:00:00+00:00",
        "frame_no": 25,
        "video_time_s": 1.0,
        "frame": frame
    }

    class FakeRedis:
        def xadd(self, stream, message, **kwargs):
            self.stream = stream
            self.message = message
            self.options = kwargs
            return "123-0"

    client = FakeRedis()

    message_id = redis_stream.publish_frame(client, frame_data)

    assert message_id == "123-0"
    assert client.stream == redis_stream.STREAM_NAME
    assert client.message["camera_id"] == "camera-01"
    assert isinstance(client.message["frame"], bytes)
    assert client.options["maxlen"] == 1000


def test_publish_frame_raises_when_encoding_fails(monkeypatch):
    monkeypatch.setattr(
        redis_stream.cv2,
        "imencode",
        lambda *args: (False, None)
    )

    with pytest.raises(RuntimeError, match="Could not encode"):
        redis_stream.publish_frame(
            object(),
            {
                "camera_id": "camera-01",
                "ts": "2026-11-20T10:00:00+00:00",
                "frame_no": 0,
                "video_time_s": 0,
                "frame": np.zeros((10, 10, 3), dtype=np.uint8)
            }
        )


def test_decode_message_restores_metadata_and_frame():
    original_frame = np.zeros((50, 50, 3), dtype=np.uint8)

    success, encoded = redis_stream.cv2.imencode(
        ".jpg", original_frame
    )
    assert success

    fields = {
        b"camera_id": b"camera-01",
        b"ts": b"2026-11-20T10:00:00+00:00",
        b"frame_no": b"25",
        b"video_time_s": b"1.0",
        b"frame": encoded.tobytes()
    }

    result = redis_stream.decode_message(fields)

    assert result["camera_id"] == "camera-01"
    assert result["frame_no"] == 25
    assert result["video_time_s"] == 1.0
    assert result["frame"].shape == (50, 50, 3)


def test_decode_message_raises_for_invalid_image():
    fields = {
        b"camera_id": b"camera-01",
        b"ts": b"2026-11-20T10:00:00+00:00",
        b"frame_no": b"0",
        b"video_time_s": b"0",
        b"frame": b"invalid-image-data"
    }

    with pytest.raises(RuntimeError, match="Could not decode"):
        redis_stream.decode_message(fields)


def test_acknowledge_frame_calls_xack():
    class FakeRedis:
        def xack(self, stream, group, message_id):
            self.arguments = (stream, group, message_id)
            return 1

    client = FakeRedis()

    result = redis_stream.acknowledge_frame(client, "123-0")

    assert result == 1
    assert client.arguments == (
        redis_stream.STREAM_NAME,
        redis_stream.GROUP_NAME,
        "123-0"
    )


def test_create_consumer_group_handles_existing_group():
    class FakeRedis:
        def xgroup_create(self, *args, **kwargs):
            raise redis.exceptions.ResponseError(
                "BUSYGROUP Consumer Group name already exists"
            )

    # Existing group should not cause an exception.
    redis_stream.create_consumer_group(FakeRedis())


def test_create_consumer_group_propagates_other_errors():
    class FakeRedis:
        def xgroup_create(self, *args, **kwargs):
            raise redis.exceptions.ResponseError("Redis unavailable")

    with pytest.raises(redis.exceptions.ResponseError):
        redis_stream.create_consumer_group(FakeRedis())


def test_read_frames_recovers_pending_and_reads_new_messages():
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    success, encoded = redis_stream.cv2.imencode(".jpg", frame)
    assert success

    fields = {
        b"camera_id": b"camera-01",
        b"ts": b"2026-11-20T10:00:00+00:00",
        b"frame_no": b"0",
        b"video_time_s": b"0",
        b"frame": encoded.tobytes()
    }

    class FakeRedis:
        def __init__(self):
            self.pending_checked = False

        def xgroup_create(self, *args, **kwargs):
            pass

        def xautoclaim(self, *args, **kwargs):
            if not self.pending_checked:
                self.pending_checked = True
                return "0-1", [("pending-1", fields)], []

            return "0-0", [], []

        def xreadgroup(self, *args, **kwargs):
            return [
                (
                    redis_stream.STREAM_NAME,
                    [("new-1", fields)]
                )
            ]

    client = FakeRedis()

    results = list(
        islice(
            redis_stream.read_frames(client, "worker-01"),
            2
        )
    )

    assert len(results) == 2
    assert results[0][0] == "pending-1"
    assert results[1][0] == "new-1"
    assert results[0][1]["camera_id"] == "camera-01"
    assert results[1][1]["frame_no"] == 0


def test_read_frames_waits_when_no_new_messages():
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    success, encoded = redis_stream.cv2.imencode(".jpg", frame)
    assert success

    fields = {
        b"camera_id": b"camera-01",
        b"ts": b"2026-11-20T10:00:00+00:00",
        b"frame_no": b"0",
        b"video_time_s": b"0",
        b"frame": encoded.tobytes()
    }

    class FakeRedis:
        def __init__(self):
            self.read_count = 0

        def xgroup_create(self, *args, **kwargs):
            pass

        def xautoclaim(self, *args, **kwargs):
            return "0-0", [], []

        def xreadgroup(self, *args, **kwargs):
            self.read_count += 1

            if self.read_count == 1:
                return []

            return [
                (
                    redis_stream.STREAM_NAME,
                    [("new-1", fields)]
                )
            ]

    client = FakeRedis()

    results = list(
        islice(
            redis_stream.read_frames(client, "worker-01"),
            1
        )
    )

    assert len(results) == 1
    assert results[0][0] == "new-1"
    assert client.read_count == 2
