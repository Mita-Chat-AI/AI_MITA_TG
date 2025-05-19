import os
import json
import aiofiles
from types import SimpleNamespace


class VoicePerson:
    def __init__(self, person) -> None:
        self.person = person

    async def get_params(self) -> SimpleNamespace:
        async with aiofiles.open(f"{os.getcwd()}/AIO-MITA/persons.json", mode='r', encoding='utf-8') as f:
            persons = json.loads(await f.read())

        if persons.get(self.person) is None:
            raise ValueError(f"Нет данных для {self.person}")
        return SimpleNamespace(**persons[self.person]["params"])