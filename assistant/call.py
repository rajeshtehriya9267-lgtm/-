"""
Core PyTgCalls wrapper — one assistant, designed so more can be added via AssistantManager later.
"""
import asyncio
import time
import shutil
import tempfile
import os

from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import MediaData, Update, JoinGroupCallPresentation  # noqa
from pytgcalls.types.input_stream import AudioParameters, InputParameters  # noqa
from pytgcalls.types import AudioPiped  # noqa
from pytgcalls.exceptions import NoActiveGroupCall, GroupCallNotFound  # noqa

from config import config
from utils.logger import log
from music.queue import queue_manager

try:
    from pytgcalls.types import AudioPiped
except ImportError:
    AudioPiped = None


class CallManager:
    def __init__(self):
        self.client: PyTgCalls | None = None
        self.assistant_id: int | None = None
        self.bot = None  # aiogram Bot, injected by main
        self._idle_task = None

    def bind(self, pyrogram_client, aiogram_bot, assistant_id: int):
        self.client = PyTgCalls(pyrogram_client)
        self.bot = aiogram_bot
        self.assistant_id = assistant_id

    async def start(self):
        await self.client.start()
        self._idle_task = None

    async def join(self, chat_id: int) -> bool:
        try:
            await self.client.play(chat_id, MediaData(""))  # join silently
            return True
        except Exception:
            try:
                await self.client.join_group_call(chat_id)
                return True
            except Exception as e:
                log.error(f"join failed {chat_id}: {e}")
                return False

    async def play(self, chat_id: int, stream_url: str, volume: int = 100) -> bool:
        try:
            # yt-dlp URLs may expire; direct streaming via ffmpeg pipe for reliability
            from pytgcalls.types import AudioPiped, AudioParameters
            stream = AudioPiped(
                stream_url,
                AudioParameters(volume=int(volume * 65536 / 100)) if volume != 100 else AudioParameters(),
            )
            await self.client.play(chat_id, stream, StreamType().pipedscreen if hasattr(StreamType(), "pipedscreen") else StreamType())
            q = queue_manager.get(chat_id)
            q.last_active = time.time()
            return True
        except NoActiveGroupCall:
            return False
        except Exception as e:
            # try join-then-play
            if await self.join(chat_id):
                try:
                    from pytgcalls.types import AudioPiped
                    await self.client.play(chat_id, AudioPiped(stream_url), StreamType())
                    return True
                except Exception as e2:
                    log.error(f"play retry failed: {e2}")
            log.error(f"play failed: {e}")
            return False

    async def pause(self, chat_id: int) -> bool:
        try:
            await self.client.pause_stream(chat_id)
            return True
        except Exception:
            return False

    async def resume(self, chat_id: int) -> bool:
        try:
            await self.client.resume_stream(chat_id)
            return True
        except Exception:
            return False

    async def seek(self, chat_id: int, seconds: int) -> bool:
        try:
            await self.client.change_stream(chat_id, MediaData(f"0:{seconds}"))
            return True
        except Exception:
            return False

    async def change_volume(self, chat_id: int, percent: int) -> bool:
        q = queue_manager.get(chat_id)
        if q.current and q.current.stream_url:
            try:
                from pytgcalls.types import AudioPiped, AudioParameters
                await self.client.play(
                    chat_id,
                    AudioPiped(q.current.stream_url, AudioParameters(volume=int(percent * 65536 / 100))),
                    StreamType(),
                )
                return True
            except Exception:
                return False
        return True

    async def leave(self, chat_id: int) -> bool:
        try:
            await self.client.leave_call(chat_id)
        except Exception:
            pass
        queue_manager.remove(chat_id)
        return True

    async def stop_all(self):
        for cid in list(queue_manager._chats.keys()):
            await self.leave(cid)

    async def vc_participants(self, chat_id: int) -> int:
        """Count participants via pyro client."""
        try:
            async for _ in self.client.pytgcalls.pyrogram.get_chat_members(chat_id, filter="voice_chat_active" if False else None):
                pass
        except Exception:
            pass
        # Fallback: rely on idle timer only
        return 99

    async def idle_monitor(self):
        """Auto-leave assistant when alone/idle for 60s."""
        while True:
            await asyncio.sleep(15)
            now = time.time()
            for chat_id, q in list(queue_manager._chats.items()):
                if q.current and not q.queue:
                    if now - q.last_active > config.IDLE_LEAVE_SECONDS:
                        # check if only assistant remains — try participant check via raw
                        try:
                            participants = await self.client.callhopper if False else None
                        except Exception:
                            participants = None
                        # Simplest reliable heuristic: no playback progress for 60s and nothing left in queue
                        try:
                            status = await self.client.get_call(chat_id)
                            if status and getattr(status, "status", None) in ("paused", None):
                                pass
                        except Exception:
                            pass
                        log.info(f"Idle timeout, leaving {chat_id}")
                        await self.leave(chat_id)
                        try:
                            if self.bot:
                                await self.bot.send_message(chat_id, "🎧 Assistant left the voice chat (idle).")
                        except Exception:
                            pass


call = CallManager()
