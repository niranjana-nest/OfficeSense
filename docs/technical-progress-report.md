# OfficeSense – Technical Progress Report

**Project:** OfficeSense – AI Video Analytics for Office Spaces  
**Report date:** 20 November 2026  
**Current development status:** Phase 0 completed; Phase 1 core pipeline implemented and tested using recorded video.

---

## 1. Project Overview

OfficeSense is an AI-powered video analytics system designed to monitor office environments and extract useful information from camera footage.

The system uses computer vision to detect people, process sampled video frames, store analytical results, and identify conditions such as crowding.

The project is being developed incrementally, following the phases and requirements described in the OfficeSense design document.

The current implementation focuses on:

- Reading and processing video footage.
- Detecting people using a pretrained YOLO model.
- Separating video ingestion from inference using Redis Streams.
- Persisting frame-level results in MongoDB.
- Evaluating crowding conditions and generating events.
- Running the core pipeline using Docker Compose.

## 2. Phase 0 – Initial Video Processing and Detection

**Status: Completed**

### Objective

Establish a working computer vision pipeline that can read recorded office footage, detect people, annotate frames, and generate an output video.

### Implementation

A standalone Python script was developed using OpenCV and Ultralytics YOLO.

The pipeline:

1. Opens a recorded video file using OpenCV.
2. Reads frames from the video.
3. Samples frames using a configurable frame stride.
4. Runs the pretrained YOLO person detector.
5. Draws bounding boxes around detected people.
6. Writes the annotated frames into an output video.

### Technologies

- Python
- OpenCV
- Ultralytics YOLO
- PyTorch

### Outcome

The Phase 0 pipeline successfully processes recorded footage and generates an annotated output video containing detected people.

This established the initial computer vision functionality used in the later pipeline.

### Relevant files

- `scripts/main.py`
- `scripts/test_yolo.py`
- `scripts/test_opencv.py`
- `scripts/read_video.py`

---

## 3. Phase 1 – Video Ingestion, Inference and Database Storage

**Status: Core recorded-video pipeline implemented and tested. Live RTSP integration and true zone-based counting remain outstanding.**

### Objective

Develop a modular processing pipeline that ingests video frames, transports them to an inference worker, performs person detection, evaluates crowding conditions, and stores results in MongoDB.

### 3.1 Video Ingestion

The ingestion module reads video footage and extracts frames at a configurable sampling interval.

Each sampled frame is associated with metadata including:

- Camera ID
- Timestamp
- Frame number
- Video timestamp

The frame is then JPEG-encoded before being published to Redis.

**Relevant file:** `src/officesense/ingestion/video_source.py`

### 3.2 Redis Stream – Frame Transport

Redis Streams is used as the message transport layer between the producer and consumer.

The producer publishes sampled frames to a Redis Stream. The consumer retrieves these messages independently and processes them.

A Redis consumer group is used to manage message consumption and acknowledgement.

The implementation also includes pending-message recovery using `XAUTOCLAIM`.

**Relevant file:** `src/officesense/ingestion/redis_stream.py`

### 3.3 Inference Worker

The inference worker retrieves frames from Redis and passes them to the person detection component.

A model registry provides a mechanism for loading inference components through a common interface.

The current implementation uses a pretrained YOLO model to identify people in each frame.

The resulting detections are used to calculate the number of detected people.

**Relevant files:**

- `src/officesense/inference/worker.py`
- `src/officesense/inference/registry.py`
- `src/officesense/inference/plugins/person_detector.py`

### 3.4 MongoDB Storage

MongoDB Atlas is used to store frame-level inference results and generated events.

Each processed frame produces a document in the `frame_results` collection.

The database connection and storage operations are handled by a dedicated storage module.

A TTL index has been created on the `ts` field of `frame_results`, configured for seven days (604,800 seconds).

This allows older frame-result documents to expire automatically.

**Relevant file:** `src/officesense/storage/database.py`

### 3.5 Crowding Rule Engine

A basic crowding rule has been implemented to identify sustained high-person-count conditions.

The rule evaluates:

- Camera ID
- Detected people count
- Video timestamp
- Event timestamp

When the detected count remains above the configured limit for the configured duration, a crowding event is generated and stored in MongoDB's `events` collection.

The current rule is camera-level. The event uses `camera_view` as a placeholder rather than a geometrically defined office zone.

**Relevant file:** `src/officesense/rules/crowding.py`

### 3.6 Docker Containerisation

Docker Compose is used to run the pipeline components as separate services.

The current Compose configuration includes:

| Service | Responsibility |
|---|---|
| Redis | Frame message transport |
| Producer | Reads recorded video and publishes frames |
| Consumer | Retrieves frames, performs inference, evaluates rules and stores results |

The Docker image uses Python 3.12 and installs CPU-only PyTorch dependencies.

Redis health checks and service dependencies are configured in Docker Compose.

The producer and consumer communicate with Redis through the Compose service network.

**Relevant files:**

- `Dockerfile`
- `docker-compose.yml`

### 3.7 Phase 1 Testing and Results

The pipeline was tested using recorded office footage.

The following behaviour was verified:

1. Docker Compose successfully started the Redis, producer and consumer services.
2. The producer read the recorded video and published sampled frames to Redis.
3. The consumer retrieved frames through the Redis consumer group.
4. The YOLO model performed person detection on the retrieved frames.
5. Frame-level results were inserted into MongoDB Atlas.
6. The crowding rule was evaluated during processing.
7. A crowding event was successfully generated and inserted into the MongoDB `events` collection.
8. The seven-day TTL index was verified in MongoDB.

The test run produced 22 frame-result documents and a crowding event.

This confirms that the recorded-video pipeline is operational across the ingestion, transport, inference, rule evaluation and storage components.

---

## 4. Current Architecture

The implemented Phase 1 processing flow is:

```text
Recorded Video
      |
      v
Video Ingestion
(OpenCV)
      |
      v
Frame Sampling
      |
      v
JPEG Encoding
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
People Count
      |
      +-------------------+
      |                   |
      v                   v
MongoDB              Crowding Rule
Frame Results             |
                          v
                    Event Generation
                          |
                          v
                    MongoDB Events
```

The producer and consumer run independently as Docker Compose services. Redis provides the communication layer between them.

---

## 5. Project Structure

```text
officesense/
├── assets/
│   └── test_images/
├── data/
│   └── videos/
├── outputs/
├── scripts/
│   ├── main.py
│   ├── read_video.py
│   ├── run_consumer.py
│   ├── run_producer.py
│   ├── test_frame_storage.py
│   ├── test_ingestion.py
│   ├── test_mongodb.py
│   ├── test_opencv.py
│   └── test_yolo.py
├── src/
│   └── officesense/
│       ├── inference/
│       │   ├── plugins/
│       │   │   └── person_detector.py
│       │   ├── registry.py
│       │   └── worker.py
│       ├── ingestion/
│       │   ├── redis_stream.py
│       │   └── video_source.py
│       ├── rules/
│       │   └── crowding.py
│       └── storage/
│           └── database.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

The repository also contains older Flask application files from an earlier experiment. They are not part of the current Phase 1 processing pipeline.

---

## 6. Current Limitations and Outstanding Work

The current implementation demonstrates the core recorded-video processing pipeline, but it does not yet satisfy every Phase 1 requirement in the design document.

| Requirement | Current status |
|---|---|
| Recorded video ingestion | Implemented |
| Configurable frame sampling | Implemented |
| Redis Stream transport | Implemented |
| Consumer group processing | Implemented |
| Pretrained person detection | Implemented |
| Model registry | Implemented |
| MongoDB frame-result storage | Implemented |
| Seven-day TTL index | Implemented and verified |
| Basic crowding rule | Implemented and tested |
| Crowding event storage | Implemented and tested |
| Docker Compose deployment | Implemented and tested |
| Live RTSP camera ingestion | Pending |
| Automatic RTSP reconnection | Pending |
| Genuine zone-based people counting | Pending |
| Zone polygon configuration and mapping | Planned for Phase 2 in the design document |

### Important clarification: Zone-based counting

The Phase 1 use case describes people counting per zone. However, the current implementation counts detected people across the entire camera frame.

The design document places zone geometry and mapping functionality in Phase 2. Until those components are implemented, the current count must be treated as a camera-level count, not a true zone-level count.

This distinction should be clarified with the project mentor.

### Important clarification: Live camera testing

The current pipeline uses recorded footage as its input source. Live RTSP ingestion has not yet been integrated.

Recorded-video testing validates the processing pipeline, but it does not establish that live camera ingestion, reconnect handling or real-time performance have been verified.

---

## 7. Next Development Steps

The next steps are:

1. Understand and validate the current Docker, Redis and consumer architecture.
2. Review the producer-consumer workflow and message lifecycle.
3. Integrate an authorised RTSP camera source.
4. Implement connection handling and automatic reconnection.
5. Validate frame sampling and inference on a live stream.
6. Clarify the Phase 1 zone-counting expectation with the mentor.
7. Implement zone mapping when the required geometry and configuration are available.
8. Validate the pipeline against representative footage and expected counts.
9. Record a working demonstration of the completed functionality.

Live camera testing must use authorised camera access and follow applicable privacy, employee-notice and retention requirements.

---

## 8. Conclusion

Phase 0 successfully established the initial person-detection pipeline using recorded video.

Phase 1 has extended this into a modular, containerised processing system. The current implementation demonstrates frame ingestion, Redis-based message transport, YOLO inference, MongoDB persistence and crowding event generation.

The recorded-video pipeline has been successfully tested end to end.

The next major milestone is to integrate live RTSP ingestion and complete the remaining Phase 1 requirements while preserving the modular architecture.

**Overall status:** Phase 0 completed. Phase 1 core implementation operational; remaining acceptance requirements are still in progress.