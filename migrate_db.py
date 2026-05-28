from pymongo import MongoClient
from utils import normalize_title

MONGO_URI = "YOUR_MONGO_URI"

client = MongoClient(MONGO_URI)

db = client["your_database"]
collection = db["your_collection"]

cursor = collection.find({})

for file in cursor:

    file_name = file.get("file_name", "")

    parsed = normalize_title(file_name)

    collection.update_one(
        {"_id": file["_id"]},
        {
            "$set": {
                "normalized_name": parsed["normalized_name"],
                "season": parsed["season"],
                "episode": parsed["episode"]
            }
        }
    )

print("Migration completed")

