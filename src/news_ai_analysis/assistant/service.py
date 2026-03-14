from typing import Dict, List, Optional
from .config import config
from .constants import SYSTEM_PROMPT
from ..llm.utils import extract_content
from ..llm.service import LLM
from ..rag.service import Vectorstore
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Assistant:
    def __init__(self, llm: LLM, vectorstore: Vectorstore, system_prompt: Optional[str] = SYSTEM_PROMPT):
        self.llm = llm
        self.__system_prompt = system_prompt
        self.__vectorstore = vectorstore
        
        # Проверяем доступность LLM
        if not self.llm.is_available():
            logger.warning("LLM модель не доступна (DISABLE_LOCAL_MODELS=True)")

    def create_chat_completion(self, messages: List[Dict]) -> str:
        # Добавляем системный промпт если его нет и он задан
        if self.__system_prompt:
            # Проверяем, есть ли уже системное сообщение
            has_system = any(msg.get("role") == "system" for msg in messages)
            if not has_system:
                messages = [{"role": "system", "content": self.__system_prompt}] + messages

        # Проверяем доступность LLM
        if not self.llm.is_available():
            return "Режим ассистента отключен (DISABLE_LOCAL_MODELS=True)"

        i = 0
        while i < config.MAX_QUERIES:
            try:
                # Получаем ответ от LLM
                messages = self.llm.create_chat_completion(messages)
                
                # Извлекаем последнее сообщение
                latest_message = messages[-1]["content"]
                
                # Проверяем наличие тегов <questions>
                if "<questions>" not in latest_message:
                    break
                    
                # Извлекаем запросы
                try:
                    # Разбираем запросы из ответа
                    queries = self._parse_queries(latest_message)
                    
                    # Выполняем поиск в векторном хранилище
                    found_news = self._search_news(queries)
                    
                    # Форматируем найденные новости
                    found_news_formatted = self._format_news_for_context(found_news)
                    
                    # Добавляем найденные новости в контекст
                    messages.append({
                        "role": "user", 
                        "content": f"На основе этих новостей ответь на вопрос:\n{found_news_formatted}"
                    })
                    
                except Exception as e:
                    logger.error(f"Ошибка при обработке запросов: {e}")
                    break
                
                i += 1
                
            except Exception as e:
                logger.error(f"Ошибка при вызове LLM: {e}")
                return f"Произошла ошибка: {str(e)}"

        # Возвращаем последнее сообщение ассистента
        return messages[-1]["content"]
    
    def _parse_queries(self, message: str) -> List[Dict]:
        """
        Парсинг запросов из сообщения с тегами <questions>
        """
        try:
            # Извлекаем содержимое между тегами
            if "<questions>" in message and "</questions>" in message:
                queries_text = message.split("<questions>\n")[-1].split("\n</questions>")[0]
                queries_lines = [q.strip() for q in queries_text.split("\n") if q.strip()]
                
                parsed_queries = []
                for q in queries_lines:
                    query_data = {"query": q, "k": config.MAX_K}
                    
                    # Парсим параметр k если есть
                    if "; k=" in q:
                        parts = q.split("; k=")
                        query_data["query"] = parts[0]
                        try:
                            query_data["k"] = int(parts[1])
                        except ValueError:
                            pass
                    
                    parsed_queries.append(query_data)
                
                return parsed_queries
        except Exception as e:
            logger.error(f"Ошибка парсинга запросов: {e}")
        
        return []
    
    def _search_news(self, queries: List[Dict]) -> List[Dict]:
        """
        Поиск новостей в векторном хранилище
        """
        found_news = []
        
        for q in queries:
            if q["query"].strip():
                try:
                    # Создаем объект запроса
                    from types import SimpleNamespace
                    search_query = SimpleNamespace(
                        query=q["query"], 
                        k=q["k"], 
                        filter=None
                    )
                    
                    # Выполняем поиск
                    results = self.__vectorstore.search([search_query])
                    
                    # Добавляем результаты
                    for doc in results:
                        found_news.append({
                            'content': doc.page_content,
                            'metadata': doc.metadata
                        })
                        
                except Exception as e:
                    logger.error(f"Ошибка поиска для запроса '{q['query']}': {e}")
        
        return found_news
    
    def _format_news_for_context(self, news_list: List[Dict]) -> str:
        """
        Форматирование новостей для контекста
        """
        if not news_list:
            return "Релевантные новости не найдены."
        
        formatted = "Найденные новости:\n"
        for i, news in enumerate(news_list[:5], 1):  # Ограничиваем 5 новостями
            formatted += f"\n{i}. "
            formatted += f"Заголовок: {news['metadata'].get('title', 'Без заголовка')}\n"
            formatted += f"   Источник: {news['metadata'].get('source', 'Неизвестно')}\n"
            formatted += f"   Дата: {news['metadata'].get('date', 'Неизвестно')}\n"
            formatted += f"   Содержание: {news['content'][:300]}...\n"
        
        return formatted