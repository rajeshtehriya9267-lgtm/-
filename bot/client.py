from pyrogram import Client
from bot.config import (
    BOT_TOKEN,
    API_ID,
    API_HASH,
    SESSION_STRING
)

bot = Client(
    "KukuMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

assistant = Client(
    "KukuAssistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)
