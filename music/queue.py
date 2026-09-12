import asyncio
from dataclasses import dataclass, field


@dataclass
class Track:
    title: str
    stream_url: str
    duration: str
    duration_sec: int
    thumbnail: str
    requester_id: int
    requester_name: str
    link: str = ""
    voice: bool = True


@dataclass
class ChatQueue:
    queue: list[Track] = field(default_factory=list)
    current: Track | None = None
    loop_track: bool = False
    loop_queue: bool = False
    volume: int = 100
    started_at: float = 0.0
    last_active: float = 0.0
    message: object = None  # now-playing message handle (pyrogram)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class QueueManager:
    def __init__(self):
        self._chats: dict[int, ChatQueue] = {}

    def get(self, chat_id: int) -> ChatQueue:
        if chat_id not in self._chats:
            self._chats[chat_id] = ChatQueue()
        return self._chats[chat_id]

    def remove(self, chat_id: int):
        self._chats.pop(chat_id, None)

    def add(self, chat_id: int, track: Track) -> int:
        q = self.get(chat_id)
        q.queue.append(track)
        return len(q.queue)

    def skip(self, chat_id: int) -> Track | None:
        q = self.get(chat_id)
        if q.loop_track and q.current:
            return q.current
        if q.loop_queue and q.current:
            q.queue.append(q.current)
        nxt = q.queue.pop(0) if q.queue else None
        return nxt

    def shuffle(self, chat_id: int) -> int:
        import random
        q = self.get(chat_id)
        random.shuffle(q.queue)
        return len(q.queue)

    def clear(self, chat_id: int):
        self.get(chat_id).queue.clear()

    def remove_index(self, chat_id: int, index: int) -> bool:
        q = self.get(chat_id)
        if 0 <= index < len(q.queue):
            q.queue.pop(index)
            return True
        return False


queue_manager = QueueManager()
