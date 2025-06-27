from aiogram import Router, F, Bot
from aiogram.types import Message
from datetime import datetime, timedelta
from aiogram.filters.command import Command

from ...database.requests import DatabaseManager


subscribe_router = Router()


@subscribe_router.message(Command('s'), F.from_user.id == 6506201559)
async def subscribe(message: Message, bot: Bot) -> None:
    text = message.text.split()

    if len(text) < 3:
        await message.reply("Неправильно используешь команду. Пример: /s ID1 ID2 ID3 + или -")
        return

    action = text[-1].lower()
    user_ids = text[1:-1]

    if action not in ('+', '-'):
        await message.reply('Ошибка! Последним аргументом должно быть + или -')
        return

    success = []
    failed = []

    for user_id_str in user_ids:
        try:
            user_id = int(user_id_str)
            db = DatabaseManager(user_id)

            if action == '+':
                period = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                await db.set_subscribe(1, period)
                await bot.send_message(
                    chat_id=user_id,
                    text=f"<b>✅ | Вам была активирована подписка на второй движок.</b>\n┗Период: до {period}"
                )
                success.append(f"{user_id} | ✅")
            else:
                await db.set_subscribe(0, None)
                await bot.send_message(
                    chat_id=user_id,
                    text=f"<b>❌ | Подписка на второй движок была деактивирована.</b>\n┗Вопросы или для покупки: @BugsCrazyMitaAIbot / @astolfo_potyjniy"
                )
                success.append(f"{user_id} ❌")

        except Exception as e:
            failed.append(f"{user_id_str} ⚠️ ({e})")

    report = f"✅ Успешно: {len(success)}\n" + "\n".join(success)
    if failed:
        report += f"\n\n⚠️ Ошибки: {len(failed)}\n" + "\n".join(failed)

    await message.reply(report)