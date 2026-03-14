"""
Функции для работы с хранилищем статей
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import streamlit as st


def get_articles(
    source_name: Optional[str] = None,
    days_back: Optional[int] = None,
    limit: int = 100,
    with_content: bool = False
) -> List[Dict]:
    """
    Получение статей из session_state с фильтрацией
    
    Args:
        source_name: Фильтр по источнику
        days_back: Только статьи за последние N дней
        limit: Максимальное количество статей
        with_content: Только статьи с загруженным контентом
    """
    if 'articles' not in st.session_state:
        return []
    
    articles = st.session_state.articles
    
    # Фильтр по источнику
    if source_name:
        articles = [a for a in articles if a['source_name'] == source_name]
    
    # Фильтр по дате
    if days_back:
        cutoff = datetime.now() - timedelta(days=days_back)
        articles = [
            a for a in articles 
            if datetime.fromisoformat(a['published_at']) > cutoff
        ]
    
    # Фильтр по наличию контента
    if with_content:
        articles = [a for a in articles if a.get('summary')]
    
    # Сортировка по дате (сначала новые)
    articles.sort(
        key=lambda x: x.get('published_at', ''), 
        reverse=True
    )
    
    return articles[:limit]


def get_sources_stats() -> Dict:
    """Статистика по источникам"""
    if 'articles' not in st.session_state:
        return {}
    
    articles = st.session_state.articles
    stats = {}
    
    for article in articles:
        source = article['source_name']
        if source not in stats:
            stats[source] = {
                'total': 0,
                'with_content': 0,
                'last_article': article['published_at']
            }
        
        stats[source]['total'] += 1
        if article.get('summary'):
            stats[source]['with_content'] += 1
        
        # Обновляем дату последней статьи
        article_date = article['published_at']
        if article_date > stats[source]['last_article']:
            stats[source]['last_article'] = article_date
    
    return stats


def add_article_to_session(article: Dict):
    """Добавление статьи в session_state"""
    if 'articles' not in st.session_state:
        st.session_state.articles = []
    
    # Проверка на дубликат
    for existing in st.session_state.articles:
        if existing['url'] == article['url']:
            return False
    
    st.session_state.articles.append(article)
    return True


def clear_old_articles(days: int = 30):
    """Очистка статей старше указанного количества дней"""
    if 'articles' in st.session_state:
        cutoff = datetime.now() - timedelta(days=days)
        st.session_state.articles = [
            a for a in st.session_state.articles 
            if datetime.fromisoformat(a.get('published_at', '')) > cutoff
        ]