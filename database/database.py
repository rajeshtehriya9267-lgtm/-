from motor.motor_asyncio import AsyncIOMotorClient
from config import config

_client: AsyncIOMotorClient = None
db = None


async def init_db():
    global _client, db
    _client = AsyncIOMotorClient(config.MONGO_DB_URI)
    db = _client.get_default_db()
    await _client.admin.command("ping")


async def close_db():
    if _client:
        _client.close()
