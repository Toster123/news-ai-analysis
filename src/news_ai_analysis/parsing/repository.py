# news_ai_analysis/parsing/repository.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlparse
from datetime import datetime, timezone
from .models import Article


def normalize_url(url: str) -> str:
    """Удаляет UTM-метки и прочий мусор из URL."""
    parsed = urlparse(url)
    # Убираем query параметры для лучшего сравнения
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


async def is_url_exists(session: AsyncSession, url: str) -> bool:
    """Проверяет, есть ли такой URL в базе данных."""
    normalized_url = normalize_url(url)
    query = select(Article).where(Article.url == normalized_url)
    result = await session.execute(query)
    return result.scalar_one_or_none() is not None


async def save_article(session: AsyncSession, article_data: dict):
    """Сохраняет новую статью."""
    from .models import Article
    
    # Нормализуем URL
    article_data['url'] = normalize_url(article_data['url'])
    
    # Конвертируем все даты в UTC без таймзоны для PostgreSQL
    if 'published_at' in article_data:
        if isinstance(article_data['published_at'], str):
            # Из строки в datetime
            dt = datetime.fromisoformat(article_data['published_at'].replace('Z', '+00:00'))
        else:
            dt = article_data['published_at']
        
        # Если есть таймзона - конвертируем в UTC и убираем таймзону
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        article_data['published_at'] = dt
    
    # Для created_at всегда создаем без таймзоны
    if 'created_at' not in article_data:
        article_data['created_at'] = datetime.now()  # Без таймзоны
    else:
        if isinstance(article_data['created_at'], str):
            dt = datetime.fromisoformat(article_data['created_at'].replace('Z', '+00:00'))
        else:
            dt = article_data['created_at']
        
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        article_data['created_at'] = dt
    
    new_article = Article(**article_data)
    session.add(new_article)
    await session.flush()


async def get_article_by_url(session: AsyncSession, url: str) -> Article | None:
    """Получает статью по URL"""
    normalized_url = normalize_url(url)
    query = select(Article).where(Article.url == normalized_url)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def update_article_summary(session: AsyncSession, url: str, summary: str):
    """Обновляет summary статьи"""
    article = await get_article_by_url(session, url)
    if article:
        article.summary = summary
        await session.flush()
