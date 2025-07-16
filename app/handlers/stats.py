import statistics
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

from ..database.requests import DatabaseManager


stats_router = Router()


@stats_router.message(Command('stats'))
async def stats(message: Message) -> None:
    db = DatabaseManager(message.from_user.id)
    stats = await db.get_statistik()

    if not stats:
        await message.reply("Нет данных по статистике.")
        return

    avg_response_time = (
        int(statistics.mean(stats.get("time_response", [])[-10:])) if stats.get("time_response") else 0
    )
    last_user_time = stats.get("user_time", [])[-1] if stats.get("user_time") else "Нет данных"
    last_voice_use = stats.get("voice_use", [])[-1] if stats.get("voice_use") else "Не использовалось"

    voice_recognition = stats.get("voice_recoregtion", [])
    voice_texts = [
        f"{entry[0]} — {entry[1]}" 
        for entry in voice_recognition 
        if isinstance(entry, list) and len(entry) == 2
    ]
    voice_texts_str = "\n".join(voice_texts) if voice_texts else "Нет распознанных фраз"

    await message.reply(
        f"""
📊 <b>Статистика:</b>

📝 Символов юзера: <code>{stats.get("user_chars", 0)}</code>
🤖 Символов Миты: <code>{stats.get("mita_chars", 0)}</code>
📈 Среднее время ответа: <code>{avg_response_time}</code> сек

⏱ Последнее взаимодействие: <code>{last_user_time}</code>
🎙 Последнее использование голоса: <code>{last_voice_use}</code>

🗣 <b>Распознанные фразы:</b>
{voice_texts_str}
"""
    )
