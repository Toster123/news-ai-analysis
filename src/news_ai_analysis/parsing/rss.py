import feedparser
import asyncio
from datetime import datetime
from typing import List, Dict
from .base import BaseParser
from src.news_ai_analysis.models import Source

class RSSParser(BaseParser):
    async def parse(self, source: Source) -> List[Dict]:
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, source.url)
        items = []
        for entry in feed.entries:
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            items.append({
                "title": entry.title,
                "content": entry.get("summary", ""),
                "url": entry.link,
                "published_at": published,
                "source_id": source.id
            })
        return items