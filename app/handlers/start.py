from aiogram import Router
from aiogram.types import Message
from aiogram_i18n import I18nContext
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import URLInputFile


from ...config_reader import config
from ..services.conditions import conditions_accept
from ..database.requests import DatabaseManager


start_router = Router()


async def start(message: Message, i18n: I18nContext, state: FSMContext) -> None:
    db = DatabaseManager(message.from_user.id)

    conditions = await db.get_conditions()
    if not conditions:
        await conditions_accept(message, i18n, state)
        return

    await message.reply_video(
        video=(URLInputFile(config.start_video_url.get_secret_value())),
        caption=i18n.get("hello")
    )
