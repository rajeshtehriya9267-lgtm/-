"""
Assistant registry. Currently one assistant; add more SessionStrings to scale.
"""
from assistant.userbot import userbot
from assistant.call import call


class AssistantManager:
    def __init__(self):
        self.assistants = [userbot]  # future: list of Userbot()

    async def bind(self, aiogram_bot):
        await self.assistants[0].start()
        assistant_id = await self.assistants[0].get_assistant_id()
        call.bind(self.assistants[0].client, aiogram_bot, assistant_id)
        await call.start()

    async def get_assistant_id(self) -> int | None:
        return await self.assistants[0].get_assistant_id()


assistant = AssistantManager()
