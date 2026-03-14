from typing import Dict, List, Optional
from .config import config
from src.news_ai_analysis.config import config as global_config
from .utils import *
from llama_cpp import Llama


class LLM():
    def __init__(self):
        self.llm = Llama.from_pretrained(
            repo_id=config.MODEL_REPO,
            filename=config.MODEL,
            n_gpu_layers=-1,
            verbose=True,
            n_ctx=config.CONTEXT_SIZE  # Добавим контекст из конфига
        ) if not global_config.DISABLE_LOCAL_MODELS else None

    def create_chat_completion(self, messages: List[Dict]) -> List[Dict]:
        """
        Отправка запроса к локальной LLM модели
        """
        if self.llm is None:
            # Возвращаем заглушку если локальные модели отключены
            messages.append({"role": "assistant", "content": "Локальные модели отключены в конфигурации"})
            return messages
            
        try:
            response = self.llm.create_chat_completion(messages=messages)
            messages.append({
                "role": "assistant", 
                "content": response['choices'][0]['message']['content']
            })
        except Exception as e:
            print(f"Ошибка при вызове LLM: {e}")
            messages.append({
                "role": "assistant", 
                "content": f"Произошла ошибка при генерации ответа: {str(e)}"
            })
            
        return messages

    def __call__(self, query: str, system_prompt: Optional[str] = None, remove_think_tags: bool = True) -> str:
        messages = [{"role": "user", "content": query}]
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
            
        result_messages = self.create_chat_completion(messages)
        return extract_content(result_messages[-1], remove_think_tags)
    
    def is_available(self) -> bool:
        """Проверка доступности модели"""
        return self.llm is not None