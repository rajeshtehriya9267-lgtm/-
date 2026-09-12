from config import config

FONT = str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                     "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳"
                     "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
                     "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗")


def bold(s: str) -> str:
    return s.translate(FONT)


def progress_bar(current: float, total: float, length: int = 12) -> str:
    if not total:
        return "◉" + "○" * (length - 1)
    filled = int(length * min(current / total, 1.0))
    return "◉" * filled + "○" * (length - filled)


def fmt_time(seconds: float) -> str:
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return "LIVE"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def parse_duration(dur) -> int:
    try:
        if isinstance(dur, int):
            return dur
        parts = [int(x) for x in str(dur).split(":")]
        return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))
    except Exception:
        return 0


def now_playing_card(title, requester, duration, position, total, loop, volume, progress=0, thumb=None) -> str:
    bar = progress_bar(progress, parse_duration(duration))
    return (
        f"╭━━━ 🎧 𝐊𝐔𝐊𝐔 𝐌𝐔𝐒𝐈𝐂 🎧 ━━━╮\n\n"
        f"🎵 <b>Song:</b> {title}\n\n"
        f"👤 <b>Requested By:</b> {requester}\n\n"
        f"⏱ <b>Duration:</b> {duration}\n"
        f"[{bar}]\n\n"
        f"🔊 <b>Volume:</b> {volume}%\n"
        f"🔁 <b>Loop:</b> {'Track' if loop == 'track' else 'Queue' if loop == 'queue' else 'Disabled'}\n\n"
        f"📋 <b>Queue:</b> {total} Song(s) | ▶️ Now: {position}\n\n"
        f"╰━━━━━━━━━━━━━━━━━━╯"
    )


def is_sudo(user_id: int) -> bool:
    return user_id in config.sudo_list or user_id == config.OWNER_ID
