import json
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ...database.requests import DatabaseManager

from pathlib import Path

config_voice_engine_router = Router()

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, "new_voice.json")
USER_CONFIG_FOLDER = os.path.join(Path(__file__).resolve().parent.parent.parent.parent / "voice_engine_parametres")


class ConfigEngineState(StatesGroup):
    speech_rate = State()
    duration_noise_level = State()
    pith = State()


config_engine_markup = {
    "speech_rate": "Скорость (-0.5 до +1.0)",
    "duration_noise_level": "Эмоциональность (0.1 до 1.0)",
    "pith": "Высота голоса (-10 до +15)"
}


def load_user_config(user_id: int):
    user_path = f"{USER_CONFIG_FOLDER}/{user_id}.json"
    if os.path.exists(user_path):
        with open(user_path, "r") as f:
            return json.load(f)
    with open(DEFAULT_CONFIG_PATH, "r") as f:
        return json.load(f)


def save_user_config(user_id: int, config: dict):
    os.makedirs(USER_CONFIG_FOLDER, exist_ok=True)
    with open(f"{USER_CONFIG_FOLDER}/{user_id}.json", "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


@config_voice_engine_router.message(Command("config_engine"))
async def config_engine(message: Message):
    builder = InlineKeyboardBuilder()

    for key, text in config_engine_markup.items():
        builder.add(InlineKeyboardButton(text=text, callback_data=key))

    builder.add(InlineKeyboardButton(text="Сбросить к дефолту", callback_data="reset_defaults"))
    builder.adjust(1)

    await message.reply("Выбери, что хочешь настроить:", reply_markup=builder.as_markup(resize_keyboard=True))


@config_voice_engine_router.callback_query(F.data.in_(list(config_engine_markup.keys())))
async def choose_param(callback: CallbackQuery, state: FSMContext):
    param = callback.data
    await callback.message.reply(f"Введи новое значение для {config_engine_markup[param]}:")

    if param == "speech_rate":
        await state.set_state(ConfigEngineState.speech_rate)
    elif param == "duration_noise_level":
        await state.set_state(ConfigEngineState.duration_noise_level)
    elif param == "pith":
        await state.set_state(ConfigEngineState.pith)

    await state.update_data(user_id=callback.from_user.id)


@config_voice_engine_router.callback_query(F.data == "reset_defaults")
async def reset_defaults(callback: CallbackQuery):
    user_id = callback.from_user.id
    db = DatabaseManager(user_id)
    

    get_voice_param = await db.get_voice_person()


    default_config = load_user_config(get_voice_param)
    save_user_config(user_id, default_config["params"])
    await callback.message.reply("Параметры сброшены к значениям по умолчанию.")


@config_voice_engine_router.message(ConfigEngineState.speech_rate)
async def set_speech_rate(message: Message, state: FSMContext):
    await apply_param_change(message, state, "speech_rate")


@config_voice_engine_router.message(ConfigEngineState.duration_noise_level)
async def set_duration_noise_level(message: Message, state: FSMContext):
    await apply_param_change(message, state, "duration_noise_level")


@config_voice_engine_router.message(ConfigEngineState.pith)
async def set_pith(message: Message, state: FSMContext):
    await apply_param_change(message, state, "pith")


async def apply_param_change(message: Message, state: FSMContext, param: str):
    user_id = message.from_user.id
    text = message.text.strip().replace(",", ".")

    # Добавляем знак +, если нужно
    if param in ["speech_rate", "pith"] and not (text.startswith("+") or text.startswith("-")):
        text = "+" + text

    try:
        value = float(text)
    except ValueError:
        await message.reply("Неверный формат числа, попробуй ещё раз.")
        return

    # Проверки диапазонов
    if param == "pith":
        if not (-10 <= value <= 15):
            await message.reply("Значение должно быть от -10 до +15.")
            return
    elif param == "speech_rate":
        if not (-0.5 <= value <= 1.0):
            await message.reply("Значение должно быть от -0.5 до +1.0.")
            return
    elif param == "duration_noise_level":
        if not (0.1 <= value <= 1.0):
            await message.reply("Значение должно быть от 0.1 до 1.0.")
            return

    # Получаем текущего персонажа
    db = DatabaseManager(user_id)
    voice_person = await db.get_voice_person()

    # Загружаем конфиг пользователя
    config = load_user_config(user_id)

    # Проверяем есть ли персонаж в конфиге
    if voice_person not in config:
        config[voice_person] = {"params": {}}
    elif "params" not in config[voice_person]:
        config[voice_person]["params"] = {}

    # Обновляем параметр
    config[voice_person]["params"][param] = value

    # Сохраняем
    save_user_config(user_id, config)

    await message.reply(f"{config_engine_markup[param]} обновлена до {value}.")
    await state.clear()
