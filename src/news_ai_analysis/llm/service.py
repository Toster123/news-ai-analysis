from typing import Dict
from .config import config
from news_ai_analysis.config import config as global_config
from .utils import *
# from llama_cpp import Llama
from groq import Groq


class LLM():
    def __init__(self):
        self.llm = Llama.from_pretrained(
            repo_id=config.MODEL_REPO,
            filename=config.MODEL,
            n_gpu_layers=-1,
            verbose=False
        ) if not global_config.DISABLE_LOCAL_MODELS else Groq(api_key="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")

    def create_chat_completion(self, messages: list[Dict]) -> list[Dict]:
        messages.append({"role": "assistant", "content": self.llm.create_chat_completion(
            messages=messages)['choices'][0]['message']['content'] if not global_config.DISABLE_LOCAL_MODELS else self.llm.chat.completions.create(
            model="moonshotai/kimi-k2-instruct",
            messages=messages,
            max_completion_tokens=8192,
            top_p=1,
        ).choices[0].message.content})
        return messages

    def __call__(self, query: str, system_prompt: None | str = None, remove_think_tags: bool = True) -> str:
        messages = [{"role": "user", "content": query}]
        if system_prompt:
            messages = [
                {"role": "system", "content": system_prompt}] + messages
        return extract_content(self.create_chat_completion(messages)[-1], remove_think_tags)
