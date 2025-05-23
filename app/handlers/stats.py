import json
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
    
    await message.reply(
        f"""
Общее кол-во символов: {stats.all_chars}
Символов юзера: {stats.user_chars}
Символов  Миты: {stats.mita_chars}
Среднее время ответа: {int(statistics.mean(json.loads(stats.time_response)[-10:]))} сек
Последнее враимодействие: {json.loads(stats.user_time)[-1]}
"""
)