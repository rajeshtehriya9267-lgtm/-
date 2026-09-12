import time
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config import config
from music.queue import queue_manager

router = Router(name="misc")
START_TIME = time.time()


@router.message(Command("ping"))
async def ping(m: Message):
    t = time.perf_counter()
    msg = await m.reply("🏓 𝐏𝐎𝐍𝐆...")
    ms = (time.perf_counter() - t) * 1000
    await msg.edit_text(f"🏓 <b>Pong!</b> <code>{ms:.0f} ms</code>")


@router.message(Command("uptime"))
async def uptime(m: Message):
    up = int(time.time() - START_TIME)
    h, rem = divmod(up, 3600)
    mn, s = divmod(rem, 60)
    await m.reply(f"⏰ <b>Uptime:</b> {h}h {mn}m {s}s")


@router.message(Command("stats"))
async def stats(m: Message):
    from database.users import db_users
    from music.queue import queue_manager as qm
    users = await db_users.total()
    streams = await db_users.total_streams()
    active_vcs = len(qm._chats)
    up = int(time.time() - START_TIME)
    h, rem = divmod(up, 3600)
    mn, s = divmod(rem, 60)
    await m.reply(
        f"╭━ 📊 <b>𝐒𝐓𝐀𝐓𝐒</b> ━╮\n\n"
        f"👥 Users: <b>{users}</b>\n"
        f"🎵 Streams: <b>{streams}</b>\n"
        f"🎙 Active VCs: <b>{active_vcs}</b>\n"
        f"⏰ Uptime: <b>{h}h {mn}m</b>\n\n"
        f"╰━━━━━━━━╯"
    )
