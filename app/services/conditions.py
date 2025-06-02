from aiogram import Router, F
from aiogram_i18n import I18nContext
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


from ..database.requests import DatabaseManager


conditions_accept_router = Router()


async def conditions_accept(message: Message, i18n: I18nContext) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=i18n.get("conditions_accept"),
            callback_data="accept_conditions"
        )
    )

    await message.reply(text=i18n.get("conditions"),
        reply_markup=builder.as_markup()
    )


@conditions_accept_router.callback_query(F.data == "accept_conditions")
async def handle_accept_conditions(callback: CallbackQuery, i18n: I18nContext) -> None:
    db = DatabaseManager(callback.from_user.id)

    await db.set_conditions(True)
    await callback.message.reply(text=i18n.get("conditions_acception"))


@conditions_accept_router.message(Command('conditions'))
async def conditions_handler(message: Message, i18n: I18nContext) -> None:
        await message.reply(text=i18n.get("conditions"))