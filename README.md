# OfficeSense
### AI Video Analytics for Office Spaces

OfficeSense is a computer vision project that aims to analyse office environments using video-based person detection and analytics.

The project uses Python, OpenCV and YOLO to process video footage and detect people. It is being developed incrementally, with each phase introducing new capabilities to the system.

## Tech Stack

- **Python** – Core programming language
- **OpenCV** – Video processing and frame handling
- **Ultralytics YOLO** – Pretrained object detection model
- **Git & GitHub** – Version control

## Project Structure

```text
OfficeSense/
├── main.py
├── test_yolo.py
├── test_opencv.py
├── read_video.py
├── video_processor.py
├── app.py
├── templates/
├── .gitignore
└── README.md
```

## Phase 0 – Foundations (Completed)

The first phase focused on running a pretrained person-detection model on recorded office video.

### Implemented Features

- Read recorded video files frame by frame using OpenCV.
- Perform person detection using a pretrained YOLO model.
- Draw bounding boxes around detected people.
- Generate an annotated output video.
- Experiment with detection confidence and video-processing settings.

### Running the Project

**1. Clone the repository**

```bash
git clone https://github.com/niranjana-nest/OfficeSense.git
cd OfficeSense
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

**3. Activate the virtual environment**

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

**4. Install dependencies**

```bash
pip install opencv-python ultralytics
```

**5. Add the required files**

Place the following files in the project root:

- `yolo26n.pt` – YOLO model weights.
- `office_video2.mp4` – Input video.

These files are excluded from Git tracking.

**6. Run the detection script**

```bash
python main.py
```

The annotated video will be generated as:

```text
annotated_output.mp4
```

## Phase 1 – Count and Store (Planned)

The next phase focuses on developing a people-counting pipeline and storing detection results in MongoDB.

### Planned Components

- **Ingest Service:** Capture and sample frames from an RTSP camera.
- **Inference Worker:** Process frames using person-detection models through a plug-in registry.
- **Redis Streams:** Transfer frames and inference results between services.
- **MongoDB Writer:** Store detection metadata in MongoDB.
- **Crowding Rule:** Implement a hard-coded rule to identify crowded zones.

### Phase 1 Goal

Demonstrate live people counting from one RTSP camera, with results stored in MongoDB and a basic crowding alert.

## Project Status

| Phase | Description | Status |
|---|---|---|
| Phase 0 | Foundations and person detection | Completed |
| Phase 1 | Count and store | Planned |

---

**OfficeSense** – Building an incremental computer vision pipeline for office-space analytics.
