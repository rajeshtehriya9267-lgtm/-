from motor.motor_asyncio import AsyncIOMotorClient
from config import config

_client: AsyncIOMotorClient = None


def get_db():
    """Har jagah ye function se database lo — connection ready hone ke baad."""
    global _client
    if _client is None:
        raise RuntimeError("Database not initialized yet!")
    return _client.get_default_db()


async def init_db():
    global _client
    _client = AsyncIOMotorClient(config.MONGO_DB_URI)
    await _client.admin.command("ping")


async def close_db():
    if _client:
        _client.close()
        _client = None
