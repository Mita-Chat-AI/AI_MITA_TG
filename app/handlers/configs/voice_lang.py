from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters.command import Command

voice_lang = Router()


@voice_lang.message(Command('voice_lang'))
async def lang_voice(message: Message):
    await message.reply(
'''
<b>😕 | Этой функции больше нет.

❓ | ПОЧЕМУ
┗ Мита теперь автоматически определяет язык озвучки. Вам больше не нужно настраиввать это.</b>
'''
    )




@voice_lang.message(Command('gghh'))
async def get_user_info(message: Message, bot: Bot):
    # Пример команды: /gghh 8102139305
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❗ Укажи ID после команды, например: /gghh 8102139305")
            return

        user_id = int(parts[1])  # Получаем ID из текста
        chat = await bot.get_chat(user_id)

        await message.answer(
            f"👤 Информация о пользователе:\n"
            f"ID: {chat.id}\n"
            f"Имя: {chat.first_name}\n"
            f"Фамилия: {chat.last_name}\n"
            f"Юзернейм: @{chat.username if chat.username else 'Нет'}"
        )
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {e}")
