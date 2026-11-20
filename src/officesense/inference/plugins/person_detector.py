from ultralytics import YOLO


class PersonDetector:
    """YOLO plug-in for detecting people in video frames."""

    def __init__(self, model_path="yolo26n.pt", confidence=0.25):
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.model_name = "yolo26n"

    def process(self, frame):
        """Run person detection and return structured detections."""

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            classes=[0],
            verbose=False
        )

        detections = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                coordinates = box.xyxy[0].tolist()

                detection = {
                    "bbox": [int(value) for value in coordinates],
                    "conf": round(float(box.conf[0]), 4)
                }

                detections.append(detection)

        return detections
