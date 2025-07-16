from ..mitacore.memory import Memory
from ..database.requests import DatabaseManager

class UserConfigService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = DatabaseManager(self.user_id)
        
    async def blocker(self, blocked: bool) -> None:
        await self.db.set_blocked_user(blocked)
        
    async def set_stats(
        self,
        user_chars: int,
        mita_chars: int,
        all_chars: int,
        time_response: int,
        user_time: int
    ) -> None:
        await self.db.set_user_chars(user_chars)
        await self.db.set_mita_chars(mita_chars)
        await self.db.set_all_chars(all_chars)

        await self.db.set_time_response(time_response)
        await self.db.set_user_time(user_time)
        
    async def setprompt(self, prompt: str) -> None:
        await self.db.set_system_prompt(prompt)
        
    async def reset_history(self):
        Memory(self.user_id).reset_memory()