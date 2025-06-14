from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from aiogram.enums.chat_type import ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery


from ...entities import Isvoice_engine
from ...database.requests import DatabaseManager


set_voice_engine_router = Router()


person = {
    "edge": "Бесплатный",
    "vosk": "Условно бесплатный",

}



@set_voice_engine_router.message(Command("set_voice"))#, F.chat.type == ChatType.PRIVATE)
async def set_voice_person(message: Message, command: CommandObject, state: FSMContext):
    args = command.args

    if not args:
        builder = InlineKeyboardBuilder()
        for key, value in person.items():
            builder.add(InlineKeyboardButton(
                text=value,
                callback_data=key
            ))
        builder.adjust(1)

        await state.set_state(Isvoice_engine.is_voice_engine)
        await state.update_data(user_id=message.from_user.id)

        await message.answer(f"🗳 | <b>Выбери <u>голосовой движок</u>, который хочешь использовать для /voice</b>", reply_markup=builder.as_markup(resize_keyboard=True))



@set_voice_engine_router.callback_query(Isvoice_engine.is_voice_engine)
async def set_person(callback : CallbackQuery, state: FSMContext):
    data = callback.data
    state_data = await state.get_data()
    user_id = state_data.get("user_id")

    db  = DatabaseManager(user_id)
    await db.set_voice_engine(data)
    await callback.message.reply(f"✅ | <b>Вы успешно выбрали {person[data]} в качестве <u>Голосового движка</u>.</b>")
    await state.clear()