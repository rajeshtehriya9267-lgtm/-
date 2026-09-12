import time
from assistant.call import call
from music.queue import queue_manager


async def do_pause(chat_id: int) -> bool:
    return await call.pause(chat_id)


async def do_resume(chat_id: int) -> bool:
    return await call.resume(chat_id)


async def do_skip(chat_id: int) -> bool:
    from music.player import play_now
    q = queue_manager.get(chat_id)
    nxt = queue_manager.skip(chat_id)
    if not nxt:
        q.current = None
        await call.leave(chat_id)
        return False
    # resolve stream if playlist-flattened (lazy)
    if not nxt.stream_url:
        from music.search import search_youtube
        info = await search_youtube(nxt.link or nxt.title)
        if info:
            nxt.stream_url = info["stream_url"]
            nxt.thumbnail = nxt.thumbnail or info["thumbnail"]
    if not nxt.stream_url:
        return await do_skip(chat_id)  # skip broken entry
    await play_now(chat_id, nxt)
    return True


async def do_stop(chat_id: int) -> bool:
    queue_manager.clear(chat_id)
    queue_manager.get(chat_id).current = None
    return await call.leave(chat_id)


async def do_seek(chat_id: int, seconds: int) -> bool:
    return await call.seek(chat_id, seconds)


async def set_volume(chat_id: int, percent: int) -> int:
    percent = max(1, min(200, percent))
    queue_manager.get(chat_id).volume = percent
    await call.change_volume(chat_id, percent)
    return percent


def elapsed(chat_id: int) -> int:
    q = queue_manager.get(chat_id)
    return int(time.time() - q.started_at) if q.started_at else 0
