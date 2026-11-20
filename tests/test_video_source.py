
from datetime import datetime

import pytest

from officesense.ingestion import video_source


class FakeVideoCapture:
    def __init__(self, frames, fps=2, opened=True):
        self.frames = iter(frames)
        self.fps = fps
        self.opened = opened
        self.released = False

    def isOpened(self):
        return self.opened

    def get(self, property_id):
        return self.fps

    def read(self):
        try:
            return True, next(self.frames)
        except StopIteration:
            return False, None

    def release(self):
        self.released = True


def test_samples_frames_using_configured_stride(tmp_path, monkeypatch):
    video_file = tmp_path / "test.mp4"
    video_file.touch()

    fake_capture = FakeVideoCapture(
        frames=["frame0", "frame1", "frame2", "frame3", "frame4"]
    )

    monkeypatch.setattr(
        video_source.cv2,
        "VideoCapture",
        lambda path: fake_capture
    )

    results = list(
        video_source.read_video_frames(
            video_path=video_file,
            camera_id="camera-01",
            frame_stride=2
        )
    )

    assert [item["frame_no"] for item in results] == [0, 2, 4]
    assert [item["frame"] for item in results] == [
        "frame0", "frame2", "frame4"
    ]
    assert fake_capture.released is True


def test_frame_metadata_is_generated_correctly(tmp_path, monkeypatch):
    video_file = tmp_path / "test.mp4"
    video_file.touch()

    fake_capture = FakeVideoCapture(
        frames=["frame0", "frame1", "frame2"],
        fps=2
    )

    monkeypatch.setattr(
        video_source.cv2,
        "VideoCapture",
        lambda path: fake_capture
    )

    results = list(
        video_source.read_video_frames(
            video_path=video_file,
            camera_id="camera-01",
            frame_stride=1
        )
    )

    assert len(results) == 3

    first_frame = results[0]
    second_frame = results[1]

    assert first_frame["camera_id"] == "camera-01"
    assert first_frame["frame_no"] == 0
    assert first_frame["video_time_s"] == 0

    assert second_frame["frame_no"] == 1
    assert second_frame["video_time_s"] == 0.5

    assert isinstance(
        datetime.fromisoformat(first_frame["ts"]),
        datetime
    )


def test_missing_video_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        list(
            video_source.read_video_frames(
                video_path="missing_video.mp4",
                camera_id="camera-01"
            )
        )


def test_unopenable_video_raises_runtime_error(tmp_path, monkeypatch):
    video_file = tmp_path / "test.mp4"
    video_file.touch()

    fake_capture = FakeVideoCapture(
        frames=[],
        opened=False
    )

    monkeypatch.setattr(
        video_source.cv2,
        "VideoCapture",
        lambda path: fake_capture
    )

    with pytest.raises(RuntimeError, match="Could not open video"):
        list(
            video_source.read_video_frames(
                video_path=video_file,
                camera_id="camera-01"
            )
        )

    assert fake_capture.released is True


def test_invalid_fps_raises_runtime_error_and_releases_capture(
    tmp_path, monkeypatch
):
    video_file = tmp_path / "test.mp4"
    video_file.touch()

    fake_capture = FakeVideoCapture(
        frames=[],
        fps=0
    )

    monkeypatch.setattr(
        video_source.cv2,
        "VideoCapture",
        lambda path: fake_capture
    )

    with pytest.raises(RuntimeError, match="Could not determine video FPS"):
        list(
            video_source.read_video_frames(
                video_path=video_file,
                camera_id="camera-01"
            )
        )

    assert fake_capture.released is True
