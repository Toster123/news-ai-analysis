"""
Интеллектуальная система мониторинга новостей и трендов
Веб-интерфейс на Streamlit
"""

import uuid
import streamlit as st
from datetime import datetime
from news_ai_analysis.ui.pages.sources import Sources
from news_ai_analysis.ui.pages.feed import Feed
from news_ai_analysis.ui.pages.sentiment import Sentiment
from news_ai_analysis.ui.pages.chat import Chat
from news_ai_analysis.ui.pages.system import System
from news_ai_analysis.ui.pages.settings import Settings
from news_ai_analysis.llm.service import LLM
from news_ai_analysis.assistant.service import Assistant
from news_ai_analysis.rag.service import Vectorstore
from news_ai_analysis.ui.utils import toggle_collector
from news_ai_analysis.collector.service import ParsingService


class App:
    def __init__(self):
        st.session_state.llm = LLM()
        st.session_state.asistant = Assistant(self.__llm)
        st.session_state.vectorstore = Vectorstore()
        # self.__sentiment_evaluator = SentimentEvaluator(llm)

        # Инициализация сервиса парсинга
        if 'parsing_service' not in st.session_state:
            st.session_state.parsing_service = ParsingService()

        # Конфигурация страницы
        st.set_page_config(
            page_title="NewsTrend Monitor",
            page_icon="📰",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ (SESSION STATE)
        if 'sources' not in st.session_state:
            # Начальные демо-данные - только RSS источники!
            st.session_state.sources = [
                {
                    'id': str(uuid.uuid4()),
                    'name': 'TechCrunch (AI)',
                    'type': 'rss',
                    'config': {'url': 'https://techcrunch.com/category/artificial-intelligence/feed/'},
                    'active': True,
                    'created_at': '2024-01-15 10:00:00'
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'The Verge',
                    'type': 'rss',
                    'config': {'url': 'https://www.theverge.com/rss/index.xml'},
                    'active': True,
                    'created_at': '2024-01-14 08:30:00'
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'ArXiv AI',
                    'type': 'rss',
                    'config': {'url': 'http://export.arxiv.org/rss/cs.AI'},
                    'active': True,
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

        if 'articles' not in st.session_state:
            st.session_state.articles = []

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
            if status['last_update']:
                st.sidebar.caption(
                    f"Последнее обновление: {status['last_update']}")
        else:
            st.sidebar.warning("🔴 Сборщик остановлен")

        # Кнопки управления
        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button(
                "▶️ Старт",
                disabled=status['running'],
                use_container_width=True,
                type="primary",
                key="start_collector"
            ):
                self._start_collector()
                st.rerun()

        with col2:
            if st.button(
                "⏹️ Стоп",
                disabled=not status['running'],
                use_container_width=True,
                key="stop_collector"
            ):
                self._stop_collector()
                print("БАНДУРА ЗАПУСТИЛАСЬ 1")
                st.rerun()

        # Метрики сборщика
        st.sidebar.markdown("### 📊 Метрики")
        st.sidebar.metric("Всего собрано статей", status['articles_collected'])

        # Количество активных источников
        active_sources = len(
            [s for s in st.session_state.sources if s['active']])
        st.sidebar.metric("Активных RSS источников", active_sources)

        st.sidebar.markdown("---")
        st.sidebar.caption("© 2026 NewsTrend Monitor")

        return pages[selected_page]

    def _start_collector(self):
        """Запуск сборщика новостей"""
        service: ParsingService = st.session_state.parsing_service
        print("БАНДУРА ЗАПУСТИЛАСЬ 2")
        service.start_background_collection(interval_minutes=15)

        st.session_state.collector_status['running'] = True
        st.session_state.collector_status['start_time'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')

    def _stop_collector(self):
        """Остановка сборщика новостей"""
        service = st.session_state.parsing_service
        service.stop_background_collection()

        st.session_state.collector_status['running'] = False
