
from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np

from officesense.inference.plugins import person_detector


def test_person_detector_initializes_model(monkeypatch):
    fake_model = MagicMock()

    def fake_yolo(model_path):
        assert model_path == "yolo26n.pt"
        return fake_model

    monkeypatch.setattr(person_detector, "YOLO", fake_yolo)

    detector = person_detector.PersonDetector(
        model_path="yolo26n.pt",
        confidence=0.4
    )

    assert detector.model is fake_model
    assert detector.confidence == 0.4
    assert detector.model_name == "yolo26n"


def test_process_returns_structured_detections(monkeypatch):
    fake_model = MagicMock()

    fake_box = SimpleNamespace(
        xyxy=np.array([[10.8, 20.2, 100.9, 200.7]]),
        conf=np.array([0.98765])
    )

    fake_model.predict.return_value = [
        SimpleNamespace(boxes=[fake_box])
    ]

    monkeypatch.setattr(
        person_detector,
        "YOLO",
        lambda model_path: fake_model
    )

    detector = person_detector.PersonDetector()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    detections = detector.process(frame)

    assert detections == [
        {
            "bbox": [10, 20, 100, 200],
            "conf": 0.9877
        }
    ]

    fake_model.predict.assert_called_once_with(
        source=frame,
        conf=0.25,
        classes=[0],
        verbose=False
    )


def test_process_skips_results_without_boxes(monkeypatch):
    fake_model = MagicMock()
    fake_model.predict.return_value = [
        SimpleNamespace(boxes=None)
    ]

    monkeypatch.setattr(
        person_detector,
        "YOLO",
        lambda model_path: fake_model
    )

    detector = person_detector.PersonDetector()

    detections = detector.process(
        np.zeros((480, 640, 3), dtype=np.uint8)
    )

    assert detections == []


def test_process_returns_empty_list_when_no_results(monkeypatch):
    fake_model = MagicMock()
    fake_model.predict.return_value = []

    monkeypatch.setattr(
        person_detector,
        "YOLO",
        lambda model_path: fake_model
    )

    detector = person_detector.PersonDetector()

    detections = detector.process(
        np.zeros((480, 640, 3), dtype=np.uint8)
    )

    assert detections == []
