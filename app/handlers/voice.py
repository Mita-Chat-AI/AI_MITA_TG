import os
import json
import httpx
from pathlib import Path
from loguru import logger
from datetime import datetime
from types import SimpleNamespace

from aiogram import Router, Bot, F
from aiogram_i18n import I18nContext
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message, BufferedInputFile, LinkPreviewOptions, InlineKeyboardButton, CallbackQuery

from ..entities import IsSendVoice
from ...config_reader import config
from ..utils.effect_audio import apply_effects
from ..database.requests import DatabaseManager
from ..services.voice_person import VoicePerson
from ..utils.utils import remove_unwanted_chars


voice_router = Router()


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(Path(__file__).resolve().parent.parent.parent / "new_voice.json")
USER_CONFIG_FOLDER = os.path.join(Path(__file__).resolve().parent.parent.parent / "voice_engine_parametres")


def load_user_config(user_id: int, person_name: str):
    user_path = os.path.join(USER_CONFIG_FOLDER, f"{user_id}.json")
    person_name = person_name.strip()

    if os.path.exists(user_path):
        with open(user_path, "r") as f:
            user_data = json.load(f)

            print( user_data[person_name].get("params", user_data[person_name]))
            return user_data[person_name].get("params", user_data[person_name])

    with open(DEFAULT_CONFIG_PATH, "r") as f:
        all_defaults = json.load(f)

    return all_defaults[person_name]["params"]


class VoiceGenerate:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = DatabaseManager(user_id)

    async def egde_generate(self, text) -> bytes | None:
        voice_person = await self.db.get_voice_person()

        speed = "10%"

        get_params_voise_person = await VoicePerson(voice_person, "persons.json").get_params()
        if isinstance(get_params_voise_person, SimpleNamespace):
            pith = get_params_voise_person.pith
            speed = get_params_voise_person.speed
            print(speed)

        params = {
            "text": remove_unwanted_chars(text),
            "person": voice_person,
            "rate": speed,
            "pith": pith
        }

        headers = {'Content-type': 'application/json'}


        response = await self._send_param(
            url=config.edge_api.get_secret_value(),
            params=params,
            headers=headers
        )

        if response is None:
            return None
        responce_effect = await apply_effects(response.content)
        return responce_effect


    async def vosk_generate(self, text) -> bytes | None:
        voice_person = await self.db.get_voice_person()

        user_config = load_user_config(self.user_id, voice_person)

        pith = user_config.get("pith")
        rate = user_config.get("rate")
        speaker_id = user_config.get("speaker_id")
        speech_rate = user_config.get("speech_rate")
        duration_noise_level = user_config.get("duration_noise_level")
        scale = user_config.get("scale")

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

        response = await self._send_param(
            url=config.edge_api.get_secret_value(),
            params=params,
            headers=headers
        )
        if response is None:
            return None
        
        responce_effect = await apply_effects(response.content)
        return responce_effect


    async def _send_param(self, url, params, headers, timeout=30):
        try:
            proxy_url = config.socks_proxy.get_secret_value()

            transport = httpx.AsyncHTTPTransport(
                proxy=proxy_url
            )

            async with httpx.AsyncClient(transport=transport, timeout=timeout) as client:
                response = await client.post(
                    url=config.edge_api.get_secret_value(),
                    json=params,
                    headers={"Content-type": "application/json"}
                )
                response.raise_for_status()
                return response
        except Exception as e:
            logger.error(f"Voice generation failed: {e}")
            return None



@voice_router.message(Command("voice"))
async def voice(message: Message, command: CommandObject, state: FSMContext, bot: Bot, i18n: I18nContext) -> None:
    user_id = message.from_user.id

    db = DatabaseManager(user_id)
    voice_generate = VoiceGenerate(user_id)  

    text = command.args
    if not text:
        await message.reply(text=i18n.get("no_args_voice"))
        return
    
    if len(text) < 10:
        await message.reply(text=i18n.get("less_10_characters"))
        return
    
    waiting_message = await message.reply(text=i18n.get("waiting_voice_message"), link_preview_options=LinkPreviewOptions(is_disabled=True))

    if await db.get_voice_engine() == 'vosk':
        get_sub = await db.get_subscribe()

        is_subscribed = get_sub.get("subscribe") == 1
        free_voice = get_sub.get("free_voice")
        left_free_voice = get_sub.get("left_free_voice")

        print(f"free_voice: {free_voice} / left_free_voice: {left_free_voice}")

        if is_subscribed:
            # подписка есть — безлим
            response = await voice_generate.vosk_generate(text)

        elif free_voice >= left_free_voice:
            # бесплатки закончились
            await message.reply("""
    У тебя закончились бесплатные генерации. Купить тут: https://t.me/DonateCrazyMitaAi/10

    А пока-что, переключаю тебя на бесплатный голосовой движок :)
            """)
            await db.set_voice_engine("edge")
            await waiting_message.delete()
            response = await voice_generate.egde_generate(text)

        else:
            # есть бесплатные попытки
            if free_voice == 0:
                await message.reply("""
    😉 | Вам предоставляется бесплатно 30 генераций на тестирование.
    ┗ Это условно бесплатный движок: платный, но с бесплатным периодом

    Купить можно за 190 руб/мес за безлим генерацию.
    Подробнее: https://t.me/DonateCrazyMitaAi/10
    """)

            response = await voice_generate.vosk_generate(text)
            await db.increment_free_voice()  # <= заменим set на отдельный метод
    else:
        response = await voice_generate.egde_generate(text)

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

    print(config.log_channel_id.get_secret_value())
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
