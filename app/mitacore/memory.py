import os
import json
from typing import List, Dict
from pathlib import Path

from loguru import logger

from ...config_reader import config



class Memory:
    def __init__(
        self,
        user_id: int,
        ) -> None:
        self.user_id = user_id
        self.memory_dir = Path(__file__).resolve().parent.parent.parent / "memories"
        self.memory = self.load_memory(user_id)

        if self.memory is None:
            self.memory = []

    def load_memory(self, user_id: int) -> List[Dict[str, str]] | None:
        """
        Загружает историю чата из JSON файла."""
        try:   
            file_path = os.path.join(self.memory_dir, f"{user_id}.json")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding='utf-8') as f:
                        return json.load(f)
        except:
            logger.error(f"Error decoding JSON for user {user_id}. Creating a new memory.")
            return None
    def save_memory(self, memory: List[Dict[str, str]], user_id: int) -> None:
        """
        Сохраняет историю чата в JSON файл.
        """
        try:
            file_path = os.path.join(self.memory_dir, f"{user_id}.json")
            os.makedirs(self.memory_dir, exist_ok=True)  # <-- Создаёт директорию, если её нет
            with open(file_path, "w", encoding='utf-8') as f:
                json.dump(memory, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"{e}")


    def reset_memory(self) -> None:
        """
        Стирает память
            Args:
                user_id: int -> айди пользователя.
            Return: 
                True -> если успешно очистили историю чата.
                False -> Если не удалось очистить историю чата. 
        """
        try:
            self.save_memory([], self.user_id)
            return True
        except Exception as e:
            logger.error(e)
            raise ValueError("Не удалось стереть память.")
        
