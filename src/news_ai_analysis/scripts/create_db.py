# scripts/create_db.py
import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
from news_ai_analysis.parsing.models import Base

async def create_database():
    """Создает базу данных если её нет"""
    # Подключаемся к стандартной postgres базе для создания новой
    conn = await asyncpg.connect(
        user='postgres',
        password='password',
        host='localhost',
        port=5432,
        database='postgres'
    )
    
    # Проверяем существует ли база
    db_exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = 'newsdb'"
    )
    
    if not db_exists:
        await conn.execute('CREATE DATABASE newsdb')
        print("✅ База данных newsdb создана")
    else:
        print("ℹ️ База данных newsdb уже существует")
    
    await conn.close()

async def init_db():
    """Инициализация таблиц"""
    from news_ai_analysis.collector.service import ParsingService
    
    # Сначала создаем БД
    await create_database()
    
    # Затем инициализируем таблицы
    service = ParsingService("postgresql+asyncpg://postgres:password@localhost:5432/newsdb")
    await service.init_db()
    print("✅ Таблицы созданы")

if __name__ == "__main__":
    asyncio.run(init_db())