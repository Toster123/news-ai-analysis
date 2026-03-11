from .config import config
from .constants import *
from ..llm.utils import *
from ..llm.service import LLM


class Assistant:
    def __init__(self, llm: LLM, system_prompt: None | str = SYSTEM_PROMPT):
        self.llm = llm
        self.__system_prompt = system_prompt

    def create_chat_completion(self, messages: list[Dict]) -> str:
        if self.__system_prompt:
            messages = [
                {"role": "system", "content": self.__system_prompt}] + messages

        i = 0
        while i < config.MAX_QUERIES and "<questions>" in (latest_message := extract_content((messages := self.llm.create_chat_completion(messages))[-1])):
            queries = latest_message.split(
                "<questions>\n")[-1].split("\n</questions>")[0].split("\n")

            k = [int(q.split("; k=")[-1]) if "; k=" in q else config.MAX_K for q in queries]
            queries = [q.split("; k=")[0] for q in queries]

            # TODO: rag search and format
            found_news_formatted = ""
            messages.append({"role": "user", "content": found_news_formatted})

            i += 1
            pass

        return extract_content(messages[-1])
