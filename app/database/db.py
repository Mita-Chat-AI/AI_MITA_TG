from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


engine = create_async_engine(url='sqlite+aiosqlite:////home/miku/AIO-MITA/db.sqlite3')
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    conditions: Mapped[bool] = mapped_column(default=False)
    tg_id = mapped_column(BigInteger)
        
    system_prompt: Mapped[str] = mapped_column(nullable=True, default=None)
    is_blocked: Mapped[bool] = mapped_column(default=False)
    person_voice: Mapped[str] = mapped_column(default="CrazyMita")
    is_history: Mapped[bool] = mapped_column(default=True)
    voice_mode: Mapped[bool] = mapped_column(default=False)
    lang: Mapped[str] = mapped_column(default="ru", server_default="ru")


class Statistik(Base):
    __tablename__  = 'statistiks'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    all_chars: Mapped[int] = mapped_column(default=0)
    user_chars: Mapped[int] = mapped_column(default=0)
    mita_chars: Mapped[int] = mapped_column(default=0)
    user_time: Mapped[str] = mapped_column(default='[]')
    time_response: Mapped[str] = mapped_column(default='[]')
    

async def async_main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
