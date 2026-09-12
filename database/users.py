from datetime import datetime, timedelta
from .database import db


class UsersDB:
    def __init__(self):
        self.col = db.users
        self.history = db.history

    async def ensure_indexes(self):
        await self.col.create_index("user_id", unique=True)
        await self.history.create_index([("user_id", 1), ("played_at", -1)])

    async def add_user(self, user_id: int, name: str = "", username: str = ""):
        await self.col.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "username": username},
             "$setOnInsert": {"joined": datetime.utcnow(), "banned": False, "lang": "en", "streams": 0}},
            upsert=True,
        )

    async def get_user(self, user_id: int):
        return await self.col.find_one({"user_id": user_id}) or {}

    async def ban(self, user_id: int):
        await self.col.update_one({"user_id": user_id}, {"$set": {"banned": True}})

    async def unban(self, user_id: int):
        await self.col.update_one({"user_id": user_id}, {"$set": {"banned": False}})

    async def banned_users(self):
        return [u async for u in self.col.find({"banned": True})]

    async def is_banned(self, user_id: int) -> bool:
        u = await self.col.find_one({"user_id": user_id})
        return bool(u and u.get("banned"))

    async def set_lang(self, user_id: int, lang: str):
        await self.col.update_one({"user_id": user_id}, {"$set": {"lang": lang}})

    async def total(self) -> int:
        return await self.col.count_documents({})

    async def active_since(self, days: int = 7) -> int:
        since = datetime.utcnow() - timedelta(days=days)
        return await self.col.count_documents({"joined": {"$gte": since}})

    async def add_stream(self, user_id: int, title: str, chat_id: int):
        await self.col.update_one({"user_id": user_id}, {"$inc": {"streams": 1}})
        await self.history.insert_one(
            {"user_id": user_id, "title": title, "chat_id": chat_id, "played_at": datetime.utcnow()}
        )

    async def total_streams(self) -> int:
        agg = await self.col.aggregate([{"$group": {"_id": None, "s": {"$sum": "$streams"}}}]).to_list(1)
        return agg[0]["s"] if agg else 0


db_users = UsersDB()
