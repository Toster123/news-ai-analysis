from .config import config
from .constants import *
from ..llm.service import LLM

class Assistant:
    def __init__(self, llm: LLM = LLM()):
        self.llm = llm

    def create_chat_completion(self, messages: list[Dict]) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        i=0
        while i < config.MAX_QUERIES and "<questions>" in (messages := self.llm.create_chat_completion(messages))[-1].content:
            # todo: rag search
            i+=1
            pass

        return messages[-1].content.replace("<think>", "").split("</think>")[-1]