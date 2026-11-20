
from datetime import datetime, timezone
from unittest.mock import MagicMock

import numpy as np
import pytest

from officesense.inference import worker


@pytest.fixture
def mock_worker_dependencies(monkeypatch):
    fake_detector = MagicMock()
    fake_detector.model_name = "yolo26n"

    fake_registry = MagicMock()
    fake_registry.load.return_value = fake_detector

    fake_client = MagicMock()
    fake_db = MagicMock()

    monkeypatch.setattr(
        worker,
        "ModelRegistry",
        lambda: fake_registry
    )
    monkeypatch.setattr(
        worker,
        "create_mongo_client",
        lambda: fake_client
    )
    monkeypatch.setattr(
        worker,
        "get_database",
        lambda client: fake_db
    )

    save_mock = MagicMock()
    monkeypatch.setattr(
        worker,
        "save_frame_result",
        save_mock
    )

    return {
        "detector": fake_detector,
        "registry": fake_registry,
        "client": fake_client,
        "db": fake_db,
        "save": save_mock,
        "monkeypatch": monkeypatch
    }


def make_frame_data(frame_no, timestamp):
    return {
        "camera_id": "camera-01",
        "ts": timestamp,
        "frame_no": frame_no,
        "frame": np.zeros((20, 20, 3), dtype=np.uint8)
    }


def test_run_inference_processes_and_stores_frames(
    mock_worker_dependencies
):
    mocks = mock_worker_dependencies

    timestamp = "2026-11-20T10:00:00+00:00"

    frames = [
        make_frame_data(0, timestamp),
        make_frame_data(25, timestamp)
    ]

    mocks["monkeypatch"].setattr(
        worker,
        "read_video_frames",
        lambda **kwargs: iter(frames)
    )

    mocks["detector"].process.side_effect = [
        [{"bbox": [1, 2, 10, 20], "conf": 0.95}],
        [
            {"bbox": [1, 2, 10, 20], "conf": 0.95},
            {"bbox": [5, 6, 15, 20], "conf": 0.90}
        ]
    ]

    worker.run_inference("test.mp4", "camera-01")

    assert mocks["save"].call_count == 2

    first_result = mocks["save"].call_args_list[0].args[1]

    assert first_result["camera_id"] == "camera-01"
    assert first_result["frame_no"] == 0
    assert first_result["models"]["person_detector"] == "yolo26n"
    assert isinstance(first_result["ts"], datetime)
    assert first_result["ts"].tzinfo == timezone.utc

    mocks["client"].close.assert_called_once()


def test_run_inference_handles_empty_video(
    mock_worker_dependencies
):
    mocks = mock_worker_dependencies

    mocks["monkeypatch"].setattr(
        worker,
        "read_video_frames",
        lambda **kwargs: iter([])
    )

    worker.run_inference("empty.mp4", "camera-01")

    mocks["save"].assert_not_called()
    mocks["detector"].process.assert_not_called()
    mocks["client"].close.assert_called_once()


def test_run_inference_closes_client_when_processing_fails(
    mock_worker_dependencies
):
    mocks = mock_worker_dependencies

    frame = make_frame_data(
        0,
        "2026-11-20T10:00:00+00:00"
    )

    mocks["monkeypatch"].setattr(
        worker,
        "read_video_frames",
        lambda **kwargs: iter([frame])
    )

    mocks["detector"].process.side_effect = RuntimeError(
        "Inference failed"
    )

    with pytest.raises(RuntimeError, match="Inference failed"):
        worker.run_inference("test.mp4", "camera-01")

    mocks["client"].close.assert_called_once()
    mocks["save"].assert_not_called()


def test_run_inference_uses_expected_configuration(
    mock_worker_dependencies
):
    mocks = mock_worker_dependencies

    mocks["monkeypatch"].setattr(
        worker,
        "read_video_frames",
        lambda **kwargs: iter([])
    )

    worker.run_inference("office.mp4", "camera-01")

    mocks["registry"].load.assert_called_once_with(
        "person_detector",
        model_path="yolo26n.pt",
        confidence=0.25
    )

    mocks["monkeypatch"].undo()
