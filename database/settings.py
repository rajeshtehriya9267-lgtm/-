from .database import db

DEFAULTS = {
    "welcome": {"enabled": True, "mode": "text", "text": None, "photo": None, "video": None, "caption": None},
    "fsub": {"enabled": False, "channels": []},
    "maintenance": {"enabled": False, "message": "⚠️ Bot under maintenance. Please try later."},
}


class SettingsDB:
    def __init__(self):
        self.col = db.settings
        self.playlists = db.playlists

    async def get(self, chat_id: int) -> dict:
        doc = await self.col.find_one({"chat_id": chat_id})
        if not doc:
            doc = {"chat_id": chat_id, **DEFAULTS}
            await self.col.insert_one(doc)
        return doc

    async def update(self, chat_id: int, key: str, value: dict):
        await self.col.update_one({"chat_id": chat_id}, {"$set": {key: value}}, upsert=True)

    # Saved user playlists
    async def save_playlist(self, user_id: int, name: str, tracks: list):
        await self.playlists.update_one(
            {"user_id": user_id, "name": name}, {"$set": {"tracks": tracks, "saved_at": __import__("datetime").datetime.utcnow()}},
            upsert=True,
        )

    async def load_playlist(self, user_id: int, name: str):
        return await self.playlists.find_one({"user_id": user_id, "name": name})

    async def user_playlists(self, user_id: int):
        return [p async for p in self.playlists.find({"user_id": user_id})]


db_settings = SettingsDB()
