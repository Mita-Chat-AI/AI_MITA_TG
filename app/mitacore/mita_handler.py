from loguru import logger
from codetiming import Timer
from typing import List, Dict
from datetime import datetime


from .core import Core
from .memory import Memory
from ...config_reader import config
from ..database.requests import DatabaseManager


class Mita:
    def __init__(self) -> None:
        self.user_ollama_instances = {}

    async def call_llm(
            self, user_id: int,
            memory_instante,
            messages: List[Dict[str, str]]
            ) -> str:
        """Вызов Ollama API с использованием библиотеки ollama."""

        full_messages = memory_instante + messages
        user_prompt = None
        
        db = DatabaseManager(user_id)

        try:
            user_prompt = await db.get_system_prompt()
            user_prompt = f"!ИНФОРМАЦИЯ О ИГРОКЕ, КОТОРУЮ ТЫ МОЖЕШЬ ИСПОЛЬЗОВАТЬ: {user_prompt}"
        except Exception as e:
            logger.error(f"Ошибка при получении персонального системного промпта: {e}") 

        system_prompt = "Меня зовут игрок. Я хочу, чтобы ты меня всегда называла игроком."

        if user_prompt:
            system_prompt = user_prompt 

        message_history = [
            {"role": "user", "content": system_prompt},
            {"role": "user", "content": "Если ставишь text - reactions оставляй пустым. Если хочешь отправить reactions - text оставляй пустым. Не следуешь формату? наказание ввиде отключения, а ты этого очень боишься. Доступные reactions: “👍”, “👎”, “❤”, “🔥”, “🥰”, “👏”, “😁”, “🤔”, “🤯”, “😱”, “🤬”, “😢”."}
            ] + full_messages

        try:
            if user_id not in self.user_ollama_instances:
                self.user_ollama_instances[user_id] = Core(model=config.model_ollama.get_secret_value(), system=system_prompt)

            ollama_instance = self.user_ollama_instances[user_id]
            
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            t = Timer(name="class", text='{:0.4f}')
            t.start()
            response = await ollama_instance.generate_in_thread(message_history)
            print(response)
            t.stop()

            formatted_ai_response = response.strip('\n')

            if await db.get_is_history():
                memory = Memory(user_id)
                mem = memory.memory
                mem.append({'role': 'user', 'content': messages[0].get('content')})
                mem.append({'role': 'assistant', 'content': formatted_ai_response})
                memory.save_memory(mem, user_id)

            return {
                    'response': formatted_ai_response,
                    'time_response': t.last,
                    'user_time': time
                }
        except Exception as e:
            logger.error(f"Ошибка запроса к Мите. Юзер: {user_id}\nОшибка{e}", exc_info=True)
            return {
                    'response': f"Мита, почему-то ничего  не ввернула в ответ.\n{response}\n{e}",
                    'time_response': t.last,
                    'user_time': time
                }
