from .config import config
from .constants import *
from ..llm.utils import *
from ..llm.service import LLM
from ..rag.service import Vectorstore


class Assistant:
    def __init__(self, llm: LLM, vectorstore: Vectorstore, system_prompt: None | str = SYSTEM_PROMPT):
        self.llm = llm
        self.__system_prompt = system_prompt
        self.__vectorstore = vectorstore

    def create_chat_completion(self, messages: list[Dict]) -> str:
        if self.__system_prompt:
            messages = [
                {"role": "system", "content": self.__system_prompt}] + messages

        i = 0
        while i < config.MAX_QUERIES and "<questions>" in (latest_message := extract_content((messages := self.llm.create_chat_completion(messages))[-1])):
            queries = latest_message.split(
                "<questions>\n")[-1].split("\n</questions>")[0].split("\n")

            queries = [{"query": q.split("; k=")[0], "k": min(int(q.split("; k=")[-1]), config.MAX_K) if "; k=" in q else config.MAX_K} for q in queries]

            found_news = distinct_documents(self.__vectorstore.search(queries))
            found_news_formatted = "\n\n".join([
                f"{article.page_content}\n{article.metadata}" for article in found_news
            ])

            messages.append({"role": "user", "content": found_news_formatted})

            i += 1
            pass

        return extract_content(messages[-1])
