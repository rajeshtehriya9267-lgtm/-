from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    BOT_TOKEN: str
    API_ID: int
    API_HASH: str
    SESSION_STRING: str
    OWNER_ID: int
    MONGO_DB_URI: str
    LOG_GROUP_ID: int
    SUPPORT_GROUP: str = "https://t.me/+5q36Fn32Y0BmYzk9"
    SUPPORT_CHANNEL: str = "https://t.me/+CS-ZvjWSB1oxZjZl"
    SUDO_USERS: str = ""

    BOT_NAME: str = "🎧 𝕂𝕌𝕂𝕌 𝕄𝕌𝕊𝕀ℂ 🎧"
    BOT_USERNAME: str = "@kukuxmusicbot"
    OWNER_NAME: str = "乂 𝐈𝐍𝐓𝐄𝐑𝐍𝐀𝐓𝐈𝐎𝐍𝐀𝐋 𝐏𝐀𝐍𝐃𝐈𝐓 乂"
    OWNER_USERNAME: str = "@internationalpanditG"
    ASSISTANT_NAME: str = "𝐊𝐔𝐊𝐔 𝐀𝐒𝐒𝐈𝐒𝐓𝐀𝐍𝐓"
    MAX_QUEUE: int = 50
    IDLE_LEAVE_SECONDS: int = 60

    class Config:
        env_file = ".env"

    @property
    def sudo_list(self) -> List[int]:
        return [int(x) for x in self.SUDO_USERS.replace(",", " ").split() if x.strip().isdigit()]


config = Settings()
