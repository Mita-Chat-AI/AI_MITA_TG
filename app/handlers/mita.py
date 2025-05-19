import os
import base64
from io import BytesIO

import cv2
from PIL import Image
from aiogram import Router, Bot, F
from aiogram.enums.chat_type import ChatType
from aiogram.enums import ChatAction, ContentType
from aiogram.types import Message, BufferedInputFile

from ..services.asr import ASR
from .voice import voice_generate
from ...config_reader import config
from ..mitacore.memory import Memory
from ..utils.utils import memory_chars
from ..mitacore.mita_handler import Mita
from ..database.requests import DatabaseManager
from ..services.config_service import UserConfigService


mita_router = Router()


async def voice(message: Message, bot: Bot):
    try:
        audio_bytes: BytesIO = await bot.download(file=message.voice)
        text = await ASR(audio_bytes).recognition()
        return text.get('text')
    except Exception as e:
        await message.reply(f"Кажется, я не смогла распознать твой голос  {e}")
        return


async def images(message: Message, bot: Bot):
    try:
        if message.photo:
            file_id = message.photo[-1].file_id
            file_path = f"/tmp/{file_id}.jpg"
            await bot.download(file_id, destination=file_path)


            prompt = message.caption
            if not prompt:
                prompt = "Дай свою реакцию на это фото очень кратко"
            return prompt, file_path

        elif message.sticker:
            file = message.sticker
            file_info = await bot.get_file(file.file_id)
            file_ext = ".webp"
            if file.is_animated:
                file_ext = ".tgs"
            elif file.is_video:
                file_ext = ".webm"
            file_path = f"/tmp/{file.file_id}{file_ext}"

            await bot.download(file, destination=file_path)

            # Конвертация webm в webp, если это видео-стикер
            if file_ext == ".webm":
                webp_path = f"/tmp/{file.file_id}_converted.webp"
                cap = cv2.VideoCapture(file_path)
                success, frame = cap.read()
                cap.release()
                if success:
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    image.save(webp_path, format="WEBP")
                    os.remove(file_path)  # Удаляем оригинальный .webm
                    file_path = webp_path  # Используем путь к новому webp-файлу
                else:
                    await message.reply("❌ Не удалось извлечь кадр из видео-стикера")
                    return None, None
        else:
            return None, None

        prompt = message.caption
        if not prompt:
            prompt = "Дай свою реакцию на это фото очень кратко"
        return prompt, file_path

    except Exception as e:
        await message.reply(f"❌ Не удалось скачать или обработать стикер: {e}")
        return None, None






@mita_router.message(F.chat.type == ChatType.PRIVATE,  F.content_type.in_([ContentType.TEXT, ContentType.PHOTO, ContentType.VOICE, ContentType.STICKER]))
async def mita(message: Message, bot: Bot) -> Message:
    user_id = message.from_user.id
    mita = Mita()
    configurator = UserConfigService(user_id)
    db = DatabaseManager(user_id)

    memory = Memory(user_id).memory

    prompt = message.text
    if prompt is None:
        prompt = '/ask'
    text = [{
        'role': 'user',
        'content': prompt


    }]


    if message.photo or message.sticker:
        prompt, file_path = await images(message, bot)
        # with open(file_path, "rb") as image_file:
        #     b64_image = base64.b64encode(image_file.read()).decode("utf-8")
        # print(b64_image)

        if not file_path:
            return
        text = [{"role": "user", "content": prompt, 'images': [file_path]}]
        # text = [{
        #     "role": "user",
        #     "content": [
        #         {"type": "text", "text": prompt},
        #         {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
        #     ]
        # }]

    elif message.voice:
        prompt = await voice(message, bot)
        if not prompt:
            return
        text = [{"role": "user", "content": prompt}]
    
    user_chars, mita_chars = await memory_chars(memory)

    if user_chars + mita_chars > int(config.max_ollama_chars.get_secret_value()):
        await message.reply("<b>💔 | К сожалению, моя память стёрлась из-за лимитов.</b>")
        Memory(user_id).reset_memory()
        return

    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    ai_response = await mita.call_llm(
        user_id,
        memory,
        text
    )

    user_chars, mita_chars = await memory_chars(Memory(user_id).memory)
    all_chars = user_chars+mita_chars
    await configurator.set_stats(
        user_chars,
        mita_chars,
        all_chars,
        ai_response.get('time_response'),
        ai_response.get('user_time')
    )

    if await db.get_voice_mode() and len(ai_response.get('response')) > 10:
        voice_buffer = await voice_generate(user_id, ai_response.get('response'))
        response = await message.reply_voice(
            BufferedInputFile(
                voice_buffer.content,
                filename="voice.ogg"
            ), 
            mime_type="audio/ogg"
        )
        
        return response
    else:
        import json

        raw_response = json.loads(ai_response["response"])


        if raw_response.get("text") and raw_response["text"].strip():
            response = await message.reply(f"<b>{raw_response['text']}</b>")
            return response

        elif raw_response.get("reactions"):
            print("REACTION SEND")
            from aiogram.types.reaction_type_emoji import ReactionTypeEmoji

            reaction = [ReactionTypeEmoji(emoji=raw_response["reactions"])]
            response = await bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=reaction
            )
            return response




        



# @voice_router.message(Command("reaction"), F.from_user.id == 6506201559)
# async def reasctins(message: Message, bot: Bot):
#     reaction = [ReactionTypeEmoji(emoji='👍')]
#     result = await bot.set_message_reaction(
#         chat_id=message.chat.id,
#         message_id=message.message_id,
#         reaction=reaction
#     )
#     await message.reply(f"{result}")

#     ret = await bot.get_chat(chat_id=8102139305)

#     await message.reply(f"{ret}")
