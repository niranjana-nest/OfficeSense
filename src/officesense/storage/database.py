import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def create_mongo_client():
    """Create a connection to MongoDB Atlas."""

    mongodb_uri = os.getenv("MONGODB_URI")

    if not mongodb_uri:
        raise ValueError("MONGODB_URI not found in .env")

    return MongoClient(
        mongodb_uri,
        serverSelectionTimeoutMS=5000
    )


def get_database(client):
    """Return the OfficeSense database."""

    return client["officesense"]


def save_frame_result(db, frame_result):
    """Save one processed frame's detection results."""

    collection = db["frame_results"]

    result = collection.insert_one(frame_result)

    return result.inserted_id


def create_ttl_index(db):
    collection = db["frame_results"]

    collection.create_index(
        "ts",
        expireAfterSeconds=7 * 24 * 60 * 60
    )

    print("MongoDB TTL index created: frame_results (7 days)")
