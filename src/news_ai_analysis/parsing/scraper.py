import asyncio
import httpx
import trafilatura


async def scrape_full_text(url: str) -> str | None:
    """
    Скачивает страницу и извлекает чистый текст статьи.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # 1. Загружаем HTML асинхронно
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            response = await client.get(url, follow_redirects=True)
            if response.status_code != 200:
                return None
            
            html_content = response.text

        # 2. Извлекаем текст с помощью trafilatura
        # Мы запускаем его в thread, так как библиотека внутри синхронная
        content = await asyncio.to_thread(
            trafilatura.extract,
            html_content,
            include_comments=False,
            include_tables=True,
            no_fallback=False  # Если не найдет основной текст, попробует другие методы
        )

        if not content:
            return None

        return content

    except Exception as e:
        return None

# --- Блок для локального тестирования ---
if __name__ == "__main__":
    test_url = "https://habr.com/ru/news/785862/" # Можно подставить любую свежую ссылку
    
    async def test():
        print(f"🕵️ Начинаем парсинг: {test_url}")
        text = await scrape_full_text(test_url)
        if text:
            print("\n✅ Успешно извлечено!")
            print(f"Длина текста: {len(text)} символов")
            print("-" * 50)
            print(text) # Печатаем первые 1000 символов
        else:
            print("\n❌ Контент не найден.")

    asyncio.run(test())
