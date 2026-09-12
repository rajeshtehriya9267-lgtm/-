import asyncio
import time

from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioParameters, StreamType
from pytgcalls.exceptions import NoActiveGroupCall

from config import config
from utils.logger import log
from music.queue import queue_manager


class CallManager:
    def __init__(self):
        self.client: PyTgCalls | None = None
        self.bot = None

    def bind(self, pyrogram_client, aiogram_bot, assistant_id: int):
        self.client = PyTgCalls(pyrogram_client)
        self.bot = aiogram_bot

    async def start(self):
        await self.client.start()

    async def play(self, chat_id: int, stream_url: str, volume: int = 100) -> bool:
        try:
            stream = AudioPiped(
                stream_url,
                AudioParameters(
                    quality=48000,
                    volume=volume / 100,
                ),
            )
            await self.client.play(chat_id, stream)
            queue_manager.get(chat_id).last_active = time.time()
            return True
        except NoActiveGroupCall:
            log.error(f"No active group call in {chat_id}")
            return False
        except Exception as e:
            log.error(f"play failed in {chat_id}: {e}")
            return False

    async def pause(self, chat_id: int) -> bool:
        try:
            await self.client.pause(chat_id)
            return True
        except Exception:
            return False

    async def resume(self, chat_id: int) -> bool:
        try:
            await self.client.resume(chat_id)
            return True
        except Exception:
            return False

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

    async def idle_monitor(self):
        """Auto-leave when queue is empty and idle for 60s."""
        while True:
            await asyncio.sleep(15)
            now = time.time()
            for chat_id, q in list(queue_manager._chats.items()):
                if q.current and not q.queue and now - q.last_active > config.IDLE_LEAVE_SECONDS:
                    log.info(f"Idle timeout, leaving {chat_id}")
                    await self.leave(chat_id)
                    try:
                        await self.bot.send_message(chat_id, "🎧 Assistant left the voice chat (idle).")
                    except Exception:
                        pass


call = CallManager()
