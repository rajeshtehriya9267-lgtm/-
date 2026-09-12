from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums.chat_type import ChatType

from config import config
from music.player import resolve, play_now, send_now_playing, handle_playlist, ensure_assistant
from music.queue import queue_manager
from music.playlist import playlist_info
from bot.keyboards.inline import playback_buttons
from utils.permissions import check_admin, rate_limited
from utils.logger import log

router = Router(name="play")


async def precheck(m: Message) -> bool:
    if rate_limited(m.from_user.id):
        return False
    if not await check_admin(m):
        await m.reply("🚫 <b>You need to be an admin to play music.</b>")
        return False
    return True


@router.message(F.text & F.text.startswith(("/play", "/vplay", "/song")))
async def play_cmd(m: Message):
    if not await precheck(m):
        return
    if m.chat.type == ChatType.PRIVATE:
        await m.reply("🎧 Add me to a group and use /play there!")
        return

    query = m.text.split(" ", 1)[1].strip() if " " in m.text else None
    if not query and m.reply_to_message and m.reply_to_message.audio:
        a = m.reply_to_message.audio
        query = a.title or a.file_name
    if not query:
        await m.reply("🎵 <b>Usage:</b> <code>/play [song name or YouTube URL]</code>")
        return

    status = await m.reply("🔍 <b>𝐒𝐄𝐀𝐑𝐂𝐇𝐈𝐍𝐆...</b>")

    # Playlist URL support
    if "list=" in query or "/playlist" in query:
        info = await playlist_info(query)
        if info:
            count = await handle_playlist(m.chat.id, query, m)
            await status.edit_text(f"📋 <b>Playlist imported:</b> {count} songs queued!\n🎵 <b>Starting first track...</b>")
            q = queue_manager.get(m.chat.id)
            if not q.current:
                await start_next(m.chat.id)
            return

    track = await resolve(query, m)
    if not track:
        await status.edit_text("❌ <b>No results found!</b> Try another query.")
        return

    q = queue_manager.get(m.chat.id)
    pos = queue_manager.add(m.chat.id, track)
    if q.current:
        await status.edit_text(
            f"✅ <b>Added to queue</b> at position #{pos}\n🎵 {track.title}\n⏱ {track.duration}"
        )
    else:
        aid = await ensure_assistant(m.chat.id)
        if not aid:
            await status.edit_text(
                "❌ <b>Cannot start playback!</b>\n\n"
                "Make sure:\n"
                "• I'm an admin in this chat\n"
                f"• Assistant {config.ASSISTANT_NAME} is a member of this group\n"
                "• Voice chat is active"
            )
            return
        await play_now(m.chat.id, track)
        await send_now_playing(m.chat.id, m)


async def start_next(chat_id: int):
    from music.controls import do_skip
    await do_skip(chat_id)
