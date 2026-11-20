import sys
from datetime import datetime, timezone
from pathlib import Path

from pymongo.errors import PyMongoError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from officesense.storage.database import (
    create_mongo_client,
    get_database,
    save_frame_result,
)

client = None

try:
    client = create_mongo_client()
    client.admin.command("ping")

    db = get_database(client)

    sample_result = {
        "camera_id": "test-camera-01",
        "ts": datetime.now(timezone.utc),
        "frame_no": 120,
        "models": {
            "person_detector": "yolo26n"
        },
        "detections": [
            {
                "bbox": [812, 220, 940, 560],
                "conf": 0.91,
                "zones": ["open-desk-area"]
            }
        ]
    }

    document_id = save_frame_result(db, sample_result)

    print("Frame result saved successfully!")
    print(f"Document ID: {document_id}")

except (PyMongoError, ValueError) as error:
    print(f"Error: {error}")

finally:
    if client:
        client.close()
