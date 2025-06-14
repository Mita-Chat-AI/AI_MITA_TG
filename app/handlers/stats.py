import json
import statistics
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

from ..database.requests import DatabaseManager


stats_router = Router()


from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
import statistics

from ..database.requests import DatabaseManager

stats_router = Router()

@stats_router.message(Command('stats'))
async def stats(message: Message) -> None:
    db = DatabaseManager(message.from_user.id)
    stats = await db.get_statistik()

    avg_response_time = (
        int(statistics.mean(stats["time_response"][-10:])) if stats["time_response"] else 0
    )
    last_user_time = stats["user_time"][-1] if stats["user_time"] else "Нет данных"
    last_voice_use = stats["voice_use"][-1] if stats["voice_use"] else "Не использовалось"
    
    # Распознанные фразы
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

📝 Символов юзера: <code>{stats["user_chars"]}</code>
🤖 Символов Миты: <code>{stats["mita_chars"]}</code>
📈 Среднее время ответа: <code>{avg_response_time}</code> сек

⏱ Последнее взаимодействие: <code>{last_user_time}</code>
🎙 Последнее использование голоса: <code>{last_voice_use}</code>

🗣 <b>Распознанные фразы:</b>
{voice_texts_str}
"""
    )