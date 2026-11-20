
from unittest.mock import MagicMock

import pytest

from officesense.storage import database


def test_create_mongo_client_uses_environment_uri(monkeypatch):
    fake_client = MagicMock()

    monkeypatch.setenv("MONGODB_URI", "mongodb://test-uri")

    monkeypatch.setattr(
        database,
        "MongoClient",
        lambda uri, **kwargs: fake_client
    )

    client = database.create_mongo_client()

    assert client is fake_client


def test_create_mongo_client_raises_when_uri_missing(monkeypatch):
    monkeypatch.delenv("MONGODB_URI", raising=False)

    with pytest.raises(
        ValueError,
        match=r"MONGODB_URI not found in \.env"
    ):
        database.create_mongo_client()


def test_get_database_returns_officesense_database():
    fake_client = MagicMock()
    fake_database = MagicMock()

    fake_client.__getitem__.return_value = fake_database

    result = database.get_database(fake_client)

    fake_client.__getitem__.assert_called_once_with("officesense")
    assert result is fake_database


def test_save_frame_result_inserts_document():
    fake_db = MagicMock()
    fake_collection = MagicMock()
    fake_result = MagicMock()
    fake_result.inserted_id = "test-id"

    fake_db.__getitem__.return_value = fake_collection
    fake_collection.insert_one.return_value = fake_result

    frame_result = {
        "camera_id": "camera-01",
        "people_count": 5
    }

    result = database.save_frame_result(fake_db, frame_result)

    fake_db.__getitem__.assert_called_once_with("frame_results")
    fake_collection.insert_one.assert_called_once_with(frame_result)
    assert result == "test-id"


def test_create_ttl_index_creates_seven_day_index(capsys):
    fake_db = MagicMock()
    fake_collection = MagicMock()

    fake_db.__getitem__.return_value = fake_collection

    database.create_ttl_index(fake_db)

    fake_db.__getitem__.assert_called_once_with("frame_results")

    fake_collection.create_index.assert_called_once_with(
        "ts",
        expireAfterSeconds=604800
    )

    assert "7 days" in capsys.readouterr().out
