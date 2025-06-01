from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram_i18n import I18nContext

from ..services.config_service import UserConfigService


reset_router = Router()


@reset_router.message(Command('reset'))
async def reset(message: Message, i18n: I18nContext) -> None:
    user_id = message.from_user.id

    configurator = UserConfigService(user_id)
    await configurator.reset_history()

    await message.reply(text=i18n.get("reset_message"))
