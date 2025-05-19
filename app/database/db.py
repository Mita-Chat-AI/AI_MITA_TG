# from sqlalchemy import BigInteger, ForeignKey, String
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


# engine = create_async_engine(url='sqlite+aiosqlite:////home/miku/AIO-MITA/db.sqlite3')


# async_session = async_sessionmaker(engine)


# class Base(AsyncAttrs, DeclarativeBase):
#     pass


# class User(Base):
#     __tablename__ = 'users'
    
#     id: Mapped[int] = mapped_column(primary_key=True)
#     conditions: Mapped[bool] = mapped_column(default=False)
#     tg_id = mapped_column(BigInteger)
        
#     system_prompt: Mapped[str] = mapped_column(nullable=True, default=None)
#     is_blocked: Mapped[bool] = mapped_column(default=False)
#     person_voice: Mapped[str] = mapped_column(default="CrazyMita")
#     is_history: Mapped[bool] = mapped_column(default=True)
#     voice_mode: Mapped[bool] = mapped_column(default=False)
#     lang: Mapped[str] = mapped_column(default="ru", server_default="ru")


# class Statistik(Base):
#     __tablename__  = 'statistiks'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     tg_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
#     all_chars: Mapped[int] = mapped_column(default=0)
#     user_chars: Mapped[int] = mapped_column(default=0)
#     mita_chars: Mapped[int] = mapped_column(default=0)
#     user_time: Mapped[str] = mapped_column(default='[]')
#     time_response: Mapped[str] = mapped_column(default='[]')
    

# async def async_main() -> None:
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

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
    lang: str = "ru"

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
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client['mitaAI']

# Коллекции
users_collection = db['users']
statistik_collection = db['statistiks']

async def async_main():
    pass