import re
from os import environ
import os
from Script import script
import logging

logger = logging.getLogger(__name__)

def is_enabled(type, value):
    data = environ.get(type, str(value))
    if data.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif data.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        logger.error(f'{type} is invalid, exiting now')
        exit()

def is_valid_ip(ip):
    ip_pattern = r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    return re.match(ip_pattern, ip) is not None

# Bot information
API_ID = environ.get('API_ID', '')
if len(API_ID) == 0:
    logger.error('API_ID is missing, exiting now')
    exit()
else:
    API_ID = int(API_ID)
API_HASH = environ.get('API_HASH', '')
if len(API_HASH) == 0:
    logger.error('API_HASH is missing, exiting now')
    exit()
BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    logger.error('BOT_TOKEN is missing, exiting now')
    exit()
BOT_ID = BOT_TOKEN.split(":")[0]
PORT = int(environ.get('PORT', '8080'))

# Upload your images to "postimages.org" and get direct link
PICS = (environ.get('PICS', 'https://i.postimg.cc/V6NDy9b9/04b015f6eafd3a49e6957b9c41f2c37b.jpg https://i.postimg.cc/TwPC8jWN/117f415875b35318a250ddf801c319b8.jpg https://i.postimg.cc/43PBF2nW/2cf5878cdd39b917f2f0400571213384.jpg https://i.postimg.cc/tTg20dVf/3e9353dae6ef6e01ecf8f6b54f51bd97.jpg https://i.postimg.cc/1tzJx0NM/59fb0d8c8a45e4832401c16189b1b319.jpg https://i.postimg.cc/d104MRTj/648129a9d72a7ac3e4af8cc6f2bae8ca.jpg https://i.postimg.cc/j5jZV6JM/a525581952c934d4abc23f295612383a.jpg https://i.postimg.cc/SsKD0Lz6/b22e06d7bdbe5513b8ce7e8560296bea.jpg https://i.postimg.cc/d104MRT4/b26eec9264bfa13d7baf430302315bac.jpg https://i.postimg.cc/bvg3FVdF/d82f7cc65a240386616d1e401c0b20fd.jpg https://i.postimg.cc/tTg20dV8/edfb9f53f30a80514651c4310255b7b7.jpg')).split()

# Bot Admins
ADMINS = environ.get('ADMINS', '1824857814')
if len(ADMINS) == 0:
    logger.error('ADMINS is missing, exiting now')
    exit()
else:
    ADMINS = [int(admins) for admins in ADMINS.split()]

# Channels
INDEX_CHANNELS = [int(index_channels) if index_channels.startswith("-") else index_channels for index_channels in environ.get('INDEX_CHANNELS', '').split()]
if len(INDEX_CHANNELS) == 0:
    logger.info('INDEX_CHANNELS is empty')
LOG_CHANNEL = environ.get('LOG_CHANNEL', '')
if len(LOG_CHANNEL) == 0:
    logger.error('LOG_CHANNEL is missing, exiting now')
    exit()
else:
    LOG_CHANNEL = int(LOG_CHANNEL)
UPDATES_SEND_CHANNEL = environ.get('UPDATES_SEND_CHANNEL', '-1002429568959')
if len(UPDATES_SEND_CHANNEL) == 0:
    logger.info('UPDATES_SEND_CHANNEL is missing')
    UPDATES_SEND_CHANNEL = None
else:
    UPDATES_SEND_CHANNEL = int(UPDATES_SEND_CHANNEL)

# support group
SUPPORT_GROUP = environ.get('SUPPORT_GROUP', '-1001771340892')
if len(SUPPORT_GROUP) == 0:
    logger.error('SUPPORT_GROUP is missing, exiting now')
    exit()
else:
    SUPPORT_GROUP = int(SUPPORT_GROUP)

# MongoDB information
DATA_DATABASE_URL = environ.get('DATA_DATABASE_URL', "")
if len(DATA_DATABASE_URL) == 0:
    logger.error('DATA_DATABASE_URL is missing, exiting now')
    exit()
FILES_DATABASE_URL = environ.get('FILES_DATABASE_URL', "")
if len(FILES_DATABASE_URL) == 0:
    logger.error('FILES_DATABASE_URL is missing, exiting now')
    exit()
DATABASE_NAME = environ.get('DATABASE_NAME', "unix")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'yoonbot')

# Links
SUPPORT_LINK = environ.get('SUPPORT_LINK', 'https://t.me/TeamYoonseri')
UPDATES_LINK = environ.get('UPDATES_LINK', 'https://t.me/FT_Channels')
FILMS_LINK = environ.get('FILMS_LINK', 'https://t.me/FT_Chatz')
TUTORIAL = environ.get("TUTORIAL", "https://t.me/FT_Channels")
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "https://t.me/FT_Channels")

# Bot settings
TIME_ZONE = environ.get('TIME_ZONE', 'Asia/Colombo') # Replace your time zone
DELETE_TIME = int(environ.get('DELETE_TIME', 3600)) # Add time in seconds
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
MAX_BTN = int(environ.get('MAX_BTN', 8))
LANGUAGES = [language.lower() for language in environ.get('LANGUAGES', 'Hindi English Telugu Tamil Kannada Malayalam Marathi Punjabi Korean Chinese Japanese Spanish French Portuguese Italian Urdu Turkish').split()]
QUALITY = [quality.lower() for quality in environ.get('QUALITY', '240p 360p 480p 576p 720p 1080p 2160p').split()]
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", script.IMDB_TEMPLATE)
FILE_CAPTION = environ.get("FILE_CAPTION", script.FILE_CAPTION)
SHORTLINK_URL = environ.get("SHORTLINK_URL", "mdiskshortner.link")
SHORTLINK_API = environ.get("SHORTLINK_API", "20f1563cb983df6bcb0bfd7576d929909adccabe")
VERIFY_EXPIRE = int(environ.get('VERIFY_EXPIRE', 86400)) # Add time in seconds
WELCOME_TEXT = environ.get("WELCOME_TEXT", script.WELCOME_TEXT)
INDEX_EXTENSIONS = [extensions.lower() for extensions in environ.get('INDEX_EXTENSIONS', 'mp4 mkv avi').split()]
PM_FILE_DELETE_TIME = int(environ.get('PM_FILE_DELETE_TIME', '3600'))

# boolean settings
USE_CAPTION_FILTER = is_enabled('USE_CAPTION_FILTER', True)
IS_VERIFY = is_enabled('IS_VERIFY', False)
AUTO_DELETE = is_enabled('AUTO_DELETE', False)
WELCOME = is_enabled('WELCOME', False)
PROTECT_CONTENT = is_enabled('PROTECT_CONTENT', False)
LONG_IMDB_DESCRIPTION = is_enabled("LONG_IMDB_DESCRIPTION", False)
LINK_MODE = is_enabled("LINK_MODE", True)
IMDB = is_enabled('IMDB', False)
SPELL_CHECK = is_enabled("SPELL_CHECK", True)
SHORTLINK = is_enabled('SHORTLINK', False)

# for stream
IS_STREAM = is_enabled('IS_STREAM', True)
BIN_CHANNEL = environ.get("BIN_CHANNEL", "-1003052098698")
if len(BIN_CHANNEL) == 0:
    logger.error('BIN_CHANNEL is missing, exiting now')
    exit()
else:
    BIN_CHANNEL = int(BIN_CHANNEL)
URL = environ.get("URL", "https://t.me/yoonseri2bot/mini_app")
if len(URL) == 0:
    logger.error('URL is missing, exiting now')
    exit()
else:
    if URL.startswith(('https://', 'http://')):
        if not URL.endswith("/"):
            URL += '/'
    elif is_valid_ip(URL):
        URL = f'http://{URL}/'
    else:
        logger.error('URL is not valid, exiting now')
        exit()

#start command reactions 
REACTIONS = [reactions for reactions in environ.get('REACTIONS', '🤝 😇 🤗 😍 👍 🎅 😐 🥰 🤩 😱 🤣 😘 👏 😛 😈 🎉 ⚡️ 🫡 🤓 😎 🏆 🔥 🤭 🌚 🆒 👻 😁').split()]  # Multiple reactions can be used separated by space
EFFECT_IDS = [effect for effect in environ.get('EFFECT_IDS', '5104841245755180586 5104858069142078462 5159385139981059251 5046509860389126442 5046589136895476101 5107584321108051014').split()]

# for Premium 
IS_PREMIUM = is_enabled('IS_PREMIUM', False)
OWNER_USERNAME = environ.get("OWNER_USERNAME", "FTAdminbot")
PAYMENT_QR_CODE = "https://i.postimg.cc/d09Z2z3p/no-qr-code-sign-isolated-white-background-vector-illustration-234692015.webp" # add your payment qr code link, like upi qr code or any crypto qr code link
PAYMENT_ID = "henockjoy65-1@okaxis"  # add your payment id like upi id or crypto address

# Format -- Days: ['CURRENCY', Price]
PREMIUM_PLANS = {
    7: ['USD', 1], 
    14: ['USD', 2],
    30: ['USD', 3],
    365: ['USD', 10]
}
PAYMENT_TYPE = "UPI"  # can be changed to "Crypto (TRC20)" or "PayPal" or etc....


# for TMDb
TMDB_API_KEY = environ.get("TMDB_API_KEY", "0da1b0909b6f81d9543daf54db258f5a")  # Get API key from here - https://www.themoviedb.org/settings/api
if len(TMDB_API_KEY) == 0:
    logger.info('TMDB_API_KEY is missing')
    TMDB_API_KEY = None
