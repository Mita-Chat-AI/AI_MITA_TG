import time
from aiogram.types import Message
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.enums.chat_type import ChatType
from aiogram_i18n import I18nContext

from .mita import mita


ask_router = Router()

memory_time = {}
last_bot_message = {}


@ask_router.message(Command("ask"), F.chat.type.in_([ChatType.GROUP, ChatType.SUPERGROUP]))
async def ask(message: Message, i18n: I18nContext, bot: Bot) -> None:
    await message.reply(text=i18n.get("waiting_voice_message"))
    user_id = message.from_user.id
    bot_response = await mita(message, bot)

    last_bot_message[user_id] = bot_response.message_id
    memory_time[user_id] = time.time()


@ask_router.message(F.reply_to_message, F.chat.type.in_([ChatType.GROUP, ChatType.SUPERGROUP]))
async def handle_reply_to_bot(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id

    if user_id in last_bot_message and message.reply_to_message.message_id == last_bot_message[user_id]:
        bot_response = await mita(message, bot)
        last_bot_message[user_id] = bot_response.message_id