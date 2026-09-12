import asyncio
import yt_dlp

YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "skip_download": True,
    "cookiefile": None,
}

STREAM_OPTS = {
    **YDL_OPTS,
    "format": "bestaudio/best",
}


def _extract(query: str, opts: dict) -> dict:
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(query, download=False)


async def search_youtube(query: str) -> dict | None:
    """Search YouTube / resolve a URL. Returns {'title','duration','stream_url','thumbnail','webpage_url','uploader'}"""
    loop = asyncio.get_event_loop()
    if query.startswith(("http://", "https://", "www.")):
        info = await loop.run_in_executor(None, _extract, query, STREAM_OPTS)
    else:
        info = await loop.run_in_executor(None, _extract, f"ytsearch:{query}", {**YDL_OPTS, "format": "bestaudio/best"})
    if not info:
        return None
    if "entries" in info:
        entries = [e for e in info["entries"] if e]
        if not entries:
            return None
        info = entries[0]

    stream_url = None
    for f in info.get("formats") or []:
        if f.get("url") and (f.get("acodec") not in (None, "none")):
            stream_url = f["url"]
            if not f.get("video_codec") or f.get("video_codec") == "none":
                break
    if not stream_url:
        stream_url = info.get("url")

    return {
        "title": info.get("title", "Unknown"),
        "duration": info.get("duration") or 0,
        "duration_str": _fmt(info.get("duration") or 0),
        "stream_url": stream_url,
        "thumbnail": info.get("thumbnail") or f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg",
        "webpage_url": info.get("webpage_url", ""),
        "uploader": info.get("uploader", "Unknown"),
    }


async def get_playlist_entries(url: str) -> list[dict]:
    loop = asyncio.get_event_loop()
    opts = {**YDL_OPTS, "extract_flat": "in_playlist", "noplaylist": False}

    def _pl():
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    info = await loop.run_in_executor(None, _pl)
    if not info or "entries" not in info:
        return []
    return [
        {
            "title": e.get("title", "Unknown"),
            "duration": e.get("duration") or 0,
            "url": e.get("url") or e.get("webpage_url", ""),
        }
        for e in info["entries"] if e
    ][:50]


def _fmt(sec) -> str:
    if not sec:
        return "LIVE"
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
