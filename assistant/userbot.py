from pyrogram import Client
from config import config
from utils.logger import log


class Userbot:
    """Single assistant account via SESSION_STRING. Extend to list-based for multi-assistant."""

    def __init__(self):
        self.client = Client(
            "kuku-assistant",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.SESSION_STRING,
            no_updates=True,
        )
        self._id = None

    async def start(self):
        await self.client.start()
        me = await self.client.get_me()
        self._id = me.id
        log.info(f"Assistant ready: {me.first_name} ({me.id})")

    async def stop(self):
        await self.client.stop()

    async def get_assistant_id(self) -> int | None:
        return self._id


userbot = Userbot()
