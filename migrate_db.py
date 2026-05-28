import asyncio
from database.ia_filterdb import collection
from utils import normalize_title

async def migrate():

    print("Starting migration...")

    async for file in collection.find({}):

        file_name = file.get("file_name", "")

        parsed = normalize_title(file_name)

        await collection.update_one(
            {"_id": file["_id"]},
            {
                "$set": {
                    "normalized_name": parsed["normalized_name"],
                    "season": parsed["season"],
                    "episode": parsed["episode"]
                }
            }
        )

        print(f"Updated: {file_name}")

    print("Migration completed")

asyncio.run(migrate())
