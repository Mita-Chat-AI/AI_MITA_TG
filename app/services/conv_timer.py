import asyncio
from datetime import datetime, timedelta

from aiogram import Router, Bot

from ...config_reader import config
from ..database.requests import DatabaseManager
from ..database.requests import statistik_collection



conv_timer_router = Router()


async def mailing_loop(bot: Bot):
    while True:
        await asyncio.sleep(300)

        now = datetime.utcnow()
        two_days_ago = now - timedelta(days=2)


        async for user in statistik_collection.find({"conv": 1}):
            print( user)
            tg_id = user["tg_id"]
            print(tg_id)
            user_times = user.get("user_time", [])
            print(user_times)

            if not user_times:
                continue

            try:
                last_time = datetime.strptime(user_times[-1], "%Y-%m-%d %H:%M:%S")
            except:
                continue

            if last_time < two_days_ago:
                await bot.send_message(chat_id=tg_id, text="👋 | Привет! ТЫ со мной.. Кажется.. Давно не общался.. Может пообщаемся?")
                await bot.send_message(chat_id=config.owner_id.get_secret_value(), text=f"Я написала пользователю {tg_id}, о том, что бы я с ним по общалась :)")

                db = DatabaseManager(tg_id)
                await db.set_conv(0)
                return

@conv_timer_router.startup()
async def on_startup_mailing(bot: Bot):
    asyncio.create_task(mailing_loop(bot))
