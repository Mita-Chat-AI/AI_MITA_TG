# NOTE: Код ChatGPT, который нужно переписать

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

from ...config_reader import config

# Класс для удобной работы с ObjectId в Pydanticfrom bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    tg_id: int
    conditions: bool = False
    system_prompt: Optional[str] = None
    is_blocked: bool = False
    person_voice: str = "CrazyMita"
    is_history: bool = True
    voice_mode: bool = False
    lang: str = "null"

    class Config:
        populate_by_name = True

        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True


class StatistikModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    tg_id: int = Field(..., description="Ссылка на User.tg_id")  # логическая ссылка
    all_chars: int = 0
    user_chars: int = 0
    mita_chars: int = 0
    user_time: List[str] = []
    time_response: List[str] = []

    class Config:
        populate_by_name = True

        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True

# Подключение к базе
client = AsyncIOMotorClient(config.mongo_db.get_secret_value())
db = client['mitaAI']

# Коллекции
users_collection = db['users']
statistik_collection = db['statistiks']

async def async_main():
    pass