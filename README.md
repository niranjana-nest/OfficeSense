# OfficeSense
### AI Video Analytics for Office Spaces

OfficeSense is a computer vision-based video analytics system designed to analyse office environments using video-based person detection and crowding-event monitoring.

The project uses Python, OpenCV and pretrained YOLO models to process video frames, detect people and generate structured detection metadata. Redis Streams handles frame transportation, while MongoDB stores inference results and event data.

The system is being developed incrementally, with a modular architecture that supports future computer vision capabilities.

---

## Project Status

| Phase | Description | Status |
|---|---|---|
| Phase 0 | Foundations and standalone person detection | Completed |
| Phase 1 | Video ingestion, inference and crowding-event processing | Core pipeline implemented; RTSP and zone mapping pending |
| Phase 2 | Tracking, zone mapping and analytics | Planned |
| Phase 3 | Configurable rules and alerts | Planned |
| Phase 4–6 | Advanced computer vision and analytics | Planned |

## Features Implemented

### Phase 0 – Foundations

- Read recorded video files using OpenCV.
- Perform person detection using a pretrained YOLO model.
- Draw bounding boxes around detected people.
- Generate annotated output videos.
- Configure detection confidence and frame-processing settings.

### Phase 1 – Count and Store

**Video ingestion**
- Read and sample video frames.
- Capture camera identifiers, frame numbers and timestamps.
- Support configurable frame sampling.

**Redis Streams**
- Publish encoded video frames to Redis Streams.
- Transport frame metadata alongside image data.
- Implement consumer groups and message acknowledgement.
- Recover pending messages using `XAUTOCLAIM`.

**Inference**
- Implement a model plug-in registry.
- Integrate a YOLO-based person detector.
- Generate structured detection results containing bounding-box coordinates and confidence scores.

**MongoDB storage**
- Store processed frame metadata and detection results in the `frame_results` collection.
- Configure a seven-day TTL index for automatic metadata expiration.

**Crowding rule**
- Evaluate people counts against a configurable threshold.
- Detect sustained crowding conditions.
- Generate crowding events.
- Track crowding state independently for each camera.

**Containerisation**
- Use Docker and Docker Compose to run Redis, the producer and the consumer.
- Support CPU-based inference.

The Phase 1 pipeline has been successfully tested using recorded video footage.

---

## System Architecture

```text
          Recorded Video
                 |
                 v
          Video Producer
                 |
          Frame Sampling
                 |
                 v
           Redis Stream
                 |
                 v
          Inference Consumer
                 |
                 v
          Model Registry
                 |
                 v
          YOLO Person Detector
                 |
                 v
          Detection Results
                 |
                 v
              MongoDB
                 |
                 v
           Crowding Rule
                 |
                 v
          Crowding Events
```

The producer publishes sampled frames to Redis Streams. The consumer retrieves frames, executes person detection and stores the resulting metadata in MongoDB. The crowding rule evaluates detection counts and generates events when configured conditions are satisfied.

A separate standalone inference worker is also available for direct video-to-MongoDB processing.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| OpenCV | Video processing and frame extraction |
| Ultralytics YOLO | Person detection |
| NumPy | Image and frame data processing |
| Redis Streams | Frame transportation and message handling |
| MongoDB Atlas | Detection metadata and event storage |
| PyMongo | MongoDB integration |
| Docker | Containerisation |
| Docker Compose | Multi-service execution |
| pytest | Automated testing |
| pytest-cov | Test coverage measurement |
| Ruff | Static analysis and linting |
| GitHub Actions | Continuous integration |

---

## Project Structure

```text
OfficeSense/
|
|-- data/
|   |-- videos/                 # Local recorded video inputs
|
|-- assets/
|   |-- test_images/            # Test images
|
|-- outputs/                    # Generated outputs
|
|-- scripts/
|   |-- main.py                 # Phase 0 detection pipeline
|   |-- read_video.py           # Video reading utility
|   |-- run_producer.py         # Redis frame producer
|   |-- run_consumer.py         # Redis inference consumer
|   |-- check_mongodb.py        # MongoDB connection check
|   |-- check_frame_storage.py  # Frame storage check
|   |-- check_ingestion.py      # Ingestion check
|   |-- check_opencv.py         # OpenCV check
|   |-- check_yolo.py           # YOLO check
|
|-- src/
|   |-- officesense/
|       |-- ingestion/
|       |   |-- video_source.py
|       |   |-- redis_stream.py
|       |
|       |-- inference/
|       |   |-- worker.py
|       |   |-- registry.py
|       |   |-- plugins/
|       |       |-- person_detector.py
|       |
|       |-- storage/
|       |   |-- database.py
|       |
|       |-- rules/
|           |-- crowding.py
|
|-- tests/
|   |-- test_crowding.py
|   |-- test_database.py
|   |-- test_person_detector.py
|   |-- test_redis_stream.py
|   |-- test_registry.py
|   |-- test_video_source.py
|   |-- test_worker.py
|
|-- docs/
|   |-- technical-progress-report.md
|
|-- .github/
|   |-- workflows/
|       |-- ci.yml
|
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- pyproject.toml
|-- .gitignore
|-- README.md
```

---

## Installation and Setup

### Prerequisites

- Python 3.12 or later
- Git
- Docker Desktop
- Docker Compose
- MongoDB Atlas account or an accessible MongoDB deployment

### 1. Clone the repository

```bash
git clone https://github.com/niranjana-nest/OfficeSense.git
cd OfficeSense
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

For development and testing:

```bash
pip install pytest pytest-cov ruff
```

### 4. Configure environment variables

Create a `.env` file in the project root.

Configure the MongoDB connection string:

```env
MONGODB_URI=your_mongodb_connection_string
```

Keep credentials private. The `.env` file is excluded from Git tracking.

### 5. Add model weights and test videos

Place the YOLO model weights and recorded test videos in their expected local project directories.

For example:

- `yolo26n.pt`
- `data/videos/office_video2.mp4`

Model weights and video files are excluded from Git tracking.

---

## Running the Application

### Docker-based Phase 1 pipeline

Ensure Docker Desktop is running and the environment is configured.

Build and start the services:

```bash
docker compose up --build -d
```

Inspect running services:

```bash
docker compose ps
```

View consumer logs:

```bash
docker compose logs -f consumer
```

View producer logs:

```bash
docker compose logs producer
```

Stop the services:

```bash
docker compose down
```

The Docker-based pipeline currently uses recorded video footage for development and integration testing.

### Phase 0 standalone detection

The standalone detection script is located at:

```text
scripts/main.py
```

It processes recorded video and generates an annotated output video using the configured detection settings.

---

## Testing

OfficeSense uses pytest for automated testing.

Run the complete test suite:

```bash
python -m pytest -v
```

Run tests with coverage:

```bash
python -m pytest --cov=officesense --cov-report=term-missing
```

Enforce the minimum coverage threshold:

```bash
python -m pytest --cov=officesense --cov-report=term-missing --cov-fail-under=95
```

### Current Test Results

| Metric | Result |
|---|---:|
| Automated tests | 35 |
| Passed | 35 |
| Failed | 0 |
| Statement coverage | 99.42% |

### Static Analysis

Run Ruff:

```bash
ruff check src/ tests/ scripts/
```

**Latest verified result:** All checks passed with zero findings.

---

## Continuous Integration

OfficeSense uses GitHub Actions for automated quality checks.

Workflow configuration:

```text
.github/workflows/ci.yml
```

The CI workflow runs on pushes to `main` and pull requests targeting `main`.

The pipeline performs:

1. Repository checkout.
2. Python environment setup.
3. Dependency installation.
4. Ruff static analysis.
5. Automated pytest execution.
6. Coverage threshold validation.

**Latest verified CI result:** Successful.

The workflow was tested using Ubuntu and Python 3.12, with a minimum coverage requirement of 95%.

[View GitHub Actions](https://github.com/niranjana-nest/OfficeSense/actions)

---

## Current Limitations

The following capabilities remain outstanding:

- Live RTSP camera integration and automatic reconnection.
- Actual polygon-based zone mapping.
- People counting per configured zone.
- Validation against hand-labelled ground-truth video results.
- Further end-to-end latency and performance testing.

The current crowding implementation uses a camera-view placeholder rather than actual geometric zone identification.

The existing integration tests use recorded video footage, not live office camera streams.

---

## Future Development

Planned development includes:

- Live RTSP video ingestion.
- Multi-camera processing.
- Object tracking and zone mapping.
- Time-series occupancy analytics.
- Configurable crowding rules.
- Alert and notification integration.
- Additional computer vision plug-ins.
- Advanced analytics and performance optimisation.

---

## Privacy and Security

OfficeSense is intended for office video analytics. Before connecting real office cameras, the required legal and HR approvals, employee notifications and data-retention arrangements must be confirmed.

The project follows a metadata-oriented processing approach. Raw video is not intended to be stored in MongoDB.

MongoDB credentials are configured through environment variables and excluded from version control.

---

**OfficeSense - Building an incremental AI-powered video analytics pipeline for office spaces.**
