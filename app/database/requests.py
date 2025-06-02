from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from .db import UserModel, StatistikModel

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["TEST"]
users_collection = db["users"]
statistik_collection = db["statistiks"]

class DatabaseManager:
    def __init__(self, tg_id: int):
        self.tg_id = tg_id

    async def set_user(self) -> None:
        if not await users_collection.find_one({"tg_id": self.tg_id}):
            await users_collection.insert_one(UserModel(tg_id=self.tg_id).dict(by_alias=True))
            await statistik_collection.insert_one(StatistikModel(tg_id=self.tg_id).dict(by_alias=True))
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
