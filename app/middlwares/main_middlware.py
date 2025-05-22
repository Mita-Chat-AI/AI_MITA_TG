from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message
from aiogram.types.chat_member_owner import ChatMemberOwner
from aiogram.types.chat_member_member import ChatMemberMember
from aiogram.types.chat_member_administrator import ChatMemberAdministrator

from  ..database.requests import DatabaseManager
from ..services.conditions import conditions_accept
from aiogram_i18n import I18nContext

class MainMiddlware(BaseMiddleware):
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        bot: Bot = data['bot']
        db = DatabaseManager(event.from_user.id)
        await db.set_user()

        i18n: I18nContext = data['i18n']
        if event.text and event.text.startswith('/'): # Проверяем что сообщение не пустое и начинается с /
            lang = await db.get_lang()
            if lang != 'null':
                print("gfgggfgfg", lang)
                await i18n.set_locale(lang)
            else:
                from ..handlers.i18n import cmd_lang
                await cmd_lang(event, i18n)
                return


        conditions = await db.get_conditions()
        if not conditions and not event.reply_to_message:
            if event.text.startswith('/voice'):
                await bot.copy_message(
                    chat_id=event.chat.id,
                    from_chat_id='@CrazyMitaAIvoices',
                    message_id=5375
                )
                return
            lang = await db.get_lang()
            if lang != 'null':
                print("gfgggfgfg", lang)
                await i18n.set_locale(lang)
            else:
                from ..handlers.i18n import cmd_lang
                await cmd_lang(event, i18n)
                return

            await conditions_accept(event, i18n)
            return

        is_blocked = await db.get_is_blocked_user()

        if is_blocked and not event.reply_to_message:
            await bot.send_message(
                chat_id=event.chat.id,
                text="К сожалению, вы были заблокированы. напишите @BugsCrazyMitaAIbot для подробностей",
                reply_to_message_id=event.message_id
            )
            return

        # await bot.send_message(
        #     chat_id=-1002471083299,
        #     text=f"{event.from_user.id}, {event.text}"
        # )


        # Проверяем, является ли сообщение командой
        if event.text and event.text.startswith('/'): # Проверяем что сообщение не пустое и начинается с /
            channel_id = -1002286457175

            get_member = await bot.get_chat_member(chat_id=channel_id, user_id=event.from_user.id)
            
            if isinstance(
                get_member, (
                    ChatMemberMember, 
                    ChatMemberAdministrator, 
                    ChatMemberOwner
                )
            ):
                # Пользователь подписан, пропускаем дальше
                pass
            else:
                await bot.send_message(
                    chat_id=event.chat.id,
                    text=f"Вам нужно подписаться на @CrazyMitaAINews прежде чем взаимодействовать с Митой.",
                    reply_to_message_id=event.message_id
                )
                return

        result = await handler(event, data)
        return result
