from aiogram import Router, Bot
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random
import os
from comfy_api_simplified import ComfyApiWrapper, ComfyWorkflowWrapper
from asyncio import create_task, CancelledError

image_generate_router = Router()


import json
from pathlib import Path

with open(Path(__file__).resolve().parents[2] / "image/persons.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    characters = data["characters"]


resolutions = {
    "Стандарт 1248x836": (1248, 836),
    "Вертикальное 832x1216": (832, 1216),
    "Квадрат 1024x1024": (1024, 1024)
}

lora_mapping = {
    "Безумная Мита": "CrazyMita.safetensors",
    "Мила": "MilaMita.safetensors",
}

generation_tasks = {}

class GenStates(StatesGroup):
    config_menu = State()
    waiting_character = State()
    waiting_resolution = State()
    waiting_cfg = State()
    generating = State()  # <-- новое состояние


@image_generate_router.message(Command("image"))
async def start_generate(message: Message, command: CommandObject, state: FSMContext, bot: Bot):
    arg = command.args
    if not arg:
        await message.reply("Укажи описание после команды, пример:\n/image улыбается")
        return

    await state.update_data(
        description=arg,
        character=characters["Безумная Мита"],
        character_name="Безумная Мита",
        resolution=(1248, 836),
        resolution_name="Стандарт 1248x836",
        cfg=7.0,
        original_message_id=message.message_id
    )

    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text="🎭 Персонаж", callback_data="pick_character"),
        InlineKeyboardButton(text="📐 Разрешение", callback_data="pick_resolution"),
        InlineKeyboardButton(text="⚙️ CFG", callback_data="pick_cfg"),
        InlineKeyboardButton(text="🎨 Сгенерировать", callback_data="start_gen")
    )
    kb.adjust(1)

    await message.reply(
        f"<b>Текущие параметры:</b>\n"
        f"👤 Персонаж: Безумная Мита\n"
        f"📏 Размер: 1248x836\n"
        f"🖌️ Описание: <i>{arg}</i>\n"
        f"⚙️ CFG: 7.0\n\n"
        "Если хочешь изменить — выбери параметр, либо запускай генерацию.",
        reply_markup=kb.as_markup()
    )
    await state.set_state(GenStates.config_menu)

@image_generate_router.callback_query(GenStates.config_menu)
async def config_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = callback.data
    if data == "pick_character":
        builder = InlineKeyboardBuilder()
        for key in characters.keys():
            builder.add(InlineKeyboardButton(text=key, callback_data=f"char_{key}"))
        builder.adjust(1)
        await callback.message.edit_text("Выбери персонажа:", reply_markup=builder.as_markup())
        await state.set_state(GenStates.waiting_character)

    elif data == "pick_resolution":
        builder = InlineKeyboardBuilder()
        for key in resolutions.keys():
            builder.add(InlineKeyboardButton(text=key, callback_data=f"res_{key}"))
        builder.adjust(1)
        await callback.message.edit_text("Выбери разрешение:", reply_markup=builder.as_markup())
        await state.set_state(GenStates.waiting_resolution)

    elif data == "pick_cfg":
        await callback.message.edit_text("Введи значение CFG от 1 до 10:")
        await state.set_state(GenStates.waiting_cfg)

    elif data == "start_gen":
        gen_msg = await callback.message.edit_text("⏳ Генерация началась...", reply_markup=InlineKeyboardBuilder()
            .add(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_generation")).as_markup()
        )
        await state.set_state(GenStates.generating)

        task = create_task(run_generation(callback, state, bot, gen_msg))
        await state.update_data(gen_task=task)

        generation_tasks[callback.from_user.id] = task

@image_generate_router.message(GenStates.waiting_cfg)
async def set_cfg(message: Message, state: FSMContext):
    try:
        value = float(message.text.strip())
        if not 1 <= value <= 10:
            raise ValueError
        await state.update_data(cfg=value)
        await return_to_main_menu(message, state, f"CFG установлен: {value}")
    except ValueError:
        await message.reply("❌ Введи число от 1 до 10")

@image_generate_router.callback_query(GenStates.waiting_character)
async def choose_character(callback: CallbackQuery, state: FSMContext):
    key = callback.data.replace("char_", "")
    if key not in characters:
        await callback.answer("Ошибка выбора персонажа", show_alert=True)
        return
    await state.update_data(character=characters[key], character_name=key)
    await return_to_main_menu(callback, state, f"Персонаж выбран: {key}")

@image_generate_router.callback_query(GenStates.waiting_resolution)
async def choose_resolution(callback: CallbackQuery, state: FSMContext):
    key = callback.data.replace("res_", "")
    if key not in resolutions:
        await callback.answer("Ошибка выбора разрешения", show_alert=True)
        return
    await state.update_data(resolution=resolutions[key], resolution_name=key)
    await return_to_main_menu(callback, state, f"Разрешение выбрано: {key}")

@image_generate_router.callback_query(GenStates.generating)
async def cancel_gen(callback: CallbackQuery, state: FSMContext):
    if callback.data != "cancel_generation":
        await callback.answer("Генерация уже в процессе.", show_alert=True)
        return

    data = await state.get_data()
    task = data.get("gen_task")

    if task:
        task.cancel()
        await callback.message.edit_text("❌ Генерация отменена.")
    else:
        await callback.answer("Генерация уже завершена.", show_alert=True)

    await state.clear()



async def return_to_main_menu(message_or_callback, state: FSMContext, text: str):
    data = await state.get_data()
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text="🎭 Персонаж", callback_data="pick_character"),
        InlineKeyboardButton(text="📐 Разрешение", callback_data="pick_resolution"),
        InlineKeyboardButton(text="⚙️ CFG", callback_data="pick_cfg"),
        InlineKeyboardButton(text="🎨 Сгенерировать", callback_data="start_gen")
    )
    kb.adjust(1)

    # Тут — корректный способ возврата через редактирование
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(
            f"{text}\n\n<b>Текущие параметры:</b>\n"
            f"👤 Персонаж: {data.get('character_name')}\n"
            f"📏 Размер: {data.get('resolution_name')}\n"
            f"⚙️ CFG: {data.get('cfg')}\n"
            f"🖌️ Описание: <i>{data.get('description')}</i>",
            reply_markup=kb.as_markup()
        )
    else:
        await message_or_callback.answer(
            f"{text}\n\n<b>Текущие параметры:</b>\n"
            f"👤 Персонаж: {data.get('character_name')}\n"
            f"📏 Размер: {data.get('resolution_name')}\n"
            f"⚙️ CFG: {data.get('cfg')}\n"
            f"🖌️ Описание: <i>{data.get('description')}</i>",
            reply_markup=kb.as_markup()
        )

    await state.set_state(GenStates.config_menu)


async def run_generation(callback: CallbackQuery, state: FSMContext, bot: Bot, status_msg: Message):
    try:
        data = await state.get_data()
        prompt_text = data["description"]
        character_prompt = data.get("character", "")
        character_name = data.get("character_name", "")
        width, height = data.get("resolution", (768, 512))
        cfg = data.get("cfg", 7.0)
        original_msg_id = data.get("original_message_id")

        # Проверка на наличие JSON
        json_path = "/home/miku/Документы/AI_MITA_TG/app/handlers/Mita.json"
        if not os.path.exists(json_path):
            await status_msg.edit_text("⚠️ JSON файл не найден.")
            return

        api = ComfyApiWrapper("http://127.0.0.1:8188/")
        wf = ComfyWorkflowWrapper(json_path)

        if character_name in lora_mapping:
            wf.set_node_param("Загрузить LoRA", "lora_name", lora_mapping[character_name])

        wf.set_node_param("Positive", "text", f"{character_prompt}{prompt_text}")
        wf.set_node_param("Пустое латентное изображение", "width", width)
        wf.set_node_param("Пустое латентное изображение", "height", height)

        seed = random.randint(0, 2**63 - 1)
        wf.set_node_param("KSampler", "seed", seed)
        wf.set_node_param("KSampler", "cfg", cfg)

        prompt_id = await api.queue_prompt_and_wait(dict(wf))
        history = api.get_history(prompt_id)
        image_node_id = wf.get_node_id("Сохранить изображение")
        images = history[prompt_id]["outputs"][image_node_id]["images"]

        for img in images:
            img_bytes = api.get_image(img["filename"], img["subfolder"], img["type"])
            await callback.message.answer_photo(
                BufferedInputFile(img_bytes, filename="image.png"),
                caption=f"🎨 <b>Изображение готово</b>\n🎲 Сид: <code>{seed}</code>\n<blockquote>{prompt_text}</blockquote>",
                reply_to_message_id=original_msg_id
            )

        await status_msg.delete()
    except CancelledError:
        await status_msg.edit_text("❌ Генерация отменена пользователем.")
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка генерации:\n<code>{str(e)}</code>")
    finally:
        generation_tasks.pop(callback.from_user.id, None)
        await state.clear()
