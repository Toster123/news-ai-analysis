import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.news_ai_analysis.db.session import async_session
from src.news_ai_analysis.models.source import Source, SourceType
from src.news_ai_analysis.models.news import News
from src.news_ai_analysis.parsers.rss import RSSParser
from src.news_ai_analysis.parsers.html import HTMLParser

logger = logging.getLogger(__name__)

PARSERS = {
    SourceType.RSS: RSSParser(),
    SourceType.HTML: HTMLParser(),
}

async def collect_news():
    """Основная функция сбора новостей."""
    async with async_session() as session:
        # Получаем все источники
        result = await session.execute(select(Source))
        sources = result.scalars().all()

        for source in sources:
            parser = PARSERS.get(source.type)
            if not parser:
                logger.warning(f"No parser for source type {source.type} (id={source.id})")
                continue

            try:
                news_items = await parser.parse(source)
            except Exception as e:
                logger.error(f"Error parsing source {source.id} ({source.url}): {e}")
                continue

            # Сохраняем только новые новости (проверка по url)
            for item in news_items:
                exists = await session.execute(
                    select(News).where(News.url == item["url"])
                )
                if not exists.scalar_one_or_none():
                    news = News(**item)
                    session.add(news)
            await session.commit()
            logger.info(f"Saved {len(news_items)} news from source {source.id}")

    logger.info("News collection finished")