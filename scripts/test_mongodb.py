import sys
from pathlib import Path

# Make the src directory importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from officesense.storage.database import (
    create_mongo_client,
    get_database
)

try:
    client = create_mongo_client()

    # Test the connection
    client.admin.command("ping")

    db = get_database(client)

    print("MongoDB connection successful!")
    print(f"Database: {db.name}")

except Exception as error:
    print(f"MongoDB connection failed: {error}")

finally:
    if "client" in locals():
        client.close()

from officesense.storage.database import (
    create_mongo_client,
    get_database
)

client = create_mongo_client()
db = get_database(client)

print(db["frame_results"].index_information())

client.close()
