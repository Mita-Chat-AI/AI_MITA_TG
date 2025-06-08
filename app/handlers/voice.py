import asyncio
import requests
from types import SimpleNamespace
from datetime import datetime


from aiogram_i18n import I18nContext
from aiogram import Router, Bot, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message, BufferedInputFile, LinkPreviewOptions, InlineKeyboardButton, CallbackQuery

from ..entities import IsSendVoice
from ...config_reader import config
from ..database.requests import DatabaseManager
from ..services.voice_person import VoicePerson
from ..utils.utils import remove_unwanted_chars
from ..utils.effect_audio import apply_effects


voice_router = Router()


async def voice_generate(user_id, text, timeout: int = 30) -> bytes | None:
    db = DatabaseManager(user_id)
    voice_person = await db.get_voice_person()

    pith = 8
    speed = "+10%"
    get_params_voise_person = await VoicePerson(voice_person, "persons.json").get_params()
    if isinstance(get_params_voise_person, SimpleNamespace):
        pith = get_params_voise_person.pith
        speed = get_params_voise_person.speed

    params = {
        "text": remove_unwanted_chars(text),
        "person": voice_person,
        "rate": speed,
        "pith": pith
    }

    
    headers = {'Content-type': 'application/json'}

    try:
        response = await asyncio.to_thread(
            requests.post,
                url=config.voice_api.get_secret_value(),
                json=params,
                headers=headers,
                proxies={'http': config.socks_proxy.get_secret_value()},
                timeout=timeout  
        )
        response.raise_for_status()
    
        responce_effect = await apply_effects(response.content)

        return responce_effect

    except:
        return None



async def voice_generate_тnew(user_id, text, timeout: int = 70) -> bytes | None:
    db = DatabaseManager(user_id)
    voice_person = await db.get_voice_person()

    get_params_voise_person = await VoicePerson(voice_person, "new_persons.json").get_params()
    if isinstance(get_params_voise_person, SimpleNamespace):
        pith = get_params_voise_person.pith

        rate = get_params_voise_person.rate
        pith = get_params_voise_person.pith
        speaker_id = get_params_voise_person.speaker_id
        speech_rate = get_params_voise_person.speech_rate
        duration_noise_level = get_params_voise_person.duration_noise_level
        scale = get_params_voise_person.scale


    params = {
        "text": remove_unwanted_chars(text),
        "person": voice_person,
        "rate": rate,
        "pith": pith,
        "speaker_id": speaker_id,
        "speech_rate": speech_rate,
        "duration_noise_level": duration_noise_level,
        "scale": scale

    }
    headers = {'Content-type': 'application/json'}

    try:
        response = await asyncio.to_thread(
            requests.post,
                url="http://localhost:4000/api/v1/vosk/get_vosk",#config.voice_api.get_secret_value(),
                json=params,
                headers=headers,
                #proxies={'http': config.socks_proxy.get_secret_value()},
                timeout=timeout  
        )
        response.raise_for_status()
    
        responce_effect = await apply_effects(response.content)
        print(responce_effect)

        return responce_effect
    except:
        return None


@voice_router.message(Command("voice"))
async def voice(message: Message, command: CommandObject, state: FSMContext, bot: Bot, i18n: I18nContext) -> None:
    user_id = message.from_user.id

    db = DatabaseManager(user_id)

    text = command.args
    if not text:
        await message.reply(text=i18n.get("no_args_voice"))
        return
    
    if len(text) < 10:
        await message.reply(text=i18n.get("less_10_characters"))
        return
    
    waiting_message = await message.reply(text=i18n.get("waiting_voice_message"), link_preview_options=LinkPreviewOptions(is_disabled=True))

    if await db.get_voice_engine() == 'vosk':
        response = await voice_generate_тnew(user_id, text)
    else:
        response = await voice_generate(user_id, text)



    if not response:
        await waiting_message.delete()
        await message.reply(text=i18n.get("generate_voice_error"))
        return
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=i18n.get("send_voice_channel"),
            callback_data='send_voice_chanel'
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=i18n.get("support_project"),
            url='yumemi_hoshino.t.me'
        )
    )
    builder.adjust(1)

    await state.set_state(IsSendVoice.is_send_voice)
    await state.update_data(user_id=user_id, voice_buffer=response, text=text)

    await waiting_message.delete()

    await message.reply_voice(
        BufferedInputFile(
            response,
            filename="voice.ogg"
        ), 
        mime_type="audio/ogg",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await message.reply(f"{await db.get_voice_engine()}")

    await bot.send_voice(
        chat_id=config.log_channel_id.get_secret_value(),
        voice=BufferedInputFile(
                response,
                filename="voice.ogg"
            ), 
            caption=f'{text}\n@{message.from_user.username}\n{message.from_user.id}'
    )

    await db.set_voice_use(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@voice_router.callback_query(IsSendVoice.is_send_voice)
async def send_voice_chanel(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: I18nContext) -> None:
    state_data = await state.get_data()
    user_id = state_data.get("user_id")
    voice_data = state_data.get("voice_buffer")
    text = state_data.get("text")

    if user_id != callback.from_user.id:
        return

    try:
        msg = await bot.send_voice(
            chat_id=-1002326238712,
            voice=BufferedInputFile(voice_data, filename="voice.ogg"),
            caption=text
        )

        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text=i18n.get("send_voice_channel_accept_tyt"),
                url=f"https://t.me/{config.voice_channel_username.get_secret_value()}/{msg.message_id}"
            )
        )

        await callback.message.reply(
            text=i18n.get("send_voice_channel_accept"),
            reply_markup=builder.as_markup(resize_keyboard=True)
        )
    except Exception as e:
        await callback.message.reply(text=i18n.get("error_send_voice_channel"))

    await state.clear()
