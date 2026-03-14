"""
Страница ленты новостей
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from news_ai_analysis.collector.storage import get_articles, get_sources_stats


class Feed:
    def __init__(self):
        st.title("📰 Лента новостей")
        
        # Фильтры
        self.render_filters()
        
        # Лента новостей
        self.render_feed()
        
        # Статистика
        self.render_stats()
    
    def render_filters(self):
        """Рендер фильтров"""
        with st.expander("🔍 Фильтры", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Фильтр по источнику
                sources = list(set(a['source_name'] for a in st.session_state.get('articles', [])))
                sources.insert(0, "Все источники")
                st.session_state.selected_source = st.selectbox("Источник", sources)
            
            with col2:
                # Фильтр по дате
                st.session_state.days = st.selectbox(
                    "За период",
                    [1, 3, 7, 14, 30, 90],
                    format_func=lambda x: f"Последние {x} дней"
                )
            
            with col3:
                # Фильтр по наличию контента
                st.session_state.with_content = st.checkbox("Только с полным текстом")
            
            # Кнопка обновления
            if st.button("🔄 Обновить", type="primary"):
                st.rerun()
    
    def render_feed(self):
        """Рендер ленты новостей"""
        # Получаем отфильтрованные статьи
        articles = get_articles(
            source_name=st.session_state.selected_source if st.session_state.selected_source != "Все источники" else None,
            days_back=st.session_state.days,
            with_content=st.session_state.with_content,
            limit=50
        )
        
        if not articles:
            st.info("📭 Нет статей для отображения. Запустите сборщик новостей.")
            return
        
        # Отображаем статьи
        for article in articles:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### [{article['title']}]({article['url']})")
                    st.caption(f"📅 {article['published_at']} | 📌 {article['source_name']}")
                    
                    if article.get('summary'):
                        with st.expander("📄 Показать текст"):
                            st.write(article['summary'])
                    else:
                        if st.button(f"📥 Загрузить текст", key=f"load_{article['url']}"):
                            self.load_article_content(article)
                
                with col2:
                    # Здесь будут кнопки для анализа
                    if st.button("🔬 Анализ", key=f"analyze_{article['url']}"):
                        st.session_state['selected_article'] = article
                        st.switch_page("pages/sentiment.py")
                
                st.divider()
    
    def render_stats(self):
        """Рендер статистики"""
        with st.sidebar:
            st.markdown("---")
            st.subheader("📊 Статистика")
            
            stats = get_sources_stats()
            
            if stats:
                # Общая статистика
                total = sum(s['total'] for s in stats.values())
                st.metric("Всего статей", total)
                
                # Статистика по источникам
                for source, data in stats.items():
                    with st.expander(f"📌 {source}"):
                        st.metric("Статей", data['total'])
                        st.metric("С полным текстом", data['with_content'])
                        st.caption(f"Последняя: {data['last_article'][:10]}")
    
    async def load_article_content(self, article):
        """Загрузка полного текста статьи"""
        with st.spinner("Загружаем текст статьи..."):
            service = st.session_state.parsing_service
            content = await service.scrape_article_content(article['url'])
            
            if content:
                # Обновляем статью в session_state
                for a in st.session_state.articles:
                    if a['url'] == article['url']:
                        a['summary'] = content
                        break
                
                st.success("✅ Текст загружен!")
                st.rerun()
            else:
                st.error("❌ Не удалось загрузить текст")