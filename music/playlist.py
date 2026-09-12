from music.search import get_playlist_entries
from utils.helpers import fmt_time


async def playlist_info(url: str) -> dict | None:
    entries = await get_playlist_entries(url)
    if not entries:
        return None
    total = sum(e["duration"] or 0 for e in entries)
    return {
        "count": len(entries),
        "duration": fmt_time(total),
        "first": entries[0]["title"],
        "entries": entries,
    }
