# 🎧 𝕂𝕌𝕂𝕌 𝕄𝕌𝕊𝕀ℂ 🎧

Premium Telegram Voice Chat Music Bot.

## Railway Deployment
1. Push this repo to GitHub.
2. railway.app → New Project → Deploy from GitHub repo.
3. Add all environment variables from `.env.example` in the Variables tab.
4. Railway auto-detects the Dockerfile. Start command: `python main.py`.

## Getting Values
- BOT_TOKEN → @BotFather
- API_ID / API_HASH → my.telegram.org
- SESSION_STRING → run `python -m pyrogram` locally with API creds (string session of assistant account)
- MONGO_DB_URI → MongoDB Atlas free tier
- LOG_GROUP_ID → forward a message from your log group to @userinfobot (starts with -100)

## Environment Variables Guide
| Variable | Description |
|---|---|
| BOT_TOKEN | Bot token from BotFather |
| API_ID / API_HASH | Telegram API credentials |
| SESSION_STRING | Pyrogram session of assistant account (must join the group) |
| OWNER_ID | Your Telegram user ID |
| MONGO_DB_URI | MongoDB connection string |
| LOG_GROUP_ID | Log channel/group ID |
| SUPPORT_GROUP / SUPPORT_CHANNEL | Invite links |
| SUDO_USERS | Comma-separated sudo user IDs |
