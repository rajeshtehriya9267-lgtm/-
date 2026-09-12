import time
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from music.queue import queue_manager
from music.controls import do_pause, do_resume, do_skip, do_stop, do_seek, set_volume, elapsed
from music.player import send_now_playing
from utils.permissions import check_admin, rate_limited
from utils.helpers import now_playing_card, fmt_time
from utils.logger import log

router = Router(name="controls")


def _fmt_card(chat_id):
    q = queue_manager.get(chat_id)
    t = q.current
    loop = "track" if q.loop_track else ("queue" if q.loop_queue else "off")
    return now_playing_card(
        t.title, t.requester_name, t.duration, 1, len(q.queue), loop, q.volume, elapsed(chat_id)
    )


@router.message(F.text & F.text.startswith(("/pause", "/resume", "/skip", "/stop", "/shuffle")))
async def control_cmd(m: Message):
    if rate_limited(m.from_user.id):
        return
    if not await check_admin(m):
        await m.reply("🚫 Admins only.")
        return
    chat_id = m.chat.id
    cmd = m.text.split()[0].lstrip("/").split("@")[0]
    q = queue_manager.get(chat_id)

    if cmd == "pause":
        ok = await do_pause(chat_id)
        await m.reply("⏸ <b>Paused</b>" if ok else "❌ Nothing playing.")
    elif cmd == "resume":
        ok = await do_resume(chat_id)
        await m.reply("▶️ <b>Resumed</b>" if ok else "❌ Nothing paused.")
    elif cmd == "skip":
        ok = await do_skip(chat_id)
        if ok and q.current:
            await m.reply_photo(q.current.thumbnail or "https://i.ibb.co/5R7wW9Q/music.png", caption=_fmt_card(chat_id), reply_markup=None)
    elif cmd == "stop":
        await do_stop(chat_id)
        await m.reply("⏹ <b>Playback stopped. Queue cleared. Assistant left.</b>")
    elif cmd == "shuffle":
        n = queue_manager.shuffle(chat_id)
        await m.reply(f"🔀 <b>Shuffled</b> {n} songs!")


@router.message(F.text & F.text.startswith(("/seek", "/volume", "/loop", "/queue", "/lyrics")))
async def misc_control_cmd(m: Message):
    if rate_limited(m.from_user.id):
        return
    if not await check_admin(m):
        await m.reply("🚫 Admins only.")
        return
    chat_id = m.chat.id
    parts = m.text.split()
    cmd = parts[0].lstrip("/").split("@")[0]
    q = queue_manager.get(chat_id)

    if cmd == "seek":
        if len(parts) < 2 or not parts[1].isdigit():
            await m.reply("⏩ <b>Usage:</b> <code>/seek 30</code> (seconds)")
            return
        ok = await do_seek(chat_id, int(parts[1]))
        await m.reply(f"⏩ <b>Seeked to</b> {parts[1]}s" if ok else "❌ Seek failed.")
    elif cmd == "volume":
        if len(parts) < 2 or not parts[1].isdigit():
            await m.reply(f"🔊 <b>Current volume:</b> {q.volume}%\n<b>Usage:</b> <code>/volume 80</code> (1–200)")
            return
        v = await set_volume(chat_id, int(parts[1]))
        await m.reply(f"🔊 <b>Volume set to</b> {v}%")
    elif cmd == "loop":
        arg = parts[1].lower() if len(parts) > 1 else "track"
        if arg == "queue":
            q.loop_queue = not q.loop_queue
            await m.reply(f"🔁 <b>Queue loop:</b> {'Enabled' if q.loop_queue else 'Disabled'}")
        else:
            q.loop_track = not q.loop_track
            await m.reply(f"🔁 <b>Track loop:</b> {'Enabled' if q.loop_track else 'Disabled'}")
    elif cmd == "queue":
        if not q.queue and not q.current:
            await m.reply("📋 <b>Queue is empty.</b>")
            return
        text = "╭━ 📋 <b>𝐐𝐔𝐄𝐔𝐄</b> ━╮\n\n"
        if q.current:
            text += f"▶️ <b>Now:</b> {q.current.title}\n\n"
        for i, t in enumerate(q.queue[:15], 1):
            text += f"<code>{i}.</code> {t.title} ({t.duration})\n"
        if len(q.queue) > 15:
            text += f"\n… and {len(q.queue) - 15} more"
        text += f"\n╰━━ 🎵 <b>Total:</b> {len(q.queue)} ━━╯"
        await m.reply(text)
    elif cmd == "lyrics":
        if not q.current:
            await m.reply("❌ Nothing playing.")
            return
        await m.reply(f"🎤 <b>Lyrics for:</b> {q.current.title}\n\n🔎 Use /lyrics on @LyricsBot or search:\n{q.current.link}")


# ---------- Inline button callbacks ----------
@router.callback_query(F.data.startswith("pp "))
async def playback_cb(cb: CallbackQuery):
    from utils.permissions import check_admin
    if not await check_admin(cb):
        await cb.answer("🚫 Admins only.", show_alert=True)
        return
    _, action, cid = cb.data.split()
    chat_id = int(cid)
    q = queue_manager.get(chat_id)

    if action == "pause":
        ok = await do_pause(chat_id)
        await cb.answer("⏸ Paused" if ok else "❌")
    elif action == "resume":
        ok = await do_resume(chat_id)
        await cb.answer("▶️ Resumed" if ok else "❌")
    elif action == "skip":
        ok = await do_skip(chat_id)
        await cb.answer("⏭ Skipped" if ok else "Queue empty — leaving VC")
        if ok and q.current:
            try:
                await cb.message.edit_caption(caption=_fmt_card(chat_id))
            except Exception:
                pass
    elif action == "stop":
        await do_stop(chat_id)
        await cb.answer("⏹ Stopped")
        try:
            await cb.message.edit_text("⏹ <b>Playback stopped. Assistant left.</b>")
        except Exception:
            pass
    elif action == "loop":
        if cb.message.reply_markup and any(b.text == "🔁 Loop" for row in cb.message.reply_markup.inline_keyboard for b in row):
            q.loop_track = not q.loop_track
        await cb.answer(f"🔁 Track loop {'ON' if q.loop_track else 'OFF'}")
        try:
            await cb.message.edit_caption(caption=_fmt_card(chat_id))
        except Exception:
            pass
    elif action == "shuffle":
        n = queue_manager.shuffle(chat_id)
        await cb.answer(f"🔀 Shuffled {n} songs")
    elif action == "vdown":
        v = await set_volume(chat_id, q.volume - 10)
        await cb.answer(f"🔊 Volume: {v}%")
        try:
            await cb.message.edit_caption(caption=_fmt_card(chat_id))
        except Exception:
            pass
    elif action == "vup":
        v = await set_volume(chat_id, q.volume + 10)
        await cb.answer(f"🔊 Volume: {v}%")
        try:
            await cb.message.edit_caption(caption=_fmt_card(chat_id))
        except Exception:
            pass
    elif action == "queue":
        text = "📋 <b>Queue:</b>\n\n"
        for i, t in enumerate(q.queue[:10], 1):
            text += f"<code>{i}.</code> {t.title}\n"
        if not q.queue:
            text += "Empty."
        await cb.answer()
        try:
            await cb.message.reply(text)
        except Exception:
            pass
    elif action == "lyrics":
        await cb.answer("🎤 Check lyrics link in chat")
        try:
            await cb.message.reply(f"🎤 {q.current.title}\n{q.current.link}" if q.current else "❌ Nothing playing.")
        except Exception:
            pass
    elif action == "settings":
        await cb.answer(f"🔊 {q.volume}% | 🔁 Loop: {'Track' if q.loop_track else 'Queue' if q.loop_queue else 'Off'}", show_alert=True)
