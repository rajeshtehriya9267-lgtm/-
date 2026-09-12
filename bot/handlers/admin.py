"""
Hidden admin panel — only OWNER, SUDO_USERS and DB admins can access.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import config
from database.admins import db_admins
from database.users import db_users
from database.settings import db_settings
from bot.keyboards.inline import admin_panel, back_button, confirm_reset
from utils.helpers import is_sudo
from utils.logger import log

router = Router(name="admin")

_admin_state: dict[int, dict] = {}  # per-admin flow state


def guard(func):
    async def wrapper(event, *a, **kw):
        user = event.from_user
        if not (is_sudo(user.id) or await db_admins.is_admin(user.id)):
            if isinstance(event, CallbackQuery):
                await cb_silent_deny(event)
            return
        return await func(event, *a, **kw)
    return wrapper


async def cb_silent_deny(cb: CallbackQuery):
    await cb.answer("🚫 Access denied.", show_alert=True)


@router.message(Command("admin"))
async def admin_cmd(m: Message):
    if not (is_sudo(m.from_user.id) or await db_admins.is_admin(m.from_user.id)):
        return  # completely hidden from normal users
    await m.answer(
        "╭━ ⚙️ <b>𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋</b> ━╮\n\n🛡 Select an option below.\n\n╰━━━━━━━━━━━╯",
        reply_markup=admin_panel(),
    )


@router.callback_query(F.data == "adm home")
@admin_guard_cb
async def adm_home(cb: CallbackQuery):
    await cb.message.edit_text("⚙️ <b>𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋</b>", reply_markup=admin_panel())


def admin_guard_cb(func):
    async def wrapper(cb: CallbackQuery, *a, **kw):
        if not (is_sudo(cb.from_user.id) or await db_admins.is_admin(cb.from_user.id)):
            await cb.answer("🚫 Access denied.", show_alert=True)
            return
        return await func(cb, *a, **kw)
    return wrapper


# ---- Welcome settings ----
@router.callback_query(F.data == "adm welcome")
@admin_guard_cb
async def adm_welcome(cb: CallbackQuery):
    s = await db_settings.get(cb.from_user.id)
    w = s["welcome"]
    await cb.message.edit_text(
        f"👋 <b>Welcome Settings</b>\n\n"
        f"Mode: <b>{w['mode']}</b>\n"
        f"Text: <code>{(w['text'] or 'Default')[:100]}</code>\n\n"
        "Send me:\n"
        "• Text → set welcome text\n"
        "• Photo/Video → set welcome media\n\n"
        "Buttons: /welcome_save /welcome_preview /welcome_reset",
        reply_markup=back_button(),
    )
    _admin_state[cb.from_user.id] = {"flow": "welcome"}


@router.callback_query(F.data == "adm wreset yes")
@admin_guard_cb
async def adm_wreset(cb: CallbackQuery):
    await db_settings.update(cb.from_user.id, "welcome", dict(await db_settings.get(1) and {
        "enabled": True, "mode": "text", "text": None, "photo": None, "video": None, "caption": None,
    }))
    await cb.message.edit_text("✅ Welcome reset to default.", reply_markup=back_button())


# ---- Force Subscribe ----
@router.callback_query(F.data == "adm fsub")
@admin_guard_cb
async def adm_fsub(cb: CallbackQuery):
    s = await db_settings.get(cb.from_user.id)
    f = s["fsub"]
    ch = "\n".join(f"• {c}" for c in f["channels"]) or "None"
    await cb.message.edit_text(
        f"🔒 <b>Force Subscribe</b>\n\nStatus: <b>{'ON' if f['enabled'] else 'OFF'}</b>\nChannels:\n{ch}\n\n"
        "Use /fsub_add @channel, /fsub_del @channel, /fsub_on, /fsub_off",
        reply_markup=back_button(),
    )


@router.message(Command("fsub_add"))
async def fsub_add(m: Message):
    if not is_sudo(m.from_user.id):
        return
    s = await db_settings.get(m.chat.id)
    f = s["fsub"]
    if len(m.text.split()) > 1:
        f["channels"].append(m.text.split()[1])
        await db_settings.update(m.chat.id, "fsub", f)
    await m.reply("✅ Channel added to ForceSub.")


@router.message(Command("fsub_on"))
async def fsub_on(m: Message):
    if not is_sudo(m.from_user.id):
        return
    s = await db_settings.get(m.chat.id)
    f = s["fsub"]; f["enabled"] = True
    await db_settings.update(m.chat.id, "fsub", f)
    await m.reply("🔒 ForceSub enabled.")


@router.message(Command("fsub_off"))
async def fsub_off(m: Message):
    if not is_sudo(m.from_user.id):
        return
    s = await db_settings.get(m.chat.id)
    f = s["fsub"]; f["enabled"] = False
    await db_settings.update(m.chat.id, "fsub", f)
    await m.reply("🔓 ForceSub disabled.")


# ---- Maintenance ----
@router.callback_query(F.data == "adm maint")
@admin_guard_cb
async def adm_maint(cb: CallbackQuery):
    s = await db_settings.get(cb.from_user.id)
    mt = s["maintenance"]
    await cb.message.edit_text(
        f"🛠 <b>Maintenance Mode</b>\n\nStatus: <b>{'ON' if mt['enabled'] else 'OFF'}</b>\n"
        f"Message: <i>{mt['message']}</i>\n\nUse /maintenance_on, /maintenance_off, /maintenance_msg <text>",
        reply_markup=back_button(),
    )


@router.message(Command("maintenance_on"))
async def maint_on(m: Message):
    if not is_sudo(m.from_user.id):
        return
    s = await db_settings.get(config.OWNER_ID)
    mt = s["maintenance"]; mt["enabled"] = True
    await db_settings.update(config.OWNER_ID, "maintenance", mt)
    await m.reply("🛠 Maintenance mode <b>ENABLED</b>. Only owner/sudo can use the bot.")
    log.info("Maintenance ON")


@router.message(Command("maintenance_off"))
async def maint_off(m: Message):
    if not is_sudo(m.from_user.id):
        return
    s = await db_settings.get(config.OWNER_ID)
    mt = s["maintenance"]; mt["enabled"] = False
    await db_settings.update(config.OWNER_ID, "maintenance", mt)
    await m.reply("✅ Maintenance mode <b>DISABLED</b>.")


# ---- User management / bans ----
@router.message(Command("ban"))
async def ban_user(m: Message):
    if not (is_sudo(m.from_user.id)):
        return
    if m.reply_to_message:
        uid = m.reply_to_message.from_user.id
    elif len(m.text.split()) > 1 and m.text.split()[1].lstrip("-").isdigit():
        uid = int(m.text.split()[1])
    else:
        await m.reply("Usage: reply to user or /ban <user_id>")
        return
    await db_users.ban(uid)
    await m.reply(f"🚫 <b>Banned:</b> <code>{uid}</code>")
    log.info(f"Ban: {uid}")


@router.message(Command("unban"))
async def unban_user(m: Message):
    if not is_sudo(m.from_user.id):
        return
    if len(m.text.split()) > 1 and m.text.split()[1].lstrip("-").isdigit():
        uid = int(m.text.split()[1])
        await db_users.unban(uid)
        await m.reply(f"✅ <b>Unbanned:</b> <code>{uid}</code>")


@router.message(Command("banned"))
async def banned_list(m: Message):
    if not is_sudo(m.from_user.id):
        return
    users = await db_users.banned_users()
    text = "🚫 <b>Banned Users:</b>\n\n" + "\n".join(f"• <code>{u['user_id']}</code> {u.get('name','')}" for u in users[:30]) if users else "No banned users."
    await m.reply(text)


# ---- Admin management ----
@router.message(Command("addadmin"))
async def add_admin(m: Message):
    if not is_sudo(m.from_user.id):
        return
    if len(m.text.split()) > 1 and m.text.split()[1].lstrip("-").isdigit():
        uid = int(m.text.split()[1])
        await db_admins.add(uid)
        await m.reply(f"🛡 <b>Admin added:</b> <code>{uid}</code>")


@router.message(Command("deladmin"))
async def del_admin(m: Message):
    if not is_sudo(m.from_user.id):
        return
    if len(m.text.split()) > 1 and m.text.split()[1].lstrip("-").isdigit():
        uid = int(m.text.split()[1])
        await db_admins.remove(uid)
        await m.reply(f"🗑 <b>Admin removed:</b> <code>{uid}</code>")


# ---- Statistics ----
@router.callback_query(F.data == "adm stats")
@admin_guard_cb
async def adm_stats(cb: CallbackQuery):
    from main import START_TIME  # circular-safe in practice via lazy import
    import time as _t
    users = await db_users.total()
    active = await db_users.active_since(7)
    streams = await db_users.total_streams()
    up = int(_t.time() - START_TIME)
    h, rem = divmod(up, 3600); mn, sec = divmod(rem, 60)
    await cb.message.edit_text(
        f"╭━ 📊 <b>𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒</b> ━╮\n\n"
        f"👥 Total Users: <b>{users}</b>\n"
        f"🟢 Active (7d): <b>{active}</b>\n"
        f"🎵 Streams Played: <b>{streams}</b>\n"
        f"⏰ Uptime: <b>{h}h {mn}m {sec}s</b>\n\n"
        f"╰━━━━━━━━━━━╯",
        reply_markup=back_button(),
    )


# ---- Broadcast ----
@router.message(Command("broadcast"))
async def broadcast(m: Message):
    if not is_sudo(m.from_user.id):
        return
    import asyncio
    from database.database import db
    if m.reply_to_message:
        src = m.reply_to_message
        ids = [u["user_id"] async for u in db.users.find({})]
        sent = 0
        status = await m.reply(f"📢 Broadcasting to {len(ids)} users...")
        for uid in ids:
            try:
                await src.copy_to(uid)
                sent += 1
            except Exception:
                pass
            if sent % 20 == 0:
                await status.edit_text(f"📢 Sent: {sent}/{len(ids)}")
            await asyncio.sleep(0.08)
        await status.edit_text(f"✅ <b>Broadcast complete:</b> {sent}/{len(ids)}")
    else:
        await m.reply("Reply to a message with /broadcast to send it to all users.")
