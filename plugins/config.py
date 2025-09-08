import os
from os import environ, getenv
import logging

logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO
)

class Config(object):
    
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    API_ID = int(os.environ.get("API_ID", ))
    API_HASH = os.environ.get("API_HASH", "")
    
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    MAX_FILE_SIZE = 2194304000
    FREE_USER_MAX_FILE_SIZE = 2194304000
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 128))
    DEF_THUMB_NAIL_VID_S = os.environ.get("DEF_THUMB_NAIL_VID_S", "https://placehold.it/90x90")
    HTTP_PROXY = os.environ.get("HTTP_PROXY", "")
    TG_MAX_FILE_SIZE = int(os.getenv("TG_MAX_FILE_SIZE", 2097152000))
    
    OUO_IO_API_KEY = ""
    MAX_MESSAGE_LENGTH = 4096
    PROCESS_MAX_TIMEOUT = 3600
    DEF_WATER_MARK_FILE = "@UploaderXNTBot"

    BANNED_USERS = set(int(x) for x in os.environ.get("BANNED_USERS", "7057966909").split())

    DATABASE_URL = os.environ.get("DATABASE_URL", "")

    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))
    LOGGER = logging
    OWNER_ID = int(os.environ.get("OWNER_ID", "7413682152"))
    SESSION_NAME = "UploaderXNTBot"
    UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", "")

    TG_MIN_FILE_SIZE = 2194304000
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
    ADL_BOT_RQ = {}

    # Set False off else True
    TRUE_OR_FALSE = os.environ.get("TRUE_OR_FALSE", "True").lower() == "true"

    # Shortlink settings
    SHORT_DOMAIN = environ.get("SHORT_DOMAIN", "shrinkme.top")
    SHORT_API = environ.get("SHORT_API", "1a2887e5dc4c4e8134a7b0afd82e8f2cfc0ee2d4")

    # Verification video link
    VERIFICATION = os.environ.get("VERIFICATION", "https://t.me/ProBotXUpdate")

    
