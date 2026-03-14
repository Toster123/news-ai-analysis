import asyncio
import feedparser
from time import mktime
from datetime import datetime, timezone
from pprint import pprint

from news_ai_analysis.parsing.schemas import RSSArticle
from news_ai_analysis.parsing.rss_config import RSS_SOURCES


async def fetch_single_feed(source: dict) -> list[RSSArticle]:
    """Скачивает и парсит одну RSS-ленту."""
    print(f"🔄 Запрашиваем: {source['name']}...")
    
    # Йоу, она синхронная - надо переделывать
    feed = await asyncio.to_thread(feedparser.parse, source["url"])
    
    articles = []
    for entry in feed.entries:
        # Пытаемся безопасно достать дату (в RSS она бывает в разных форматах)
        pub_date = datetime.now(timezone.utc)
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            # Преобразуем struct_time от feedparser в нормальный datetime
            timestamp = mktime(entry.published_parsed)
            pub_date = datetime.fromtimestamp(timestamp, timezone.utc)

        # Создаем Pydantic объект
        article = RSSArticle(
            source_name=source["name"],
            title=entry.title,
            url=entry.link,
            published_at=pub_date
        )
        articles.append(article)
        
    print(f"✅ {source['name']}: найдено {len(articles)} статей.")
    return articles


async def fetch_all_rss() -> list[RSSArticle]:
    """Асинхронно собирает статьи со всех источников."""
    print("🚀 Старт сбора RSS...")
    
    # Создаем задачи для параллельного выполнения
    tasks = [fetch_single_feed(source) for source in RSS_SOURCES]
    
    print("ЙООООУУУ1")
    # Ждем выполнения всех задач
    results = await asyncio.gather(*tasks)  # Здесь сделать, чтобы не стопился процесс сам
    
    print("ЙООООУУУУ2")
    # results - это список списков. "Сплющиваем" его в один плоский список
    all_articles = [article for sublist in results for article in sublist]
    
    print(f"🎉 Сбор завершен. Всего собрано: {len(all_articles)} статей.")
    return all_articles

# --- Блок для локального тестирования ---
if __name__ == "__main__":
    # Запускаем асинхронную функцию
    articles = asyncio.run(fetch_all_rss())
    
    # Выводим первые 5 статей, чтобы посмотреть на результат
    print("\n--- ПРИМЕР ДАННЫХ ---")
    for a in articles[:5]:
        print(f"[{a.source_name}] {a.published_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"Заголовок: {a.title}")
        print(f"Ссылка: {a.url}\n")
