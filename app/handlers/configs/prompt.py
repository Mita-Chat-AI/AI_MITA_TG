from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext


from ...entities import Bio
from ...services.config_service import UserConfigService


prompt_router = Router()


@prompt_router.message(Command('setbio'))
async def mybio(message: Message, state: FSMContext) -> None:
    await state.set_state(Bio.bio)
    await message.reply(f"""
😘 | <b>Пупс, расскажи мне о себе по-подробней.</b>
┗ Опиши себя: сколько тебе лет? Чем занимаешься? А так же, как я должна с тобой общаться?

🤔 | <b>К примеру:</b>
<blockquote>Меня зовут Паша, мне 17 лет, я занимаюсь программированием. Я хочу, что бы ты называла меня по имени, а так же, относилась ко мне с любовью.</blockquote>
"""
    )


@prompt_router.message(Bio.bio)
async def mybio_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(bio=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    configurator = UserConfigService(user_id)
    
    await message.reply(f"""
✅ | <b>Отлично! Я записала твое описание:</b>
┗ Теперь, даже если, я забуду о нашей переписки, я буду помнить о тебе вечность. ☺️      

🤔 | <b>Твоё био:</b>
<blockquote>{data['bio']}</blockquote>               
""")

    await configurator.setprompt(data['bio'])
    await state.clear()
