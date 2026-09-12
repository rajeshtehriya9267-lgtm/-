from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B
from config import config


def playback_buttons(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="⏸ Pause", callback_data=f"pp pause {chat_id}"),
         B(text="▶️ Resume", callback_data=f"pp resume {chat_id}"),
         B(text="⏭ Skip", callback_data=f"pp skip {chat_id}")],
        [B(text="⏹ Stop", callback_data=f"pp stop {chat_id}"),
         B(text="🔁 Loop", callback_data=f"pp loop {chat_id}"),
         B(text="🔀 Shuffle", callback_data=f"pp shuffle {chat_id}")],
        [B(text="📋 Queue", callback_data=f"pp queue {chat_id}"),
         B(text="🎵 Lyrics", callback_data=f"pp lyrics {chat_id}"),
         B(text="⚙ Settings", callback_data=f"pp settings {chat_id}")],
        [B(text="🔉 Volume -", callback_data=f"pp vdown {chat_id}"),
         B(text="🔊 Volume +", callback_data=f"pp vup {chat_id}")],
    ])


def start_buttons(support: str, channel: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="🎵 Play Music", url=f"https://t.me/{config.BOT_USERNAME.lstrip('@')}?start=play"),
         B(text="📋 Commands", callback_data="cmds")],
        [B(text="👑 Owner", url=f"https://t.me/{config.OWNER_USERNAME.lstrip('@')}"),
         B(text="💬 Support", url=support)],
        [B(text="📢 Channel", url=channel),
         B(text="⚙ Language", callback_data="lang")],
    ])


def admin_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="👋 Welcome", callback_data="adm welcome"), B(text="🔒 ForceSub", callback_data="adm fsub")],
        [B(text="👥 Users", callback_data="adm users"), B(text="🚫 Ban/Unban", callback_data="adm bans")],
        [B(text="🛠 Maintenance", callback_data="adm maint"), B(text="📢 Broadcast", callback_data="adm bcast")],
        [B(text="🛡 Admins", callback_data="adm admins"), B(text="🌐 Language", callback_data="adm lang")],
        [B(text="📊 Statistics", callback_data="adm stats")],
    ])


def back_button(cb: str = "adm home") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text="◀️ Back", callback_data=cb)]])


def language_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="🇬🇧 English", callback_data="lang en"), B(text="🇮🇳 हिंदी", callback_data="lang hi")],
    ])


def confirm_reset() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="✅ Confirm", callback_data="adm wreset yes"), B(text="❌ Cancel", callback_data="adm home")],
    ])
