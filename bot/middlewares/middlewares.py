from aiogram import BaseMiddleware
from database.users import db_users


class UserTrackingMiddleware(BaseMiddleware):
    """Registers every user & chat, blocks banned users + maintenance mode."""

    def __init__(self, maintenance_flag: dict):
        self.maintenance = maintenance_flag

    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        msg = getattr(event, "message", None) or getattr(event, "callback_query", None)
        if user and not user.is_bot:
            name = user.first_name or ""
            uname = user.username or ""
            await db_users.add_user(user.id, name, uname)
            if await db_users.is_banned(user.id) and not (hasattr(event, "text") and str(getattr(event, "text", "")).startswith("/start")):
                if isinstance(msg, object) and hasattr(msg, "answer"):
                    pass
                return  # silently block banned users
        # maintenance mode: only owner/sudo pass
        if self.maintenance.get("enabled") and user:
            from utils.helpers import is_sudo
            if not is_sudo(user.id):
                text = self.maintenance.get("message") or "🛠 Bot under maintenance."
                if hasattr(event, "answer"):
                    await event.answer(text)
                return
        return await handler(event, data)
