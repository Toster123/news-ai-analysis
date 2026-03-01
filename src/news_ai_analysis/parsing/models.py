import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from src.news_ai_analysis.models import Base

class SourceType(str, enum.Enum):
    RSS = "rss"
    HTML = "html"
    API = "api"

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(SourceType), nullable=False)
    url = Column(String, nullable=False, unique=True)
    # можно добавить is_active, period и т.д.

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    url = Column(String, nullable=False, unique=True)
    published_at = Column(DateTime, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("Source")