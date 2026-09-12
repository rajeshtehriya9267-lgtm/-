import asyncio
import time
from datetime import datetime

from pyrogram import Client, idle
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.database import init_db, close_db
from database.users import db_users
from assistant.userbot import userbot
from assistant.call import call
from bot.handlers import start, play, controls, admin, misc
from utils.logger import log

START_TIME = time.time()


class KukuMusic:
    def __init__(self):
        self.pyro = Client(
            "kuku-assistant",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.SESSION_STRING,
        )
        self.aio_bot = Bot(
            config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.dp = Dispatcher()

    async def startup(self):
        await init_db()
        await self.pyro.start()
        me = await self.pyro.get_me()
        log.info(f"Assistant online: @{me.username}")
        await self.aio_bot.get_me()
        await call.start()
        await db_users.ensure_indexes()

        self.dp.include_router(start.router)
        self.dp.include_router(admin.router)
        self.dp.include_router(play.router)
        self.dp.include_router(controls.router)
        self.dp.include_router(misc.router)

        # start idle-monitor
        asyncio.create_task(call.idle_monitor())
        try:
            await self.aio_bot.send_message(
                config.LOG_GROUP_ID,
                f"🎧 <b>𝕂𝕌𝕂𝕌 𝕄𝕌𝕊𝕀ℂ</b> deployed successfully!\n"
                f"⏰ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            )
        except Exception:
            pass
        log.info("Bot started.")

    async def shutdown(self):
        await call.stop_all()
        await self.pyro.stop()
        await self.aio_bot.session.close()
        await close_db()


async def main():
    bot = KukuMusic()
    bot.aio_bot.kuku = bot  # expose app-wide
    await bot.startup()
    try:
        await asyncio.gather(idle(), bot.dp.start_polling(bot.aio_bot))
    finally:
        await bot.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
