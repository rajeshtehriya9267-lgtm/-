from aiogram.types import CallbackQuery, Message
from config import config
from database.admins import db_admins
from database.users import db_users
from utils.helpers import is_sudo


async def check_admin(message_or_cb, user_id: int = None) -> bool:
    user_id = user_id or message_or_cb.from_user.id
    if is_sudo(user_id):
        return True
    if await db_admins.is_admin(user_id):
        return True
    # chat admin check
    msg = message_or_cb.message if isinstance(message_or_cb, CallbackQuery) else message_or_cb
    if msg and getattr(msg, "chat", None) and msg.chat.type in ("group", "supergroup"):
        try:
            member = await msg.chat.get_member(user_id)
            return member.status in ("administrator", "creator")
        except Exception:
            return False
    return False


async def check_user_allowed(cb: CallbackQuery) -> bool:
    if await db_users.is_banned(cb.from_user.id):
        await cb.answer("🚫 You are banned from using this bot.", show_alert=True)
        return False
    return True


RATE_WINDOW = 5  # seconds
_rate: dict = {}


def rate_limited(user_id: int) -> bool:
    import time
    now = time.time()
    last = _rate.get(user_id, 0)
    if now - last < 1.0:  # 1 msg/sec anti-spam
        return True
    _rate[user_id] = now
    # prune
    if len(_rate) > 5000:
        _rate.clear()
    return False
