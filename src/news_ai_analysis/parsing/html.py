import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from .base import BaseParser
from src.news_ai_analysis.models import Source

class HTMLParser(BaseParser):
    async def parse(self, source: Source) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            async with session.get(source.url) as resp:
                html = await resp.text()
        soup = BeautifulSoup(html, 'html.parser')
        items = []
        # Пример: ищем все article с заголовками
        for article in soup.find_all('article'):
            title_tag = article.find('h2')
            link_tag = article.find('a')
            if not title_tag or not link_tag:
                continue
            url = link_tag.get('href')
            if not url.startswith('http'):
                url = source.url.rstrip('/') + '/' + url.lstrip('/')
            items.append({
                "title": title_tag.text.strip(),
                "content": article.get_text(strip=True)[:500],
                "url": url,
                "published_at": None,
                "source_id": source.id
            })
        return items