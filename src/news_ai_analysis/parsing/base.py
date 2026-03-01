from abc import ABC, abstractmethod
from typing import List, Dict
from src.news_ai_analysis.models import Source

class BaseParser(ABC):
    @abstractmethod
    async def parse(self, source: Source) -> List[Dict]:
        """Возвращает список словарей с ключами: title, content, url, published_at, source_id"""
        pass