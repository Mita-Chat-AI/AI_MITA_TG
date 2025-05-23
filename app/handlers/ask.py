import time
from aiogram.types import Message
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.enums.chat_type import ChatType

from .mita import mita


ask_router = Router()

memory_time = {}
last_bot_message = {}


@ask_router.message(Command("ask"), F.chat.type.in_([ChatType.GROUP, ChatType.SUPERGROUP]))
async def ask(message: Message, bot: Bot) -> None:
    await message.reply("<b>❤️ | Я тебе уже пишу!</b>")
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
    else:
        print("Not last message")