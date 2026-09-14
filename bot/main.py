import logging
import asyncio

from bot.client import bot, assistant

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

LOGGER = logging.getLogger("KUKU_MUSIC")


async def start_all():
    try:
        await bot.start()
        me = await bot.get_me()

        LOGGER.info(
            f"Bot Started -> @{me.username}"
        )

        await assistant.start()

        ame = await assistant.get_me()

        LOGGER.info(
            f"Assistant Started -> @{ame.username}"
        )

        print("=" * 50)
        print("🎧 KUKU MUSIC STARTED")
        print("=" * 50)

        await asyncio.Event().wait()

    except Exception as e:
        LOGGER.error(e)


if __name__ == "__main__":
    asyncio.run(start_all())
