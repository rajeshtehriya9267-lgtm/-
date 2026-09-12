import time
from pyrogram.types import Message
from aiogram.types import CallbackQuery

from config import config
from assistant.call import call
from assistant.manager import assistant
from music.queue import queue_manager, Track
from music.search import search_youtube, get_playlist_entries
from utils.helpers import now_playing_card, fmt_time, parse_duration
from utils.logger import log
from database.users import db_users
from bot.keyboards.inline import playback_buttons


async def resolve(query: str, requester: Message | CallbackQuery) -> Track | None:
    info = await search_youtube(query)
    if not info:
        return None
    return Track(
        title=info["title"],
        stream_url=info["stream_url"],
        duration=info["duration_str"],
        duration_sec=info["duration"],
        thumbnail=info["thumbnail"],
        requester_id=requester.from_user.id,
        requester_name=f"<a href='tg://user?id={requester.from_user.id}'>{requester.from_user.first_name}</a>",
        link=info["webpage_url"],
    )


async def ensure_assistant(chat_id: int) -> int | None:
    """Get assistant user id, ensure bot admin perms + VC exists."""
    uid = await assistant.get_assistant_id()
    if not uid:
        return None
    try:
        member = await call.bot.get_chat_member(chat_id, (await call.bot.me()).id)
        if member.status not in ("administrator", "creator"):
            return None
    except Exception:
        return None
    return uid


async def play_now(chat_id: int, track: Track, edit_message=None):
    q = queue_manager.get(chat_id)
    async with q.lock:
        q.current = track
        q.started_at = time.time()
        q.last_active = time.time()
    ok = await call.play(chat_id, track.stream_url, q.volume)
    if not ok:
        log.error(f"Failed to play in {chat_id}")
        return
    await db_users.add_stream(track.requester_id, track.title, chat_id)
    text = now_playing_card(
        track.title, track.requester_name, track.duration,
        1, len(q.queue), "track" if q.loop_track else ("queue" if q.loop_queue else "off"),
        q.volume, 0,
    )
    if edit_message:
        try:
            await edit_message.edit_text(text, disable_web_page_preview=True)
        except Exception:
            pass


async def send_now_playing(chat_id: int, send_to):
    q = queue_manager.get(chat_id)
    if not q.current:
        return
    elapsed = time.time() - q.started_at if q.started_at else 0
    text = now_playing_card(
        q.current.title, q.current.requester_name, q.current.duration,
        1, len(q.queue), "track" if q.loop_track else ("queue" if q.loop_queue else "off"),
        q.volume, elapsed,
    )
    try:
        msg = await send_to.reply_photo(q.current.thumbnail, caption=text, reply_markup=playback_buttons(chat_id))
        q.message = msg
    except Exception:
        try:
            q.message = await send_to.reply(text, disable_web_page_preview=True, reply_markup=playback_buttons(chat_id))
        except Exception:
            pass


async def handle_playlist(chat_id: int, url: str, requester: Message, max_items: int = 25):
    entries = await get_playlist_entries(url)
    if not entries:
        return 0
    q = queue_manager.get(chat_id)
    for e in entries[:max_items]:
        q.queue.append(Track(
            title=e["title"], stream_url="", duration=fmt_time(e["duration"]),
            duration_sec=e["duration"], thumbnail="", link=e["url"],
            requester_id=requester.from_user.id,
            requester_name=f"@{requester.from_user.username}" if requester.from_user.username else requester.from_user.first_name,
        ))
    return len(entries[:max_items])
