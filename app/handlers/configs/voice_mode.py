from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.enums.chat_type import ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery

from ...entities import VoiceModState
from ...database.requests import DatabaseManager


voicemod_router = Router()


person = {
    True: "Включить войс мод",
    False: "Выключить войс мод"
}


@voicemod_router.message(Command("set_voicemod",), F.chat.type == ChatType.PRIVATE)
async def set_voicemod(message: Message, state: FSMContext):
    
    builder = InlineKeyboardBuilder()
    for key_bool in person.keys():
        button_text = person[key_bool]

        callback_data_str = str(key_bool)
        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data_str
        ))
    builder.adjust(1)

    await state.set_state(VoiceModState.wait_voice_mod)
    await state.update_data(user_id=message.from_user.id)

    await message.answer("<b>❓ | voice-mod, это режим, при котором, Мита вместо текста, будет отправлять голосовые сообщения.</b>", reply_markup=builder.as_markup(resize_keyboard=True))


@voicemod_router.callback_query(VoiceModState.wait_voice_mod)
async def set_mod(callback : CallbackQuery, state: FSMContext):
    # callback.data теперь будет строкой: "True" или "False"
    callback_data_str = callback.data
    state_data = await state.get_data()
    user_id = state_data.get("user_id")

    try:
        new_voice_mode_state = callback_data_str == "True"
    except Exception as e:
        print(f"Ошибка преобразования callback_data: {callback_data_str}, ошибка: {e}")
        await callback.answer("Произошла ошибка.", show_alert=True)
        await state.clear()
        return

    if user_id:
        try:
            db = DatabaseManager(user_id)
            await db.set_voice_mode(new_voice_mode_state)

            feedback_message = person[new_voice_mode_state].replace("ить", "ен")
            await callback.answer(f"Статус обновлен: {feedback_message}")
            await callback.message.edit_text(f"Статус обновлен: {feedback_message}", reply_markup=None)
        except Exception as e:
            print(f"Ошибка при обновлении статуса войс мода для {user_id}: {e}")
            import traceback
            traceback.print_exc()
            await callback.answer("Не удалось сохранить настройку.", show_alert=True)
        finally:
            await state.clear()
    else:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        await state.clear()