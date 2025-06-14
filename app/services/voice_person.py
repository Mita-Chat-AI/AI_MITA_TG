import os
import json
import aiofiles
from pathlib import Path
from types import SimpleNamespace

class VoicePerson:
    def __init__(self, person, file_config) -> None:
        self.person = person
        self.file_config = file_config 

    async def get_params(self) -> SimpleNamespace:
        async with aiofiles.open(Path(__file__).resolve().parent.parent.parent / self.file_config , mode='r', encoding='utf-8') as f:
            persons = json.loads(await f.read())

        if persons.get(self.person) is None:
            raise ValueError(f"Нет данных для {self.person}")
        return SimpleNamespace(**persons[self.person]["params"])
    
