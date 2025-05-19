from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums.chat_type import ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery

from ...entities import IsHistory
from ...database.requests import DatabaseManager


is_history  = Router()


@is_history.message(Command('history'), F.chat.type == ChatType.PRIVATE)
async def show_history_options(message: Message, state:  FSMContext):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text="Включить",
        callback_data="onhistory"
    ))
    builder.add(InlineKeyboardButton(
        text="Выключить",
        callback_data="offhistory"
    ))
    builder.adjust(2)

    await state.set_state(IsHistory.history)
    await state.update_data(user_id=message.from_user.id)

    await message.answer( 
'''
<b>
❓ |  Что делаем с вашей историей чата
┗ Выключить -> Мита не сохраняет её.
┗ Включить -> Мита сохраняет её.
</b>
''', 
reply_markup=builder.as_markup(resize_keyboard=True))


@is_history.callback_query(IsHistory.history)
async def is_hupdate_history_settingistorys(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    state_data = await state.get_data()
    user_id = state_data.get("user_id")
    db = DatabaseManager(user_id)

    is_history = None
    if data == 'onhistory':
        is_history = True
    else:
        is_history = False

    await db.set_is_history(is_history)

    await callback.message.reply(f"Теперь у вас {'сохрается история чата' if is_history else 'Не сохраняется история чата'}")
    await state.clear()