import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import TEXT, ASCENDING
from pymongo.errors import DuplicateKeyError, OperationFailure
from info import USE_CAPTION_FILTER, FILES_DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, MAX_BTN, DATA_DATABASE_URL
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
    
    document = {
        '_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size,
        'caption': file_caption
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
        recent_limit = 100  # default limit for fetching recently added files
        results = []
        
        cursor1 = collection.find({}).sort("_id", -1).limit(recent_limit)
        docs1 = await cursor1.to_list(length=recent_limit)
        results.extend(docs1)

        return results

    if ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    db_query = {"$regex": raw_pattern, "$options": "i"}
    search_filter = {"$or": [{"file_name": db_query}]}
    
    if USE_CAPTION_FILTER:
        search_filter["$or"].append({"caption": db_query})

    results = []
    
    cursor1 = collection.find(search_filter)
    docs1 = await cursor1.to_list(length=None) 
    results.extend(docs1)

    return results


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

