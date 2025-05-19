import asyncio
import requests

from aiogram import Router, Bot, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message, BufferedInputFile, LinkPreviewOptions, InlineKeyboardButton, CallbackQuery

from ...config_reader import config
from ..database.requests import DatabaseManager
from ..services.voice_person import VoicePerson
from ..utils.utils import remove_unwanted_chars

from aiogram_i18n import I18nContext

class IsSendVoice(StatesGroup):
    is_send_voice =  State()

from types import SimpleNamespace

voice_router = Router()


proxy = {
    'http': config.socks_proxy.get_secret_value()
    }


async def voice_generate(user_id, text, timeout: int = 70):
    db = DatabaseManager(user_id)
    voice_person = await db.get_voice_person()

    pith = 8
    get_params_voise_person = await VoicePerson(voice_person).get_params()
    if isinstance(get_params_voise_person, SimpleNamespace):
        pith = get_params_voise_person.pith

    params = {
        "text": remove_unwanted_chars(text),
        "person": voice_person,
        "rate": "+10%",
        "pith": pith
    }
    headers = {'Content-type': 'application/json'}

    try:
        response = await asyncio.to_thread(
            requests.post,
                url=config.voice_api.get_secret_value(),
                json=params,
                headers=headers,
                proxies=proxy,
                timeout=timeout  
        )
        response.raise_for_status()
        return response
    except:
        return None


from aiogram.types.reaction_type_emoji import ReactionTypeEmoji

@voice_router.message(Command("reaction"), F.from_user.id == 6506201559)
async def reasctins(message: Message, bot: Bot):
    reaction = [ReactionTypeEmoji(emoji='👍')]
    result = await bot.set_message_reaction(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reaction=reaction
    )
    await message.reply(f"{result}")

    ret = await bot.get_chat(chat_id=8102139305)

    await message.reply(f"{ret}")
1


@voice_router.message(Command("voice"))
async def voice(message: Message, command: CommandObject, state: FSMContext, bot: Bot) -> None:
    user_id = message.from_user.id

    text = command.args
    if not text:
        await message.reply("<b>🤨 | И что?</b>")
        return
    
    if len(text) < 10:
        await message.reply("<b>😕 | Можно генерировать голсовые, только от 10 символов.</b> ВОТ И НАПИШИ ТАМ /voice 1234567890 ВОТ ТАК НА ПРИМЕР")
        return
    
    waiting_message = await message.reply(f"<b>❤️ | Обрабатываю.</b>\n┗ Поддержать проект -> yumemi_hoshino.t.me", link_preview_options=LinkPreviewOptions(is_disabled=True))

    
    response = await voice_generate(user_id, text)

    if not response:
        await waiting_message.delete()
        await message.reply("Ошибка при генерации голоса. Попробуйте ещё раз, или напишите в @BugsCrazyMitaAIbot")
        return
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Отправить в канал голосовых",
            callback_data='send_voice_chanel'
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="💲 | Поддержатиь проект",
            url='yumemi_hoshino.t.me'
        )
    )
    builder.adjust(1)

    await state.set_state(IsSendVoice.is_send_voice)
    await state.update_data(user_id=user_id, voice_buffer=response.content, text=text)

    await waiting_message.delete()

    await message.reply_voice(
        BufferedInputFile(
            response.content,
            filename="voice.ogg"
        ), 
        mime_type="audio/ogg",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

    await bot.send_voice(
        chat_id=-1002471083299,
        voice=BufferedInputFile(
                response.content,
                filename="voice.ogg"
            ), 
            caption=f'{text}\n@{message.from_user.username}\n{message.from_user.id}'
    )



@voice_router.callback_query(IsSendVoice.is_send_voice)
async def send_voice_chanel(callback: CallbackQuery, bot: Bot, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data.get("user_id")
    voice_data = state_data.get("voice_buffer")
    text = state_data.get("text")

    if user_id != callback.from_user.id:
        return

    audio_id = await bot.send_voice(
        chat_id=-1002326238712,
        voice=BufferedInputFile(
                voice_data,
                filename="voice.ogg"
            ), 
            caption=text
    )

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="туть",
            url=f"t.me/CrazyMitaAIvoices/{audio_id.message_id}"
        )
    )

    await callback.message.reply(f"✅ | Ваше голосовое отправлено. Его можно посмотерть здесь:", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.clear()

