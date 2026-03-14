"""
Сервис для интеграции парсинга с Streamlit интерфейсом
"""
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import streamlit as st
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from news_ai_analysis.parsing.fetcher import fetch_all_rss
from news_ai_analysis.parsing.scraper import scrape_full_text
from news_ai_analysis.parsing.repository import save_article, is_url_exists
from news_ai_analysis.parsing.schemas import RSSArticle
from news_ai_analysis.models import Base
from news_ai_analysis.parsing.models import Article
from news_ai_analysis.parsing.rss_config import RSS_SOURCES as DEFAULT_SOURCES


class ParsingService:
    """Сервис для управления парсингом новостей"""
    
    def __init__(self, db_url: str = None):
        """
        Инициализация сервиса с подключением к PostgreSQL
        
        Args:
            db_url: Строка подключения к БД. Если None, использует стандартные параметры
        """
        if db_url is None:
            # Стандартное подключение к PostgreSQL в Docker
            # Формат: postgresql+asyncpg://user:password@host:port/dbname
            db_url = "postgresql+asyncpg://postgres:password@localhost:5433/postgres"
        
        self.db_url = db_url
        self.engine = create_async_engine(
            db_url,
            echo=True,  # Логировать SQL запросы (можно отключить в продакшене)
            pool_size=5,  # Размер пула соединений
            max_overflow=10  # Максимальное количество дополнительных соединений
        )
        self.async_session = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        self._running = False
        self._thread = None
        
    async def init_db(self):
        """Создание таблиц в БД (если их нет)"""
        async with self.engine.begin() as conn:
            # Для PostgreSQL нужно создать расширение для UUID если используете
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            # Создаем таблицы
            print("Мы зашли в INIT_DB")
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы/проверены в PostgreSQL")
    
    async def check_connection(self) -> bool:
        """Проверка подключения к БД"""
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к PostgreSQL: {e}")
            return False
    
    async def collect_articles(self, sources: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Сбор статей из источников с сохранением в PostgreSQL
        
        Args:
            sources: Список источников из st.session_state.sources
        """
        print("🚀 Начинаем сбор статей...")
        
        # Проверяем подключение к БД
        if not await self.check_connection():
            print("❌ Нет подключения к БД")
            return []
        else:
            print("ЗАЛУПА ЗАШЛА")
            await self.init_db()
        
        # Определяем источники для парсинга
        if sources:
            # Фильтруем только активные RSS источники
            rss_sources = [
                {"name": s["name"], "url": s["config"]["url"]}
                for s in sources 
                if s["active"] and s["type"] == "rss"
            ]
        else:
            # Используем дефолтные источники
            rss_sources = DEFAULT_SOURCES
        
        if not rss_sources:
            print("⚠️ Нет активных RSS источников")
            return []
        
        # Временно подменяем конфиг для fetcher
        from news_ai_analysis.parsing import rss_config
        original_sources = rss_config.RSS_SOURCES
        rss_config.RSS_SOURCES = rss_sources
        
        try:
            # Собираем статьи
            articles = await fetch_all_rss()
            
            # Сохраняем в PostgreSQL и собираем результаты для UI
            saved_articles = []
            async with self.async_session() as session:
                async with session.begin():  # Начинаем транзакцию
                    for article in articles:
                        # Проверяем на дубликаты
                        if not await is_url_exists(session, article.url):
                            # Сохраняем в БД
                            article_data = article.model_dump()  # для Pydantic v2
                            # Или article.dict() для Pydantic v1
                            
                            # Добавляем временную метку создания
                            article_data['created_at'] = datetime.now()
                            
                            await save_article(session, article_data)
                            
                            # Добавляем в результат для UI
                            saved_articles.append({
                                "id": None,  # ID будет после commit
                                "source_name": article.source_name,
                                "title": article.title,
                                "url": article.url,
                                "published_at": article.published_at.isoformat(),
                                "summary": None,  # Пока без summary
                                "created_at": datetime.now().isoformat()
                            })
                            print(f"✅ Сохранена новая статья: {article.title[:50]}...")
                        else:
                            print(f"⏩ Статья уже существует: {article.title[:50]}...")
                    
                    # Транзакция автоматически закоммитится при выходе из context manager
                    
            print(f"🎉 Собрано {len(saved_articles)} новых статей")
            return saved_articles
            
        except Exception as e:
            print(f"❌ Ошибка при сборе статей: {e}")
            return []
        finally:
            # Восстанавливаем оригинальный конфиг
            rss_config.RSS_SOURCES = original_sources
    
    async def scrape_article_content(self, url: str) -> Optional[str]:
        """Скрапинг полного текста статьи"""
        return await scrape_full_text(url)
    
    async def get_articles_from_db(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Получение статей напрямую из БД"""
        from sqlalchemy import select
        
        async with self.async_session() as session:
            query = select(Article).order_by(Article.published_at.desc()).limit(limit).offset(offset)
            result = await session.execute(query)
            articles = result.scalars().all()
            
            return [
                {
                    "id": a.id,
                    "source_name": a.source_name,
                    "title": a.title,
                    "url": a.url,
                    "summary": a.summary,
                    "published_at": a.published_at.isoformat(),
                    "created_at": a.created_at.isoformat()
                }
                for a in articles
            ]
    
    def start_background_collection(self, interval_minutes: int = 15):
        """Запуск фонового сбора новостей"""
        if self._running:
            print("⚠️ Сбор уже запущен")
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._background_worker,
            args=(interval_minutes,),
            daemon=True
        )
        self._thread.start()
        print("✅ Фоновый сбор запущен")
    
    def stop_background_collection(self):
        """Остановка фонового сбора"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("🛑 Фоновый сбор остановлен")
    
    def _background_worker(self, interval_minutes: int):
        """Фоновый воркер для периодического сбора"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self._running:
            try:
                # Собираем статьи из активных источников
                sources = st.session_state.get('sources', [])
                articles = loop.run_until_complete(
                    self.collect_articles(sources)
                )
                
                # Обновляем метрики в session_state
                if 'collector_status' in st.session_state:
                    st.session_state.collector_status['articles_collected'] += len(articles)
                    st.session_state.collector_status['last_update'] = datetime.now().isoformat()
                
                # Сохраняем статьи в session_state для отображения
                if 'articles' not in st.session_state:
                    st.session_state.articles = []
                
                # Добавляем только новые статьи (по URL)
                existing_urls = {a['url'] for a in st.session_state.articles}
                new_articles = [a for a in articles if a['url'] not in existing_urls]
                st.session_state.articles.extend(new_articles)
                
                print(f"📊 Добавлено {len(new_articles)} новых статей в ленту")
                print(f"📊 Всего статей в памяти: {len(st.session_state.articles)}")
                
            except Exception as e:
                print(f"❌ Ошибка в фоновом сборе: {e}")
                import traceback
                traceback.print_exc()
            
            # Ждем до следующего сбора
            for _ in range(interval_minutes * 60):
                if not self._running:
                    break
                time.sleep(1)
        
        loop.close()
