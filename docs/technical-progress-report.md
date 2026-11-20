# OfficeSense – Weekly Technical Progress Report

**Reporting Period:** Week 1  
**Date:** 20 November 2026  
**Project:** OfficeSense – AI Video Analytics for Office Spaces  
**Role:** Software Engineering Intern  
**Repository:** [OfficeSense – GitHub](https://github.com/niranjana-nest/OfficeSense)

---

## 1. Project Overview

OfficeSense is an AI-powered video analytics system designed to monitor office spaces through computer vision. The system processes video frames, detects people, stores structured detection metadata, and evaluates configurable conditions to identify crowding events.

The first development phase focuses on establishing the video ingestion, inference, data storage and rule-processing pipeline.

Development has progressed through the Phase 0 video-processing prototype and the core Phase 1 pipeline.

## 2. Completed Features

### 2.1 Phase 0 – Standalone Video Detection

Implemented a standalone video-processing pipeline using OpenCV and YOLO.

Completed functionality:
- Reads recorded office video files.
- Extracts and processes video frames.
- Performs person detection using a pretrained YOLO model.
- Draws bounding boxes around detected people.
- Generates annotated output videos.
- Supports configurable confidence thresholds, image sizes and frame sampling.

### 2.2 Phase 1 – Video Analytics Pipeline

Implemented the principal components of the Phase 1 architecture.

**Video ingestion**
- Developed a video source module to read and sample video frames.
- Captures camera identifiers, frame numbers and timestamps.
- Supports configurable frame sampling.

**Redis Stream**
- Implemented frame publishing using Redis Streams.
- Encodes frames into JPEG before publishing.
- Implemented message decoding and reconstruction.
- Implemented consumer group creation and message acknowledgement.
- Added recovery of pending messages using `XAUTOCLAIM`.
- Implemented continuous message consumption when new messages are unavailable.

**Inference and plug-in architecture**
- Implemented a model registry for inference plug-ins.
- Integrated a YOLO-based person detector.
- Filters detections to the person class.
- Returns structured bounding-box coordinates and confidence scores.

**MongoDB storage**
- Implemented MongoDB client creation and database access.
- Stores processed frame metadata and detection results in the `frame_results` collection.
- Configured a seven-day TTL index for automatic metadata expiration.

**Crowding rule**
- Implemented a duration-based crowding rule.
- Tracks people counts independently for each camera.
- Generates a crowding event when the configured threshold is exceeded for the required duration.
- Prevents repeated event generation while the same crowding condition continues.
- Resets crowding state when the count returns to the permitted limit.

**Containerised execution**
- Implemented Dockerfile and Docker Compose configuration for Redis, the producer and the consumer.
- Successfully built and executed the CPU-based Docker pipeline.

### 2.3 Integration Verification

The Docker-based pipeline was executed using recorded video footage.

Verification included:
- Successful frame publishing to Redis.
- Successful frame consumption and inference.
- Person detection using the YOLO model.
- Storage of processed frame results in MongoDB.
- Generation of a crowding event.
- Verification of Redis consumer group processing and pending-message recovery.
- Confirmation of the seven-day MongoDB TTL index.

The recorded-video integration run processed 22 frame results and generated a crowding event.

**Current limitation:** Live RTSP camera integration and genuine polygon-based zone mapping have not yet been completed. The current crowding event uses `camera_view` as a placeholder rather than a geometrically defined zone.

---

## 3. Implemented Architecture

The current Phase 1 architecture consists of:

1. **Producer:** Reads sampled frames from a recorded video source.
2. **Redis Stream:** Transports encoded frames and associated metadata.
3. **Consumer:** Retrieves frames from Redis and coordinates inference.
4. **Inference plug-in:** Executes YOLO-based person detection.
5. **MongoDB:** Stores structured frame results.
6. **Crowding rule engine:** Evaluates people counts and generates events.

A separate standalone inference worker is also implemented for direct video-to-MongoDB processing.

The standalone worker and Redis-based Docker consumer are distinct execution paths.

## 4. Automated Testing and Results

Implemented an automated test suite using pytest and pytest-cov.

**Final test results:**

| Module | Tests passed |
|---|---:|
| Crowding rule | 5 |
| MongoDB storage | 5 |
| Person detector | 4 |
| Redis Stream | 10 |
| Model registry | 2 |
| Video ingestion | 5 |
| Inference worker | 4 |
| **Total** | **35** |

**Result:** 35 tests passed, 0 failed.

The automated tests cover:
- Expected and negative behaviour of the crowding rule.
- Frame sampling and metadata generation.
- Invalid video handling and resource cleanup.
- Redis frame encoding, publishing, decoding and acknowledgement.
- Consumer group creation and error handling.
- Pending-message recovery and empty-stream waiting behaviour.
- Model registry loading and invalid plug-in handling.
- Person detection output formatting.
- MongoDB connection configuration, document insertion and TTL index creation.
- Inference worker processing, storage and client cleanup.

Most unit tests use mocked dependencies to isolate application logic. Actual Redis, Docker and MongoDB integration was verified separately through the recorded-video pipeline execution.

## 5. Test Coverage

Measured using pytest-cov.

| Metric | Result |
|---|---:|
| Total executable statements | 172 |
| Covered statements | 171 |
| Uncovered statements | 1 |
| Overall statement coverage | **99.42%** |

The sole uncovered statement is the standalone execution entry point in `inference/worker.py`. It is not executed when the module is imported during unit testing.

The Redis Stream, video ingestion, person detector, model registry, crowding rule and MongoDB storage modules achieved 100% statement coverage.

The inference worker achieved 96% statement coverage.

The coverage requirement configured in CI is 95%.

## 6. Static Analysis

Static analysis was performed using Ruff.

Initial findings included:
- Import ordering and formatting issues.
- Unused imports and variables.
- Broad exception handling.
- An inappropriate use of `exit()`.
- Test assertion and regular-expression lint findings.

The identified issues were reviewed and resolved. Diagnostic scripts were renamed to prevent pytest from mistakenly collecting them as automated test modules.

**Final result:**

- Ruff checks completed successfully.
- Zero remaining Ruff findings across `src/`, `tests/` and `scripts/`.

## 7. Security Findings

Performed a dependency vulnerability audit using `pip-audit` against `requirements.txt`.

**Result:** No known vulnerabilities found in the declared dependencies.

This audit covers known dependency vulnerabilities and does not constitute a complete application security assessment.

The project also uses environment-based configuration for MongoDB credentials. The `.env` file is excluded from version control through `.gitignore`.

## 8. Continuous Integration

Configured a GitHub Actions CI workflow in:

`.github/workflows/ci.yml`

The workflow is triggered by pushes to the `main` branch and pull requests targeting `main`.

The pipeline performs:

1. Repository checkout.
2. Python 3.12 environment setup.
3. Dependency installation.
4. Ruff static analysis.
5. Automated pytest execution with coverage reporting.
6. A minimum coverage gate of 95%.

**Verified GitHub Actions execution:**

- Workflow: OfficeSense CI
- Trigger: Push to `main`
- Commit: `d13f0e7`
- Environment: Ubuntu, Python 3.12
- Duration: 2 minutes 46 seconds
- Ruff: Passed
- Automated tests and coverage gate: Passed
- Overall CI status: **Successful**

GitHub reported a non-blocking Node.js 20 deprecation warning for underlying GitHub Actions. It did not affect the successful workflow execution.

## 9. Repository and Version Control

GitHub repository:

https://github.com/niranjana-nest/OfficeSense

Relevant commits:

- [351c96c – Build Phase 1 video analytics pipeline with Docker and Redis](https://github.com/niranjana-nest/OfficeSense/commit/351c96c)
- [7441602 – Add Phase 0 and Phase 1 technical progress report](https://github.com/niranjana-nest/OfficeSense/commit/7441602)
- [d13f0e7 – Add automated tests and GitHub Actions CI](https://github.com/niranjana-nest/OfficeSense/commit/d13f0e7)

The automated test suite, static-analysis configuration, diagnostic-script renames and GitHub Actions workflow have been committed and pushed to `main`.

## 10. Unresolved Blockers and Outstanding Requirements

The following items remain outstanding:

**Live camera ingestion**
- Integration with an authorised RTSP camera stream.
- Camera reconnection and live-stream validation.
- Verification of the live ingestion pipeline.

**Zone-based analytics**
- Implementation of actual zone geometry and polygon mapping.
- People counting per configured zone.
- Replacement of the current `camera_view` placeholder in crowding events.

**Further integration and validation**
- Additional recorded-video testing against hand-labelled expected counts.
- Validation of event timing and end-to-end processing latency.
- Further integration testing across the complete pipeline.

**CI improvements**
- Address the non-blocking Node.js 20 deprecation warning.
- Consider adding automated security scanning to GitHub Actions.

Before connecting real office cameras, the required legal and HR approvals, employee notifications and data-retention arrangements must be confirmed.

## 11. Demonstration Video

**Status:** To be submitted separately.

The Week 1 demonstration video will be submitted as a separate deliverable and will demonstrate the implemented functionality of the Phase 0 and Phase 1 pipeline.

## 12. Conclusion

During Week 1, the OfficeSense project progressed from a standalone person-detection prototype to a containerised video analytics pipeline with Redis-based frame transport, YOLO inference, MongoDB storage and crowding-event evaluation.

Automated testing, static analysis, dependency auditing and continuous integration were also established.

The project currently has 35 passing automated tests, 99.42% statement coverage, zero Ruff findings and a successful GitHub Actions execution.

The core recorded-video pipeline has been implemented and verified. Live RTSP integration and true zone-based analytics remain outstanding requirements for further Phase 1 development.