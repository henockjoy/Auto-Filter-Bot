from pyrogram.errors import UserNotParticipant, FloodWait
from info import LONG_IMDB_DESCRIPTION, ADMINS, IS_PREMIUM, TIME_ZONE, TMDB_API_KEY, USE_CAPTION_FILTER, UPDATES_SEND_CHANNEL, FILMS_LINK
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from pyrogram import enums
import re
from datetime import datetime
from database.users_chats_db import db
from shortzy import Shortzy
import requests, pytz
from Script import script
from rapidfuzz import fuzz


class temp(object):
    START_TIME = 0
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CANCEL = False
    U_NAME = None
    B_NAME = None
    SETTINGS = {}
    VERIFICATIONS = {}
    GET_ALL_FILES = {}
    USERS_CANCEL = False
    GROUPS_CANCEL = False
    BOT = None
    PREMIUM = {}


def get_plan_name(days):
    plan_names = {
        7: "1 Week",
        14: "2 Weeks",
        21: "3 Weeks",
        30: "1 Month",
        60: "2 Months",
        90: "3 Months",
        180: "6 Months",
        365: "1 Year"
    }
    if days in plan_names:
        return f"{plan_names[days]} Plan"
    return f"{days} Days Plan"


async def send_update(title, year):
    if not UPDATES_SEND_CHANNEL:
        return
    btn = [[
        InlineKeyboardButton('📥 Request from Here 📥', url=FILMS_LINK)
    ]]
    data = await get_poster(f"{title} {year}")
    if not data:
        _year = f"({year})" if year else ""
        await temp.BOT.send_message(chat_id=UPDATES_SEND_CHANNEL, text=f"✅ New Added ✅\n\n🏷 Title: {title.title()} {_year}", reply_markup=InlineKeyboardMarkup(btn))
        return
    caption = script.NEW_ADDED_TEMPLATE.format(
        title=data['title'],
        kind=data['kind'],
        votes=data['votes'],
        tmdb_id=data["tmdb_id"],
        runtime=data["runtime"],
        release_date=data['release_date'],
        year=data['year'],
        genres=data['genres'],
        plot=data['plot'],
        rating=data['rating'],
        url=data['url'],
        languages=data['languages'],
        countries=data['countries']
    )
    
    if data.get('poster'):
        await temp.BOT.send_photo(chat_id=UPDATES_SEND_CHANNEL, photo=data.get('poster'), caption=caption, reply_markup=InlineKeyboardMarkup(btn))
    else:
        await temp.BOT.send_message(chat_id=UPDATES_SEND_CHANNEL, text=caption, reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True))


async def handle_next_back(data, offset=0, max_results=0):
    out_data = data[offset:][:max_results]
    total_results = len(data)
    next_offset = offset + max_results
    if next_offset >= total_results:
        next_offset = 0
    return out_data, next_offset, total_results

async def is_subscribed(bot, query):
    btn = []
    if await is_premium(query.from_user.id, bot):
        return btn
    stg = await db.get_bot_sttgs()
    if not stg or not stg.get('FORCE_SUB_CHANNELS'):
        return btn
    for id in stg.get('FORCE_SUB_CHANNELS').split(' '):
        chat = await bot.get_chat(int(id))
        try:
            await bot.get_chat_member(int(id), query.from_user.id)
        except UserNotParticipant:
            btn.append(
                [InlineKeyboardButton(f'Join : {chat.title}', url=chat.invite_link)]
            )
    if stg and stg.get('REQUEST_FORCE_SUB_CHANNELS') and not await db.find_join_req(query.from_user.id):
        id = stg.get('REQUEST_FORCE_SUB_CHANNELS')
        chat = await bot.get_chat(int(id))
        try:
            await bot.get_chat_member(int(id), query.from_user.id)
        except UserNotParticipant:
            url = await bot.create_chat_invite_link(int(id), creates_join_request=True)
            btn.append(
                [InlineKeyboardButton(f'Request : {chat.title}', url=url.invite_link)]
            )
    return btn


def upload_image(file_path):
    with open(file_path, 'rb') as f:
        files = {'files[]': f}
        response = requests.post("https://uguu.se/upload", files=files)

    if response.status_code == 200:
        try:
            data = response.json()
            return data['files'][0]['url'].replace('\\/', '/')
        except Exception as e:
            return None
    else:
        return None


def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    else:
        return ", ".join(str(i) for i in k)


async def get_poster(query, bulk=False, id=False, file=None):
    if not TMDB_API_KEY:
        return None
    TMDB_BASE = "https://api.themoviedb.org/3"

    year = None
    title = query

    if not id:
        query = query.strip()

        year_match = re.findall(r"[1-2]\d{3}$", query)
        if year_match:
            year = year_match[0]
            title = query.replace(year, "").strip()

        elif file:
            file_year = re.findall(r"[1-2]\d{3}", file)
            if file_year:
                year = file_year[0]

        url = f"{TMDB_BASE}/search/multi"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title
        }

        res = requests.get(url, params=params).json()

        results = [
            r for r in res.get("results", [])
            if r.get("media_type") in ["movie", "tv"]
        ]

        if not results:
            return None

        if year:
            filtered = []
            for r in results:
                release = r.get("release_date") or r.get("first_air_date")
                if release and release.startswith(str(year)):
                    filtered.append(r)

            if filtered:
                results = filtered

        if bulk:
            _bulk = []
            for r in results:
                _title = r.get("title") or r.get("name")
                if _title:
                    _bulk.append({
                        "title": _title,
                        "id": r["id"]
                        })
            return _bulk


        data = results[0]
        tmdb_id = data["id"]
        media_type = data["media_type"]

    else:
        tmdb_id = query

        movie_test = requests.get(
            f"{TMDB_BASE}/movie/{tmdb_id}",
            params={"api_key": TMDB_API_KEY}
        )

        if movie_test.status_code == 200:
            media_type = "movie"
            data = movie_test.json()
        else:
            media_type = "tv"
            data = requests.get(
                f"{TMDB_BASE}/tv/{tmdb_id}",
                params={"api_key": TMDB_API_KEY}
            ).json()

    if not id:
        data = requests.get(
            f"{TMDB_BASE}/{media_type}/{tmdb_id}",
            params={"api_key": TMDB_API_KEY}
        ).json()

    title = data.get("title") or data.get("name")

    backdrop = None
    if data.get("backdrop_path"):
        backdrop = f"https://image.tmdb.org/t/p/original{data['backdrop_path']}"

    release_date = data.get("release_date") or data.get("first_air_date")

    genres = list_to_str([g["name"] for g in data.get("genres", [])])

    runtime = None
    if media_type == "movie":
        runtime = data.get("runtime")
    else:
        runtime = list_to_str(data.get("episode_run_time"))

    plot = data.get("overview") if LONG_IMDB_DESCRIPTION else str(data.get("overview"))[:200]

    rating = data.get("vote_average")
    votes = data.get("vote_count")
    languages = list_to_str([l["english_name"] for l in data.get("spoken_languages", [])])
    countries = list_to_str([c["name"] for c in data.get("production_countries", [])])

    return {
        "title": title,
        "tmdb_id": tmdb_id,
        "kind": media_type,
        "languages": languages,
        "countries": countries,
        "release_date": release_date,
        "year": release_date[:4] if release_date else None,
        "genres": genres,
        "runtime": runtime,
        "rating": rating,
        "votes": votes,
        "poster": backdrop,
        "plot": plot,
        "url": f"https://www.themoviedb.org/{media_type}/{tmdb_id}"
    }

async def is_check_admin(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except:
        return False

async def get_verify_status(user_id):
    verify = temp.VERIFICATIONS.get(user_id)
    if not verify:
        verify = await db.get_verify_status(user_id)
        temp.VERIFICATIONS[user_id] = verify
    return verify

async def update_verify_status(user_id, verify_token="", is_verified=False, link="", expire_time=0):
    current = await get_verify_status(user_id)
    current['verify_token'] = verify_token
    current['is_verified'] = is_verified
    current['link'] = link
    current['expire_time'] = expire_time
    temp.VERIFICATIONS[user_id] = current
    await db.update_verify_status(user_id, current)

    
async def is_premium(user_id, bot):
    if not IS_PREMIUM:
        return True
    if user_id in ADMINS:
        return True
    mp = await db.get_plan(user_id)
    if mp['premium']:
        if mp['expire'] < datetime.now():
            await bot.send_message(user_id, f"Your premium {mp['plan']} is expired in {mp['expire'].strftime('%Y.%m.%d %H:%M:%S')}, use /plan to activate new plan again")
            mp['expire'] = ''
            mp['plan'] = ''
            mp['premium'] = False
            await db.update_plan(user_id, mp)
            return False
        return True
    else:
        return False


async def check_premium(bot):
    while True:
        pr = [i for i in await db.get_premium_users() if i['status']['premium']]
        for p in pr:
            mp = p['status']
            if mp['expire'] < datetime.now():
                try:
                    await bot.send_message(
                        p['id'],
                        f"Your premium {mp['plan']} is expired in {mp['expire'].strftime('%Y.%m.%d %H:%M:%S')}, use /plan to activate new plan again"
                    )
                except Exception:
                    pass
                mp['expire'] = ''
                mp['plan'] = ''
                mp['premium'] = False
                await db.update_plan(p['id'], mp)
        await asyncio.sleep(1200)


async def broadcast_messages(user_id, message, pin):
    try:
        m = await message.copy(chat_id=user_id)
        if pin:
            await m.pin(both_sides=True)
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message, pin)
    except Exception as e:
        await db.delete_user(int(user_id))
        return "Error"

async def groups_broadcast_messages(chat_id, message, pin):
    try:
        k = await message.copy(chat_id=chat_id)
        if pin:
            try:
                await k.pin()
            except:
                pass
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await groups_broadcast_messages(chat_id, message, pin)
    except Exception as e:
        await db.delete_chat(chat_id)
        return "Error"

async def get_settings(group_id):
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        temp.SETTINGS.update({group_id: settings})
    return settings
    
async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current.update({key: value})
    temp.SETTINGS.update({group_id: current})
    await db.update_settings(group_id, current)

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


async def get_shortlink(url, api, link):
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link

def get_readable_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result

def get_wish():
    time = datetime.now(pytz.timezone(TIME_ZONE))
    now = time.strftime("%H")
    if now < "12":
        status = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 🌞"
    elif now < "18":
        status = "ɢᴏᴏᴅ ᴀꜰᴛᴇʀɴᴏᴏɴ 🌗"
    else:
        status = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌘"
    return status
    
async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""
        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1
        unit = ts[index:]
        if value:
            value = int(value)
        return value, unit
    value, unit = extract_value_and_unit(time_string)
    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0

REMOVE_WORDS = [
    "480p", "720p", "1080p", "2160p",
    "webrip", "web dl", "web-dl", "bluray",
    "x264", "x265", "hevc", "h264",
    "aac", "ddp", "ddp2", "amzn",
    "nf", "hdrip", "web", "dl",
    "mkv", "mp4", "hdr", "dv"
]

def normalize_title(text: str):

    text = text.lower()

    season = None
    episode = None

    # Extract S01E06
    se_match = re.search(r"s(\d+)e(\d+)", text, re.I)

    if se_match:
        season = int(se_match.group(1))
        episode = int(se_match.group(2))

    # Remove season/episode text
    text = re.sub(r"s\d+e\d+", "", text, flags=re.I)

    # Replace separators
    text = re.sub(r"[-_.]", " ", text)

    # Remove brackets
    text = re.sub(r"\[.*?\]|\(.*?\)", "", text)

    # Remove junk words
    for word in REMOVE_WORDS:
        text = text.replace(word, "")

    # Remove special chars
    text = re.sub(r"[^a-z0-9 ]", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return {
        "normalized_name": text,
        "season": season,
        "episode": episode
    }


def fuzzy_match(query, text):

    return fuzz.partial_ratio(
        query.lower(),
        text.lower()
    )


