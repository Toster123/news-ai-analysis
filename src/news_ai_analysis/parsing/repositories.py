
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Source, News

class SourceRepository:
    @staticmethod
    async def get_all_active(session: AsyncSession):
        result = await session.execute(select(Source))
        return result.scalars().all()

class NewsRepository:
    @staticmethod
    async def exists_by_url(session: AsyncSession, url: str) -> bool:
        result = await session.execute(select(News).where(News.url == url))
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def add(session: AsyncSession, **news_data):
        news = News(**news_data)
        session.add(news)
        return news