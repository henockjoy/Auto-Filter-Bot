import logging
from struct import pack
import re
from utils import normalize_title, fuzzy_match
import base64
from pyrogram.file_id import FileId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import TEXT, ASCENDING
from pymongo.errors import DuplicateKeyError, OperationFailure
from info import USE_CAPTION_FILTER, FILES_DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, DATA_DATABASE_URL
import PTN, asyncio
from database.users_chats_db import data_db
from utils import send_update

logger = logging.getLogger(__name__)

client = AsyncIOMotorClient(FILES_DATABASE_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

updates_collection = data_db['notified_media']

async def setup_database():
    try:
        await updates_collection.create_index(
            [("title", ASCENDING), ("year", ASCENDING)],
            unique=True,
            name="title_year_unique"
        )
        logger.info("DATA_DATABASE_URL update indexes created/verified.")
    except OperationFailure as e:
        if e.code == 85:  # IndexOptionsConflict
            logger.warning("DATA_DATABASE_URL update index conflict detected. Dropping old indexes and recreating...")
            await updates_collection.drop_indexes() 
            await updates_collection.create_index(
                [("title", ASCENDING), ("year", ASCENDING)],
                unique=True,
                name="title_year_unique"
            )
            logger.info("DATA_DATABASE_URL update indexes recreated successfully.")
        else:
            logger.exception(e)
            exit()

    try:
        await collection.create_index([("file_name", TEXT), ("caption", TEXT)], name="file_name_caption_text")
        await collection.create_index("normalized_name")
        await collection.create_index("season")
        await collection.create_index("episode")
        logger.info("FILES_DATABASE_URL indexes created/verified.")
    except OperationFailure as e:
        if e.code == 85:  # IndexOptionsConflict
            logger.warning("FILES_DATABASE_URL index conflict detected. Dropping old text indexes and recreating...")
            await collection.drop_indexes() 
            await collection.create_index([("file_name", TEXT), ("caption", TEXT)], name="file_name_caption_text")
            logger.info("FILES_DATABASE_URL indexes recreated successfully.")
        elif 'quota' in str(e).lower():
            if not SECOND_FILES_DATABASE_URL:
                logger.error('Your FILES_DATABASE_URL quota is full, add SECOND_FILES_DATABASE_URL. (Bot will still work for searching)')
            else:
                logger.info('FILES_DATABASE_URL quota is full, relying on SECOND_FILES_DATABASE_URL')
        else:
            logger.exception(e)
            exit() 

async def db_count_documents():
    return await collection.count_documents({})


async def trigger_update_if_new(title, year):
    if not title:
        return
    normalized_title = str(title).strip().lower()
    try:
        await updates_collection.insert_one({
            "title": normalized_title, 
            "year": year
        })
        asyncio.create_task(send_update(title, year))
    except DuplicateKeyError:
        pass


async def save_file(media):
    file_id = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
    file_caption = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.caption))
    
    parsed = normalize_title(file_name)
    caption_text = file_caption or file_name

    languages = extract_languages(caption_text)
    qualities = extract_qualities(caption_text)

    document = {
        '_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size,
        'caption': file_caption,

        # NEW SEARCH FIELDS
        'normalized_name': parsed["normalized_name"],
        'season': parsed["season"],
        'episode': parsed["episode"]
        "languages": languages,
        "qualities": qualities
    }

    
    data = PTN.parse(file_name)
    title = data.get('title')
    year = data.get('year')
    
    try:
        await collection.insert_one(document)
        logger.info(f'Saved - {file_name}')
        
        await trigger_update_if_new(title, year)
        return 'suc'
        
    except DuplicateKeyError:
        logger.warning(f'Already Saved - {file_name}')
        return 'dup'
        
    except OperationFailure:
        logger.error('FILES_DATABASE_URL is full')
        return 'err'

async def get_search_results(query):

    query = str(query).strip()

    if not query:
        cursor = collection.find({}).sort("_id", -1)
        return await cursor.to_list(length=None)

    parsed = normalize_title(query)

    normalized_query = parsed["normalized_name"]

    query_words = normalized_query.split()

    regex_pattern = ".*".join(query_words)

    db_query = {
        "normalized_name": {
            "$regex": regex_pattern,
            "$options": "i"
        }
    }

    if parsed["season"] is not None:
        db_query["season"] = parsed["season"]

    if parsed["episode"] is not None:
        db_query["episode"] = parsed["episode"]

    cursor = collection.find(db_query)

    files = []

    async for file in cursor:

        score = fuzzy_match(
            normalized_query,
            file.get("normalized_name", "")
        )

        if score >= 90:
            files.append(file)

    return files


async def delete_files(query):
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        regex = query
        
    filter_query = {'file_name': regex}
    
    result1 = await collection.delete_many(filter_query)
    total_deleted = result1.deleted_count
    
    return total_deleted


async def get_file_details(query):
    return await collection.find_one({'_id': query})


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id

