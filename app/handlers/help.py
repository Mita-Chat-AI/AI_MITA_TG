from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command


help_router = Router()


@help_router.message(Command('help'))
async def help(message: Message) -> None:
    await message.reply(
        text="""
<b>❓ | Вот, что я умею:</b>
—————
┗ /voice текст-> [сгенерировать голосовое сообщение].
┗ /voice_lang -> [поменять Язык миты в /voice].
┗ /reset -> [Стереть всю память].
┗ /history -> [Настройки сохранения памяти].
┗ /set_tokens -> [Установить лимит слов на ответ].
┗ /stats -> [Получить статистику по нашему общению].
—————
<u>Просто напиши мне что-нибудь, и я отвечу!</u>
            """
    )