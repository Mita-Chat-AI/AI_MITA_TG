from aiogram import Router
from aiogram.types import Message
from aiogram_i18n import I18nContext

from ..database.requests import DatabaseManager

start_router = Router()


async def start(message: Message, i18n: I18nContext) -> None:
    # db = DatabaseManager(message.from_user.id)
    # lang = await db.get_lang()

    # if lang:
    await i18n.set_locale("ru")

    await message.reply(
        text=i18n.get("hello")
    )
