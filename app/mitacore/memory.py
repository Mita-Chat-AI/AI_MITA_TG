import os
import json
from typing import List, Dict
from pathlib import Path
from loguru import logger


class Memory:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.memory_dir = Path(__file__).resolve().parent.parent.parent / "memories"
        self.memory = self.load_memory()

        if self.memory is None:
            self.memory = []

    def load_memory(self) -> List[Dict[str, str]] | None:
        """
        Загружает историю чата из JSON файла.
        """
        file_path = self.memory_dir / f"{self.user_id}.json"
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки памяти пользователя {self.user_id}: {e}")

        return None

    def save_memory(self) -> None:
        """
        Сохраняет историю чата в JSON файл.
        """
        try:
            os.makedirs(self.memory_dir, exist_ok=True)
            file_path = self.memory_dir / f"{self.user_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения памяти: {e}")

    def reset_memory(self) -> bool:
        """
        Стирает всю память пользователя.
        """
        try:
            self.memory = []
            self.save_memory()
            return True
        except Exception as e:
            logger.error(f"Ошибка очистки памяти: {e}")
            return False

    def floating_window(self) -> None:
        """
        Плавающее контекстное окно:
        Если сообщений больше 3, удаляет четвёртое сообщение (первое после проптов).
        """

        removed_message = self.memory.pop(3)
        logger.info(f"Удалено сообщение из памяти: {removed_message}")
        self.save_memory()
