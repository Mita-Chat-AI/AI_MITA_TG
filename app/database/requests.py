from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from ...config_reader import config
from .db import UserModel, StatistikModel, SubscribeModel


client = AsyncIOMotorClient(config.mongo_db.get_secret_value())#"mongodb://localhost:27017")
db = client[config.mongo_name.get_secret_value()]
users_collection = db["users"]
statistik_collection = db["statistiks"]
subscribe_collection = db['subscribes']

class DatabaseManager:
    def __init__(self, tg_id: int):
        self.tg_id = tg_id

    async def set_user(self) -> None:
        if not await users_collection.find_one({"tg_id": self.tg_id}):
            await users_collection.insert_one(UserModel(tg_id=self.tg_id).dict(by_alias=True))
            await statistik_collection.insert_one(StatistikModel(tg_id=self.tg_id).dict(by_alias=True))
            await subscribe_collection.insert_one(SubscribeModel(tg_id=self.tg_id).dict(by_alias=True))
            logger.info("User and Statistik created")
    
    async def get_is_blocked_user(self) -> bool:
        user = await users_collection.find_one({"tg_id": self.tg_id})
        return user.get("is_blocked", False) if user else False

    async def set_blocked_user(self, blocked: bool) -> bool:
        await users_collection.update_one({"tg_id": self.tg_id}, {"$set": {"is_blocked": blocked}})
        return await self.get_is_blocked_user()

    async def set_user_chars(self, user_chars: int) -> None:
        await statistik_collection.update_one({"tg_id": self.tg_id}, {"$set": {"user_chars": user_chars}})

    async def set_mita_chars(self, mita_chars: int) -> None:
        await statistik_collection.update_one({"tg_id": self.tg_id}, {"$set": {"mita_chars": mita_chars}})

    async def set_all_chars(self, all_chars: int) -> None:
        await statistik_collection.update_one({"tg_id": self.tg_id}, {"$set": {"all_chars": all_chars}})

    async def get_statistik(self):
        return await statistik_collection.find_one({"tg_id": self.tg_id})

    async def set_time_response(self, new_time: str) -> None:
        await statistik_collection.update_one({"tg_id": self.tg_id}, {"$push": {"time_response": new_time}})

    async def set_user_time(self, new_time: str) -> None:
        await statistik_collection.update_one({"tg_id": self.tg_id}, {"$push": {"user_time": new_time}})

    async def set_voice_use(self, new_voice_use: str) -> None:
        await statistik_collection.update_one({"tg_id": self.tg_id}, {"$push": {"voice_use": new_voice_use}})

    async def set_voice_recoregtion(self, new_voice_recoregtion: str) -> None:
        await statistik_collection.update_one({"tg_id": self.tg_id}, {"$push": {"voice_recoregtion": new_voice_recoregtion}})

    async def set_system_prompt(self, system_prompt: str) -> None:
        await users_collection.update_one({"tg_id": self.tg_id}, {"$set": {"system_prompt": system_prompt}})

    async def get_system_prompt(self):
        user = await users_collection.find_one({"tg_id": self.tg_id})
        return user.get("system_prompt") if user else None

    async def set_voice_person(self, person_voice: str):
        await users_collection.update_one({"tg_id": self.tg_id}, {"$set": {"person_voice": person_voice}})

    async def get_voice_person(self):
        user = await users_collection.find_one({"tg_id": self.tg_id})
        return user.get("person_voice") if user else None

    async def set_is_history(self, is_history: bool):
        await users_collection.update_one({"tg_id": self.tg_id}, {"$set": {"is_history": is_history}})

    async def get_is_history(self):
        user = await users_collection.find_one({"tg_id": self.tg_id})
        return user.get("is_history") if user else None

    async def set_voice_mode(self, voice_mode: bool):
        await users_collection.update_one({"tg_id": self.tg_id}, {"$set": {"voice_mode": voice_mode}})

    async def get_voice_mode(self):
        user = await users_collection.find_one({"tg_id": self.tg_id})
        return user.get("voice_mode") if user else None

    async def get_conditions(self):
        user = await users_collection.find_one({"tg_id": self.tg_id})
        return user.get("conditions") if user else None

    async def set_conditions(self, conditions: bool):
        await users_collection.update_one({"tg_id": self.tg_id}, {"$set": {"conditions": conditions}})

    async def get_lang(self):
        user = await users_collection.find_one({"tg_id": self.tg_id})
        return user.get("lang", "ru") if user else "ru"

    async def set_lang(self, lang: str):
        await users_collection.update_one({"tg_id": self.tg_id}, {"$set": {"lang": lang}})

    async def set_conv(self, conv: int) -> None:
        await statistik_collection.update_one({"tg_id": self.tg_id}, {"$set": {"conv": conv}})

    async def get_conv(self):
        user = await users_collection.find_one({"tg_id": self.tg_id})
        return user.get("conv") if user else None
    
    async def set_voice_engine(self, voice_engine: int) -> None:
        await users_collection.update_one({"tg_id": self.tg_id}, {"$set": {"voice_engine": voice_engine}})

    async def get_voice_engine(self):
        user = await users_collection.find_one({"tg_id": self.tg_id})
        print(user.get("get_voice_engine"))
        return user.get("voice_engine") if user else "edge"
    

    async def set_subscribe(self, subscribe: int, period: str = None) -> None:
        """Установить или обновить подписку пользователя."""
        await subscribe_collection.update_one(
            {"tg_id": self.tg_id},
            {"$set": {"subscribe": subscribe, "period": period}},
            upsert=True  # если документа нет — создать
        )

    async def get_subscribe(self) -> dict:
        """Получить статус подписки пользователя. Если нет — вернуть дефолт."""
        doc = await subscribe_collection.find_one({"tg_id": self.tg_id})

        return {
            "subscribe": doc.get("subscribe"),
            "period": doc.get("period"),
            "free_voice": doc.get("free_voice"),
            "left_free_voice": doc.get("left_free_voice")
        }

    async def increment_free_voice(self):
        await subscribe_collection.update_one(
            {"tg_id": self.tg_id},
            {"$inc": {"free_voice": 1}}
        )

    async def get_free_voice(self) -> int:
        doc = await subscribe_collection.find_one({"tg_id": self.tg_id})
        return doc.get("free_voice", 0) if doc else 0

    async def set_free_voice(self, value: int):
        await subscribe_collection.update_one({"tg_id": self.tg_id}, {"$set": {"free_voice": value}})

    async def set_let_free_voice(self, value: int):
        await subscribe_collection.update_one({"tg_id": self.tg_id}, {"$set": {"left_free_voice": value}})

    async def get_all_tgid(self):
        return [doc["tg_id"] async for doc in users_collection.find({}, {"tg_id": 1, "_id": 0})]
    
    async def get_all_conv(swlf):
        return statistik_collection.find({"conv": 1})