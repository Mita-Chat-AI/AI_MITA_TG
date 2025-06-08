from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command, CommandStart
from aiogram_i18n import I18nContext, LazyProxy
from aiogram_i18n.types import InlineKeyboardButton
from aiogram_i18n.utils.language_inline_keyboard import LanguageInlineMarkup

from ..database.requests import DatabaseManager
from .start import start


i18n_router = Router()

#async def start(message: Message, i18n: I18nContext, state: FSMContext) -> None:

lang_kb = LanguageInlineMarkup(
    key="lang_button",
    hide_current=False,
    keyboard=[[InlineKeyboardButton(text=LazyProxy("back"), callback_data="back")]],
)



@i18n_router.callback_query(lang_kb.filter)
async def btn_help(call: CallbackQuery, lang: str, i18n: I18nContext, state: FSMContext) -> None:
    db = DatabaseManager(call.from_user.id)

    await call.answer()
    await db.set_lang(lang=lang)

    await i18n.set_locale(lang)

    await call.message.edit_text(text=i18n.get("cur-lang", language=await db.get_lang()))
    await start(call.message, i18n, state)


@i18n_router.message(Command("lang"))
async def cmd_langg(message: Message, i18n: I18nContext) -> None:
        db = DatabaseManager(message.from_user.id)
        
        await message.reply(
            text=i18n.get("cur-lang", language=await db.get_lang()), reply_markup=lang_kb.reply_markup()
        )


@i18n_router.message(CommandStart())
async def cmd_lang(message: Message, i18n: I18nContext, state: FSMContext) -> None:
    db = DatabaseManager(message.from_user.id)
    await db.set_user()

    if await db.get_lang() == "null":
        print(2)
        await message.reply(
            text=i18n.get("cur-lang", language=i18n.locale), reply_markup=lang_kb.reply_markup()
        )
        return
    else:
        await start(message, i18n, state)

