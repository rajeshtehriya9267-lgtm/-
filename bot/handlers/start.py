from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from config import config
from bot.keyboards.inline import start_buttons, language_buttons
from database.settings import db_settings

router = Router(name="start")

START_TEXT = f"""╭━━━ 🎧 𝐊𝐔𝐊𝐔 𝐌𝐔𝐒𝐈𝐂 🎧 ━━━╮

✨ <b>Welcome to the Premium Music Experience</b> ✨

⚡ High Quality VC Streaming
🎵 YouTube & YouTube Music Support
📋 Smart Queue Management
🔁 Loop & Shuffle Modes
🔊 Volume Control
🖼 Beautiful Now Playing Cards

👑 <b>Owner:</b> {config.OWNER_NAME}
🛡 <b>Bot:</b> {config.BOT_USERNAME}

╰━━━━━━━━━━━━━━━━━━╯"""


@router.message(CommandStart())
async def start_cmd(m: Message):
    await m.answer_photo(
        "https://envs.sh/GRhJ.jpg" if False else "https://te.legra.ph/file/2d2936b1c00a1c14b0d3a.jpg",
        caption=START_TEXT,
        reply_markup=start_buttons(config.SUPPORT_GROUP, config.SUPPORT_CHANNEL),
    )


@router.message(Command("commands", "help"))
async def commands_cmd(m: Message):
    await m.answer(
        "╭━ 📋 <b>𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒</b> ━╮\n\n"
        "▶️ /play — Play song by name/URL\n"
        "📹 /vplay — Play video stream\n"
        "⏸ /pause — Pause playback\n"
        "▶️ /resume — Resume playback\n"
        "⏭ /skip — Skip current song\n"
        "⏹ /stop — Stop & clear queue\n"
        "⏩ /seek — Seek seconds\n"
        "🔊 /volume — Set volume 1–200\n"
        "📋 /queue — View queue\n"
        "🔀 /shuffle — Shuffle queue\n"
        "🔁 /loop — Loop track/queue\n"
        "🎤 /lyrics — Song lyrics\n"
        "🏓 /ping — Bot latency\n"
        "📊 /stats — Bot statistics\n"
        "⏰ /uptime — Bot uptime\n\n"
        "╰━━━━━━━━━━━━╯"
    )


@router.callback_query(F.data == "cmds")
async def cmds_cb(cb: CallbackQuery):
    await cb.message.edit_text("📋 Use /commands to see all commands.")
    await cb.answer()


@router.callback_query(F.data == "lang")
async def lang_cb(cb: CallbackQuery, db_settings=db_settings):
    await cb.message.reply("🌐 Choose your language:", reply_markup=language_buttons())
    await cb.answer()


@router.callback_query(F.data.startswith("lang en"))
async def lang_en(cb: CallbackQuery):
    await db_settings.update(cb.from_user.id, "user_lang", {"lang": "en"})
    await cb.message.edit_text("🇬🇧 Language set to English!")
    await cb.answer()


@router.callback_query(F.data.startswith("lang hi"))
async def lang_hi(cb: CallbackQuery):
    await db_settings.update(cb.from_user.id, "user_lang", {"lang": "hi"})
    await cb.message.edit_text("🇮🇳 भाषा हिंदी में बदल दी गई!")
    await cb.answer()
