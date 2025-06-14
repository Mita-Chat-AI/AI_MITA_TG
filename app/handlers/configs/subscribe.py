from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command

from ...database.requests import DatabaseManager

subscribe_router = Router()


@subscribe_router.message(Command('subscribe'), F.from_user.id == 6506201559)
async def subscribe(message: Message) -> None:
    text = message.text.split(maxsplit=2)

    

    if len(text) != 3:
        await message.reply("не правильно используешь команду")
        return

    if text[2].lower() not in ('-', '+'):
        await message.reply('Не правильн! + или - !')
        return


    db = DatabaseManager(int(text[1]))

    try:
        await db.set_subscribe(1 if text[2] == '+' else 0) # Вызываем blocker, но не используем его возвращаемое значение.
    except Exception as e:
        await message.reply(text=f"{e}")
        return

    await message.reply(text=f"Подписка была активирована")
