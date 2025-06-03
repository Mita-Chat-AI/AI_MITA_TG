import asyncio

from aiogram import Router, Bot, F
from aiogram.types import Message

from ...config_reader import config
from ..database.requests import DatabaseManager


mailing_router = Router()

chat_id_mailing = config.mailing_chat_id.get_secret_value()


@mailing_router.message(F.chat.id == chat_id_mailing)
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

            await bot.send_message(
                chat_id=config.owner_id.get_secret_value(),
                text=f"{user_id} отправлено ваше сообщение"
            )
        except Exception as e:
            await bot.send_message(
                chat_id=config.owner_id.get_secret_value(),
                text=f"НЕ УДАЛОСЬ ОТПРАВИТЬ {user_id} ваше сообщение\n\n{e}"
            )

    await bot.send_message(
        chat_id=config.owner_id.get_secret_value(),
        text=f"Всё сообщения были отправлены"
    )

