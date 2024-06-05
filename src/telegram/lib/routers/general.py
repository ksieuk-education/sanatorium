import aiogram


class GeneralRouter:
    def __init__(self, bot: aiogram.Bot):
        self.bot = bot

    async def send_message_by_id(self, user_id: str, message_text: str):
        await self.bot.send_message(user_id, message_text)
