"""
Интеллектуальная система мониторинга новостей и трендов
Веб-интерфейс на Streamlit

Основные разделы:
1. Управление источниками (полная реализация CRUD)
2. Лента новостей и агрегация
3. Анализ тональности
4. AI Ассистент
5. Система и мониторинг
6. Настройки
"""


import uuid
import streamlit as st
from src.news_ai_analysis.ui.pages.sources import Sources
from src.news_ai_analysis.ui.pages.feed import Feed
from src.news_ai_analysis.ui.pages.sentiment import Sentiment
from src.news_ai_analysis.ui.pages.chat import Chat
from src.news_ai_analysis.ui.pages.system import System
from src.news_ai_analysis.ui.pages.settings import Settings
from src.news_ai_analysis.llm.service import LLM
from src.news_ai_analysis.assistant.service import Assistant
from src.news_ai_analysis.rag.service import Vectorstore


class App:
    def __init__(self):
        st.session_state.llm = LLM()
        st.session_state.asistant = Assistant(self.__llm)
        st.session_state.vectorstore = Vectorstore()
        # self.__sentiment_evaluator = SentimentEvaluator(llm)

        # Конфигурация страницы
        st.set_page_config(
            page_title="NewsTrend Monitor",
            page_icon="📰",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # ============================================
        # ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ (SESSION STATE)
        # ============================================

        if 'sources' not in st.session_state:
            # Начальные демо-данные
            st.session_state.sources = [
                {
                    'id': str(uuid.uuid4()),
                    'name': 'TechCrunch RSS',
                    'type': 'rss',
                    'config': {'url': 'https://techcrunch.com/feed/'},
                    'active': True,
                    'created_at': '2024-01-15 10:00:00'
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'BBC World News',
                    'type': 'gdelt-api',
                    'config': {'query': 'world news'},
                    'active': True,
                    'created_at': '2024-01-14 08:30:00'
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Currents News Service',
                    'type': 'currents-api',
                    'config': {'api_key': 'sk-xxxx-xxxx'},
                    'active': False,
                    'created_at': '2024-01-10 14:20:00'
                }
            ]

        if 'collector_status' not in st.session_state:
            st.session_state.collector_status = {
                'running': False,
                'start_time': None,
                'articles_collected': 0,
                'last_update': None
            }

        if 'messages' not in st.session_state:
            st.session_state.messages = []

        # Рендер боковой панели и получение выбранной страницы
        current_page = self.render_sidebar()

        # Рендер соответствующей страницы
        page_classes = {
            'sources': Sources,
            'feed': Feed,
            'sentiment': Sentiment,
            'chat': Chat,
            'system': System,
            'settings': Settings
        }

        page_classes[current_page]()


    def render_sidebar(self):
        """Боковая панель с навигацией и управлением сборщиком"""

        # Заголовок приложения
        st.sidebar.title("📰 NewsTrend Monitor")
        st.sidebar.markdown("---")

        # Навигация
        pages = {
            'Управление источниками': 'sources',
            'Лента новостей': 'feed',
            'Анализ тональности': 'sentiment',
            'AI Ассистент': 'chat',
            'Система': 'system',
            'Настройки': 'settings'
        }

        selected_page = st.sidebar.radio(
            "📂 Разделы",
            list(pages.keys()),
            index=0
        )

        st.sidebar.markdown("---")

        # Блок управления сборщиком
        st.sidebar.header("🎛️ Управление сборщиком")

        # Статус сборщика
        status = st.session_state.collector_status
        if status['running']:
            st.sidebar.success("🟢 Сборщик запущен")
        else:
            st.sidebar.warning("🔴 Сборщик остановлен")

        # Кнопки управления
        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button(
                "▶️ Старт",
                disabled=status['running'],
                use_container_width=True,
                type="primary"
            ):
                toggle_collector('start')
                st.rerun()

        with col2:
            if st.button(
                "⏹️ Стоп",
                disabled=not status['running'],
                use_container_width=True
            ):
                toggle_collector('stop')
                st.rerun()

        # Метрики сборщика
        st.sidebar.markdown("### 📊 Метрики")
        if status['running'] and status['start_time']:
            st.sidebar.info(f"Время работы: {status['start_time']}")
        st.sidebar.metric("Собрано статей", status['articles_collected'])

        st.sidebar.markdown("---")
        st.sidebar.caption("© 2026 NewsTrend Monitor")

        return pages[selected_page]