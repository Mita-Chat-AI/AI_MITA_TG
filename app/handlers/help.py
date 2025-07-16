from aiogram import Router
from aiogram.types import Message
from aiogram_i18n import I18nContext
from aiogram.filters.command import Command
from aiogram.types.input_file import URLInputFile

from ...config_reader import config


help_router = Router()


@help_router.message(Command('help'))
async def help(message: Message, i18n: I18nContext) -> None:
    await message.reply_photo(
        photo=URLInputFile(config.help_pic_url.get_secret_value()),
        caption=i18n.get("help_message")
    )