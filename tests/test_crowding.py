
from datetime import datetime, timezone

from officesense.rules.crowding import CrowdingRule


def test_no_event_when_people_count_is_below_limit():
    rule = CrowdingRule(max_people=5, min_duration_s=8)

    event = rule.evaluate(
        camera_id="camera-01",
        people_count=5,
        video_time_s=0,
        event_ts=datetime.now(timezone.utc)
    )

    assert event is None


def test_crowding_event_triggers_after_required_duration():
    rule = CrowdingRule(max_people=6, min_duration_s=8)

    timestamp = datetime.now(timezone.utc)

    rule.evaluate("camera-01", 7, 0, timestamp)

    event = rule.evaluate("camera-01", 7, 4, timestamp)

    assert event is None

    event = rule.evaluate("camera-01", 7, 8, timestamp)

    assert event is not None
    assert event["camera_id"] == "camera-01"
    assert event["severity"] == "warning"
    assert event["details"]["duration_s"] == 8


def test_no_duplicate_event_while_crowding_continues():
    rule = CrowdingRule(max_people=6, min_duration_s=8)

    timestamp = datetime.now(timezone.utc)

    rule.evaluate("camera-01", 7, 0, timestamp)
    rule.evaluate("camera-01", 7, 8, timestamp)

    event = rule.evaluate("camera-01", 9, 10, timestamp)

    assert event is None


def test_crowding_state_resets_when_count_returns_to_limit():
    rule = CrowdingRule(max_people=6, min_duration_s=8)

    timestamp = datetime.now(timezone.utc)

    rule.evaluate("camera-01", 7, 0, timestamp)
    rule.evaluate("camera-01", 6, 4, timestamp)

    event = rule.evaluate("camera-01", 7, 8, timestamp)

    assert event is None


def test_cameras_are_tracked_independently():
    rule = CrowdingRule(max_people=6, min_duration_s=8)

    timestamp = datetime.now(timezone.utc)

    rule.evaluate("camera-01", 7, 0, timestamp)
    rule.evaluate("camera-02", 7, 0, timestamp)

    event = rule.evaluate("camera-01", 7, 8, timestamp)

    assert event is not None
    assert event["camera_id"] == "camera-01"

    other_event = rule.evaluate("camera-02", 7, 4, timestamp)

    assert other_event is None
