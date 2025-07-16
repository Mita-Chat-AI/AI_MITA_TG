from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from aiogram.enums.chat_type import ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery


from ...entities import PersonState
from ...database.requests import DatabaseManager


voice_person_router = Router()


person = {
    "CrazyMita": "Безумная Мита",
    "CapMita": "Кепочка Мита",
    "KindMita": "Добрая Мита",
    "SleepyMita": "Сонная Мита",
    "Player": "Игрок",
    "MilaMita": "МиЛа",
    "PhoneMita": "МитаФОН",
    "ShortHairMita": "Коротко волосая :)",
    "TinyMita": "Маленькая-уродливая",
    "GhostMita": "Призрачная Мита"

}



@voice_person_router.message(Command("set_person"), F.chat.type == ChatType.PRIVATE)
async def set_voice_person(message: Message, command: CommandObject, state: FSMContext):
    args = command.args

    if not args:
        builder = InlineKeyboardBuilder()
        for key, value in person.items():
            builder.add(InlineKeyboardButton(
                text=value,
                callback_data=key
            ))
        builder.adjust(2)

        await state.set_state(PersonState.wait_person)
        await state.update_data(user_id=message.from_user.id)

        await message.answer(f"🗳 | <b>Выбери голос, который хочешь использовать для /voice</b>", reply_markup=builder.as_markup(resize_keyboard=True))
    else:
        if args in person:
            db  = DatabaseManager(message.from_user.id)
            await db.set_voice_person(args)
            await state.clear()
            await message.reply(f"✅ | <b>Вы успешно выбрали {person[args]} в качестве персонажа.</b>")
        else:
            await message.reply("К сожалению, я не нашла такого голоса :)")


@voice_person_router.callback_query(PersonState.wait_person)
async def set_person(callback : CallbackQuery, state: FSMContext):
    data = callback.data
    state_data = await state.get_data()
    user_id = state_data.get("user_id")

    db  = DatabaseManager(user_id)
    await db.set_voice_person(data)
    await callback.message.reply(f"✅ | <b>Вы успешно выбрали {person[data]} в качестве персонажа.</b>")
    await state.clear()