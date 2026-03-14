from datetime import datetime
from pydantic import BaseModel


class RSSArticle(BaseModel):
    source_name: str        # Название источника (например, "Habr")
    title: str              # Заголовок новости
    url: str                # Ссылка на полный текст
    published_at: datetime  # Время публикации
