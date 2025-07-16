
from typing import List, Dict

from loguru import logger
from openai import AsyncOpenAI
# from pydantic import BaseModel

from ...config_reader import config

# def extract_json(content: str) -> str:
#     if content.strip().startswith("```"):
#         content = "\n".join(content.strip().splitlines()[1:-1])
#     return content


# class ResponseOutput(BaseModel):
#   text: str
#   reactions: str


class Core:
    def __init__(
        self,
        model: str,
        system: str = None
        ) -> None:

        self.model = model
        self.system = system
        self.client = AsyncOpenAI(base_url=config.lm_api.get_secret_value(), api_key="lm-studio")


    async def generateWithMemory(self, messages: List[Dict[str, str]]) -> str:
        print(messages)
        '''
        Sends the message history to Ollama.

        Parameters
        ----------
        messages : List[Dict[str, str]]
            The message history (list of dictionaries with role and content).

        Returns
        -------
        str
            The assistant's response.
        '''

        logger.info("Отправляю запрос к LLM")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )

        assistant_reply = response.choices[0].message.content

        return assistant_reply