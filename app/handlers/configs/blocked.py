from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command

from ...services.config_service import UserConfigService


blocked_router = Router()


@blocked_router.message(Command('blocked'), F.from_user.id == 6506201559)
async def blocked(message: Message) -> None:
    text = message.text.split(maxsplit=2)

    if len(text) != 3:
        await message.reply("не правильно используешь команду")
        return

    if text[2].lower() not in ('-', '+'):
        await message.reply('Не правильн! + или - !')
        return

    configurator = UserConfigService(int(text[1]))

    try:
        await configurator.blocker(True if text[2] == '+' else False) # Вызываем blocker, но не используем его возвращаемое значение.
        is_blocked = await configurator.db.get_is_blocked_user() # Получаем статус блокировки из базы данных.
    except Exception as e:
        await message.reply(text=f"{e}")
        return

    await message.reply(text=f"{'Пользователь был заблокирован' if is_blocked else 'пользователь был разблокирован'}")
