from typing import Dict
from .config import config
from llama_cpp import Llama

class LLM():
    def __init__(self):
        self.llm = Llama.from_pretrained(
            repo_id=config.MODEL_REPO,
            filename=config.MODEL,
            n_gpu_layers=-1,            
            verbose=False
        )

    def create_chat_completion(self, messages: list[Dict]) -> list[Dict]:
        messages.append({"role": "assistant", "content": self.llm.create_chat_completion(messages=messages)['choices'][0]['message']['content']})
        return messages

    def __call__(self, query: str, system_prompt = None) -> str:
        messages = [{"role": "user", "content": query}]
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        return self.create_chat_completion(messages)[-1].content
