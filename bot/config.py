import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SESSION_STRING = os.getenv("SESSION_STRING")

MONGO_DB_URI = os.getenv("MONGO_DB_URI")

OWNER_ID = int(os.getenv("OWNER_ID"))
SUDO_ID = int(os.getenv("SUDO_ID"))

LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))

SUPPORT_GROUP = os.getenv("SUPPORT_GROUP")
UPDATES_CHANNEL = os.getenv("UPDATES_CHANNEL")

OWNER_USERNAME = os.getenv("OWNER_USERNAME")

ASSISTANT_NAME = os.getenv("ASSISTANT_NAME")
ASSISTANT_USERNAME = os.getenv("ASSISTANT_USERNAME")
