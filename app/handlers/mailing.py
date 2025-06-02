import asyncio

from aiogram import Router, Bot, F
from aiogram.types import Message

from ..database.requests import DatabaseManager


mailing_router = Router()


@mailing_router.message(F.chat.id == -1002427185323)  # без кавычек, это int
async def mailing(message: Message, bot: Bot):
    db = DatabaseManager(message.from_user.id)
    tg_ids = await db.get_all_tgid()

    for user_id in tg_ids:
        try:
            await asyncio.sleep(5.0)
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
        except Exception as e:
            print(f"Не удалось отправить пользователю {user_id}: {e}")
