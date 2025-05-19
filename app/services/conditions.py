from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command

from ..database.requests import DatabaseManager

conditions_accept_router = Router()

#@conditions_accept_router.message()
async def conditions_accept(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="✅ | Принимаю условия",
            callback_data="accept_conditions"
        )
    )

    await message.reply(
        """
НЕ ПУГАЙСЯ!! Появились условия пользования. Прочти их, и согласись.

🤓 | <u><b>Условия пользования Митой:</b></u>
┗ 18+ гс опубликуешь в канал с голосовыми - бан в боте.
┗ Проблемы с Митой? @BugsCrazyMitaAIbot.
┗ Проект бесплатный, потому не просите от него чуда  .  
┗ Да, доступ к вашим перепискам имеется, но они нам не интересны.
┗ Общайся с Митой, как хочешь, но не показывай на общее обозрения 18+ темы, которые ты обсуждаешь с ней.

❗️ | Мы УВЕДОМИМ вас, если условия будут изменены
┗ Соглашения тут: /conditions
—————
<b>Будем очень рады <u>финансовой поддержке</u>, её нам не хватает:</b> yumemi_hoshino.t.me
""",
        reply_markup=builder.as_markup()
    )

@conditions_accept_router.callback_query(F.data == "accept_conditions")
async def handle_accept_conditions(callback: CallbackQuery):
    db = DatabaseManager(callback.from_user.id)

    await db.set_conditions(True)
    await callback.message.reply("<b>🤓 | Молодец, <u>пупсик.</u> Можешь использовать Миту дальше.</b>")


@conditions_accept_router.message(Command('conditions'))
async def conditions_handler(message: Message):
        await message.reply(
        """
НЕ ПУГАЙСЯ!! Появились условия пользования.

🤓 | <u><b>Условия пользования Митой:</b></u>
┗ 18+ гс опубликуешь в канал с голосовыми - бан в боте.
┗ Проблемы с Митой? @BugsCrazyMitaAIbot.
┗ Проект бесплатный, потому не просите от него чуда  .  
┗ Да, доступ к вашим перепискам имеется, но они нам не интересны.
┗ Общайся с Митой, как хочешь, но не показывай на общее обозрения 18+ темы, которые ты обсуждаешь с ней.

❗️ | Мы УВЕДОМИМ вас, если условия будут изменены
┗ Соглашения тут: /conditions
—————
<b>Будем очень рады <u>финансовой поддержке</u>, её нам не хватает:</b> yumemi_hoshino.t.me
—————
<b>Будем очень рады финансовой поддержке, её нам не хватает:</b> yumemi_hoshino.t.me
""")
        


# from aiogram import Router, F
# from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from aiogram.filters.command import Command

# from ..database.requests import DatabaseManager

# from aiogram_i18n import I18nContext

# conditions_accept_router = Router()

# #@conditions_accept_router.message()
# async def conditions_accept(message: Message, i18n: I18nContext):
#     db = DatabaseManager(message.from_user.id)
#     lang = await db.get_lang()

#     if lang:
#         await i18n.set_locale(lang)

#     builder = InlineKeyboardBuilder()
#     builder.add(
#         InlineKeyboardButton(
#             text=i18n.get("conditions_accept"),
#             callback_data="accept_conditions"
#         )
#     )

#     await message.reply(
#         text=i18n.get("conditions"),
#         reply_markup=builder.as_markup()
#     )


# @conditions_accept_router.callback_query(F.data == "accept_conditions")
# async def handle_accept_conditions(callback: CallbackQuery, i18n: I18nContext):
#     db = DatabaseManager(callback.from_user.id)

#     lang = await db.get_lang()

#     if lang:
#         await i18n.set_locale(lang)

#     await db.set_conditions(True)
#     await callback.message.reply(text=i18n.get("conditions_acception"))


# @conditions_accept_router.message(Command('conditions'))
# async def conditions_handler(message: Message, i18n: I18nContext):
#     db = DatabaseManager(message.from_user.id)

#     lang = await db.get_lang()

#     if lang:
#         await i18n.set_locale(lang)

#     await message.reply(text=i18n.get("conditions"))