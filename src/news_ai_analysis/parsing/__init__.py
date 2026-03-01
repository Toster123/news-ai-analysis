from .rss import RSSParser
from .html import HTMLParser
from src.news_ai_analysis.models import SourceType

PARSERS = {
    SourceType.RSS: RSSParser(),
    SourceType.HTML: HTMLParser(),
}