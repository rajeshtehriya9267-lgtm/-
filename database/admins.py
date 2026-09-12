from .database import get_db


class AdminsDB:
    # ✅ Fix: __init__ ki jagah property
    @property
    def col(self):
        return get_db().admins

    async def add(self, user_id: int):
        await self.col.update_one({"user_id": user_id}, {"$set": {"admin": True}}, upsert=True)

    async def remove(self, user_id: int):
        await self.col.delete_one({"user_id": user_id})

    async def all_ids(self) -> list[int]:
        return [a["user_id"] async for a in self.col.find({})]

    async def is_admin(self, user_id: int) -> bool:
        return bool(await self.col.find_one({"user_id": user_id}))


db_admins = AdminsDB()
