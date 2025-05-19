from aiogram import Dispatcher, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore

from .app.handlers import (start_router,
                           i18n_router,
                           help_router,
                           blocked_router,
                           mita_router,
                           prompt_router,
                           stats_router,
                           reset_router,
                           ask_router,
                           voice_person_router,
                           voice_router,
                           voice_lang,
                           is_history,
                           voicemod_router,
                           conditions_accept_router
                           )
from .app.database.db import async_main
from .config_reader import config
from .app.middlwares.main_middlware import MainMiddlware


async def main() -> None:
    import logging

    logging.basicConfig(level=logging.INFO)

    await async_main()
    dp = Dispatcher()

    

    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(
            path="/home/miku/AIO-MITA/app/locales/{locale}/LC_MESSAGES",
            default_locale='ru'
        )
    )

    dp.include_routers(
        start_router,
        i18n_router,
        help_router,
        blocked_router,
        prompt_router,
        stats_router,
        reset_router,
        voice_person_router,
        voice_router,
        voice_lang,
        is_history,
        voicemod_router,
        conditions_accept_router,

        ask_router,
        mita_router
        
    )

    start_router.message.middleware(MainMiddlware())
    help_router.message.middleware(MainMiddlware())
    mita_router.message.middleware(MainMiddlware())
    voice_router.message.middleware(MainMiddlware())

    voice_lang.message.middleware(MainMiddlware())
    voicemod_router.message.middleware(MainMiddlware())
    ask_router.message.middleware(MainMiddlware())

    async with bot:
        await bot.send_message(
            chat_id=config.owner_id.get_secret_value(),
            text=f"Привет! Я заработала!"
        )

    i18n_middleware.setup(dispatcher=dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
