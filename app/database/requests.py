import json
from loguru import logger
from sqlalchemy import select, update

from .db import User, Statistik
from .db import async_session


class DatabaseManager:
    def __init__(self, tg_id):
        self.tg_id = tg_id
    
    async def set_user(self) -> None:
        async with async_session() as session:
            user = await session.scalar(
                select(User.tg_id).where(
                    User.tg_id == self.tg_id
                )
            )
            logger.info('Database Function select set_user')

            if not user:
                session.add(
                    User(tg_id=self.tg_id
                         )
                )
                logger.info('Database Function add User to set_user')
                session.add(
                    Statistik(
                        tg_id=self.tg_id
                    )
                )
                logger.info('Database Function add Statistik to set_user')
                await session.commit()

    async def get_is_blocked_user(self) -> bool:
        async with async_session() as session:
            is_blocked = await session.scalar(
                select(User.is_blocked).where(
                    User.tg_id == self.tg_id
                )
            )
            logger.info('Database Function select get_is_blocked_user')
            return is_blocked

    async def set_blocked_user(self, blocked: bool) -> bool:
        async with async_session() as session:
            await session.execute(
                update(User).where(
                    User.tg_id == self.tg_id
                ).values(
                    is_blocked=blocked
                )
            )
            logger.info('Database Function update set_blocked_user')
            await session.commit()

            is_blocked = await self.get_is_blocked_user()
            return is_blocked

    async def set_user_chars(self, user_chars: int) -> None:
        async with async_session() as session:
            await session.execute(
                update(Statistik).where(
                    Statistik.tg_id == self.tg_id
                ).values(
                    user_chars=user_chars
                )
            )
            await session.commit()

    async def set_mita_chars(self, mita_chars: int) -> None:
        async with async_session() as session:
            await session.execute(
                update(Statistik).where(
                    Statistik.tg_id == self.tg_id
                ).values(
                    mita_chars=mita_chars
                )
            )
            await session.commit()

    async def set_all_chars(self, all_chars: int) -> None:
        async with async_session() as session:
            await session.execute(
                update(Statistik).where(
                    Statistik.tg_id == self.tg_id
                ).values(
                    all_chars=all_chars
                )
            )
            await session.commit()

    async def get_statistik(self):
        async with async_session() as sesson:
            result = await sesson.scalar(
                select(Statistik).where(
                    Statistik.tg_id == self.tg_id
                )
            )

            logger.info("Database Function select get_statistik")
            return result

    async def set_time_response(self, new_time: str) -> None:
        async with async_session() as session:
            statistik_entry = await session.scalar(
                select(Statistik).where(
                    Statistik.tg_id == self.tg_id
                )
            )

            if statistik_entry:
                time = json.loads(statistik_entry.time_response)
                time.append(new_time)

                statistik_entry.time_response = json.dumps(time)
                await session.commit()
                logger.info("Database Function update set_time_response")
            else:
                logger.warning(f"set_time_response stats not found {self.tg_id}")

    async def set_user_time(self, new_time: str) -> None:
        async with async_session() as session:
            statistik_entry = await session.scalar(
                select(Statistik).where(
                    Statistik.tg_id == self.tg_id
                )
            )

            if statistik_entry:
                time = json.loads(statistik_entry.user_time)
                time.append(new_time)

                statistik_entry.user_time = json.dumps(time)
                await session.commit()
                logger.info("Database Function update set_user_time")
            else:
                logger.warning(f"set_user_time stats not found {self.tg_id}")

    async def set_system_prompt(self, system_prompt: str) -> None:
        async with async_session() as session:
            await session.execute(
                update(User).where(
                    User.tg_id == self.tg_id
                ).values(
                    system_prompt=system_prompt
                )
            )
            await session.commit()
    
    async def get_system_prompt(self):
        async with async_session() as session:
            result = await session.scalar(
                select(
                    User.system_prompt
                ).where(
                    User.tg_id == self.tg_id
                )
            )
            return result
        
    async def get_statistik(self):
        async with async_session() as session:
            result = await session.scalar(
                select(
                    Statistik
                ).where(
                    Statistik.tg_id == self.tg_id
                )
            ) 
            return result
    
    async def set_voice_person(self, person_voice: str):
        async with async_session() as session:
            await session.execute(
                update(User).where(
                    User.tg_id == self.tg_id
                ).values(
                    person_voice=person_voice
                )
            )
            await session.commit()
            
    async def get_voice_person(self):
        async with async_session() as session:
            response = await session.scalar(
                select(
                    User.person_voice
                ).where(
                    User.tg_id == self.tg_id
                )
            )
            return response

    async def set_is_history(self, is_history: bool):
        async with async_session() as session:
            await session.execute(
                update(User).where(
                    User.tg_id == self.tg_id
                ).values(
                    is_history=is_history
                )
            )
            await session.commit()
            
    async def get_is_history(self):
        async with async_session() as session:
            response = await session.scalar(
                select(
                    User.is_history
                ).where(
                    User.tg_id == self.tg_id
                )
            )
            return response
    
    async def set_voice_mode(self, voice_mode: bool):
        async with async_session() as session:
            await session.execute(
                update(User).where(
                    User.tg_id == self.tg_id
                ).values(
                    voice_mode=voice_mode
                )
            )
            await session.commit()
            
    async def get_voice_mode(self):
        async with async_session() as session:
            response = await session.scalar(
                select(
                    User.voice_mode
                ).where(
                    User.tg_id == self.tg_id
                )
            )
            return response

    async def get_conditions(self):
        async with async_session() as session:
            response = await session.scalar(
                select(
                    User.conditions
                ).where(
                    User.tg_id == self.tg_id
                )
            )
            return response
        
    async def set_conditions(self, conditions: bool):
        async with async_session() as session:
            await session.execute(
                update(User).where(
                    User.tg_id == self.tg_id
                ).values(
                    conditions=conditions
                )
            )
            await session.commit()
            

    async def get_lang(self):
        async with async_session() as session:
            response = await session.scalar(
                select(
                    User.lang
                ).where(
                    User.tg_id == self.tg_id
                )
            )
            return response
        
    async def set_lang(self, lang: bool):
        async with async_session() as session:
            await session.execute(
                update(User).where(
                    User.tg_id == self.tg_id
                ).values(
                    lang=lang
                )
            )
            await session.commit()