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

import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from typing import Dict, List, Optional

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

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def get_source_type_label(source_type: str) -> str:
    """Возвращает читаемое название типа источника"""
    labels = {
        'rss': 'RSS лента',
        'gdelt-api': 'GDELT API',
        'currents-api': 'Currents API'
    }
    return labels.get(source_type, source_type)

def get_source_icon(source_type: str) -> str:
    """Возвращает иконку для типа источника"""
    icons = {
        'rss': '📡',
        'gdelt-api': '🌍',
        'currents-api': '📰'
    }
    return icons.get(source_type, '📌')

def validate_source_config(source_type: str, config: Dict) -> tuple[bool, str]:
    """Валидация конфигурации источника"""
    if source_type == 'rss':
        if 'url' not in config or not config['url']:
            return False, "URL обязателен для RSS источника"
        if not config['url'].startswith(('http://', 'https://')):
            return False, "URL должен начинаться с http:// или https://"
    elif source_type == 'currents-api':
        if 'api_key' not in config or not config['api_key']:
            return False, "API Key обязателен для Currents API"
    elif source_type == 'gdelt-api':
        # GDELT может работать без параметров
        pass
    return True, ""

def add_source(name: str, source_type: str, config: Dict, active: bool = True) -> bool:
    """Добавление нового источника"""
    valid, error_msg = validate_source_config(source_type, config)
    if not valid:
        st.error(error_msg)
        return False

    new_source = {
        'id': str(uuid.uuid4()),
        'name': name,
        'type': source_type,
        'config': config,
        'active': active,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    st.session_state.sources.append(new_source)
    return True

def update_source(source_id: str, name: str, source_type: str, config: Dict, active: bool) -> bool:
    """Обновление существующего источника"""
    valid, error_msg = validate_source_config(source_type, config)
    if not valid:
        st.error(error_msg)
        return False

    for source in st.session_state.sources:
        if source['id'] == source_id:
            source['name'] = name
            source['type'] = source_type
            source['config'] = config
            source['active'] = active
            return True
    return False

def delete_source(source_id: str) -> bool:
    """Удаление источника"""
    st.session_state.sources = [s for s in st.session_state.sources if s['id'] != source_id]
    return True

def toggle_collector(action: str):
    """Управление сборщиком"""
    if action == 'start':
        st.session_state.collector_status['running'] = True
        st.session_state.collector_status['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elif action == 'stop':
        st.session_state.collector_status['running'] = False

# ============================================
# КОМПОНЕНТЫ ИНТЕРФЕЙСА
# ============================================

def render_sidebar():
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


def render_sources_page():
    """Раздел: Управление источниками"""

    st.title("📡 Управление источниками")

    # Вкладки для разных действий
    tab1, tab2, tab3 = st.tabs(["📋 Список источников", "➕ Добавить источник", "✏️ Редактировать"])

    # === Вкладка 1: Список источников ===
    with tab1:
        st.subheader("Зарегистрированные источники")

        if not st.session_state.sources:
            st.info("Источники пока не добавлены. Перейдите во вкладку 'Добавить источник'.")
        else:
            # Формирование данных для отображения
            sources_data = []
            for source in st.session_state.sources:
                # Форматирование конфига для отображения
                if source['type'] == 'rss':
                    config_display = source['config'].get('url', '')
                elif source['type'] == 'currents-api':
                    config_display = '••••••••' + source['config'].get('api_key', '')[-4:]
                elif source['type'] == 'gdelt-api':
                    config_display = source['config'].get('query', '(без фильтра)')
                else:
                    config_display = str(source['config'])

                sources_data.append({
                    'ID': source['id'],
                    'Название': source['name'],
                    'Тип': get_source_type_label(source['type']),
                    'Конфигурация': config_display,
                    'Статус': '🟢 Активен' if source['active'] else '🔴 Неактивен',
                    'Создан': source['created_at']
                })

            df = pd.DataFrame(sources_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # Удаление источников
            st.markdown("### 🗑️ Удаление источников")

            # Чекбоксы для выбора источников на удаление
            selected_for_delete = []
            for source in st.session_state.sources:
                col1, col2 = st.columns([0.1, 1])
                with col1:
                    if st.checkbox(f"Выбрать", key=f"delete_{source['id']}"):
                        selected_for_delete.append(source['id'])
                with col2:
                    st.write(f"**{source['name']}** ({get_source_type_label(source['type'])})")

            if selected_for_delete:
                if st.button("🗑️ Удалить выбранные источники", type="primary"):
                    for source_id in selected_for_delete:
                        delete_source(source_id)
                    st.success(f"Удалено источников: {len(selected_for_delete)}")
                    st.rerun()
            else:
                st.info("Выберите источники для удаления")

    # === Вкладка 2: Добавление источника ===
    with tab2:
        st.subheader("Добавление нового источника")

        with st.form("add_source_form"):
            # Название источника
            name = st.text_input(
                "Название источника",
                placeholder="Например: TechCrunch RSS",
                help="Введите понятное название для идентификации источника"
            )

            # Тип источника
            source_type = st.selectbox(
                "Тип источника",
                options=['rss', 'gdelt-api', 'currents-api'],
                format_func=get_source_type_label,
                help="Выберите тип источника данных"
            )

            # Динамические поля в зависимости от типа
            config = {}

            if source_type == 'rss':
                config['url'] = st.text_input(
                    "URL RSS ленты",
                    placeholder="https://example.com/feed.xml",
                    help="Полный URL RSS или Atom ленты"
                )

            elif source_type == 'currents-api':
                config['api_key'] = st.text_input(
                    "API Key",
                    type="password",
                    placeholder="sk-xxxxxxxxxxxxxxxx",
                    help="Ваш API ключ от сервиса Currents API"
                )

            elif source_type == 'gdelt-api':
                config['query'] = st.text_input(
                    "Поисковый запрос (опционально)",
                    placeholder="Например: technology AI",
                    help="Ключевые слова для фильтрации новостей в GDELT"
                )
                config['mode'] = st.selectbox(
                    "Режим поиска",
                    options=['artlist', 'timelinevol'],
                    format_func=lambda x: 'Список статей' if x == 'artlist' else 'Временная шкала',
                    help="artlist - список статей, timelinevol - временная шкала"
                )

            # Активность
            active = st.toggle("Активен", value=True, help="Включить сбор из этого источника")

            # Кнопка отправки
            submitted = st.form_submit_button("💾 Добавить источник", type="primary", use_container_width=True)

            if submitted:
                if not name:
                    st.error("Пожалуйста, введите название источника")
                else:
                    if add_source(name, source_type, config, active):
                        st.success(f"✅ Источник '{name}' успешно добавлен!")
                        st.rerun()

    # === Вкладка 3: Редактирование источника ===
    with tab3:
        st.subheader("Редактирование источника")

        if not st.session_state.sources:
            st.info("Нет источников для редактирования.")
        else:
            # Выбор источника для редактирования
            source_options = {s['id']: f"{s['name']} ({get_source_type_label(s['type'])})"
                           for s in st.session_state.sources}
            selected_id = st.selectbox(
                "Выберите источник",
                options=list(source_options.keys()),
                format_func=lambda x: source_options[x]
            )

            if selected_id:
                # Поиск источника
                source = next((s for s in st.session_state.sources if s['id'] == selected_id), None)

                if source:
                    with st.form("edit_source_form"):
                        # Название
                        edit_name = st.text_input(
                            "Название",
                            value=source['name']
                        )

                        # Тип (только для чтения - нельзя менять тип)
                        st.text_input(
                            "Тип",
                            value=get_source_type_label(source['type']),
                            disabled=True
                        )

                        # Динамические поля
                        edit_config = {}

                        if source['type'] == 'rss':
                            edit_config['url'] = st.text_input(
                                "URL RSS ленты",
                                value=source['config'].get('url', '')
                            )

                        elif source['type'] == 'currents-api':
                            edit_config['api_key'] = st.text_input(
                                "API Key",
                                type="password",
                                value=source['config'].get('api_key', ''),
                                placeholder="Оставьте пустым, чтобы не менять"
                            )

                        elif source['type'] == 'gdelt-api':
                            edit_config['query'] = st.text_input(
                                "Поисковый запрос",
                                value=source['config'].get('query', '')
                            )
                            edit_config['mode'] = st.selectbox(
                                "Режим поиска",
                                options=['artlist', 'timelinevol'],
                                index=0 if source['config'].get('mode') == 'artlist' else 1,
                                format_func=lambda x: 'Список статей' if x == 'artlist' else 'Временная шкала'
                            )

                        # Активность
                        edit_active = st.toggle("Активен", value=source['active'])

                        # Кнопки
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            update_submitted = st.form_submit_button("💾 Сохранить изменения", type="primary", use_container_width=True)
                        with col2:
                            delete_submitted = st.form_submit_button("🗑️ Удалить источник", use_container_width=True)

                        if update_submitted:
                            if not edit_name:
                                st.error("Название не может быть пустым")
                            else:
                                # Если API ключ не изменяется, оставляем старый
                                if source['type'] == 'currents-api' and not edit_config.get('api_key'):
                                    edit_config['api_key'] = source['config'].get('api_key', '')

                                if update_source(selected_id, edit_name, source['type'], edit_config, edit_active):
                                    st.success("✅ Изменения сохранены!")
                                    st.rerun()

                        if delete_submitted:
                            delete_source(selected_id)
                            st.success("Источник удален")
                            st.rerun()


def render_feed_page():
    """Раздел: Лента новостей и агрегация"""

    st.title("📰 Лента новостей")

    # Фильтры
    st.subheader("Фильтры")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Выбор источников
        source_options = ["Все источники"] + [s['name'] for s in st.session_state.sources if s['active']]
        selected_sources = st.multiselect(
            "Источники",
            options=source_options[1:],
            default=source_options[1:],
            help="Выберите источники для отображения"
        )

    with col2:
        # Ключевые слова
        keywords = st.text_input(
            "Ключевые слова",
            placeholder="Например: AI, технологии, бизнес",
            help="Фильтр по ключевым словам в заголовках"
        )

    with col3:
        # Даты
        date_range = st.date_input(
            "Период",
            value=(),
            help="Выберите диапазон дат"
        )

    # Кнопка применения фильтров
    if st.button("🔍 Применить фильтры", type="primary"):
        st.rerun()

    st.markdown("---")

    # Демо-данные новостей
    st.subheader("Новости")

    demo_news = [
        {
            'title': 'Искусственный интеллект трансформирует индустрию здравоохранения',
            'date': '2024-01-20',
            'source': 'TechCrunch RSS',
            'summary': 'Н покаовые исследованиязывают, что AI-системы значительно улучшают диагностику заболеваний...',
            'sentiment': 'Позитивная',
            'tags': ['AI', 'здравоохранение', 'технологии']
        },
        {
            'title': 'Экономические эксперты предупреждают о возможной рецессии',
            'date': '2024-01-19',
            'source': 'BBC World News',
            'summary': 'Ведущие экономисты мира обсуждают риски глобальной рецессии и её возможные последствия...',
            'sentiment': 'Негативная',
            'tags': ['экономика', 'финансы', 'рецессия']
        },
        {
            'title': 'Новая технология квантовых вычислений представлена на конференции',
            'date': '2024-01-18',
            'source': 'TechCrunch RSS',
            'summary': 'Квантовые компьютеры становятся ближе к практическому применению в бизнесе...',
            'sentiment': 'Нейтральная',
            'tags': ['квантовые вычисления', 'технологии', 'инновации']
        }
    ]

    # Отображение карточек новостей
    for news in demo_news:
        with st.container():
            # Заголовок
            st.markdown(f"### {news['title']}")

            # Мета-информация
            col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
            with col1:
                st.caption(f"📅 {news['date']}")
            with col2:
                st.caption(f"📰 {news['source']}")
            with col3:
                sentiment_color = "🟢" if news['sentiment'] == 'Позитивная' else ("🔴" if news['sentiment'] == 'Негативная' else "🟡")
                st.caption(f"{sentiment_color} {news['sentiment']}")
            with col4:
                st.caption(f"Теги: {', '.join(news['tags'])}")

            # Краткое содержание
            st.write(news['summary'])

            # Кнопки действий
            col1, col2 = st.columns([1, 10])
            with col1:
                if st.button("🔗 Открыть", key=f"open_{news['title'][:10]}"):
                    pass
            with col2:
                if st.button("📊 Детальный анализ", key=f"analyze_{news['title'][:10]}"):
                    pass

            st.markdown("---")

    # Пагинация
    st.markdown("### Страницы")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    with col1:
        st.button("◀ Предыдущая", disabled=True)
    with col2:
        st.button("1", type="primary")
    with col3:
        st.button("2")
    with col4:
        st.button("3")
    with col5:
        st.button("Следующая ▶")


def render_sentiment_page():
    """Раздел: Анализ тональности"""

    st.title("💭 Анализ тональности")

    # Сводная статистика
    st.subheader("Сводка")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Всего статей", "1,234")
    with col2:
        st.metric("🟢 Позитивных", "456 (37%)")
    with col3:
        st.metric("🔴 Негативных", "234 (19%)")
    with col4:
        st.metric("🟡 Нейтральных", "544 (44%)")

    st.markdown("---")

    # Визуализация
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Распределение тональности")

        # Демо данные для pie chart
        sentiment_data = pd.DataFrame({
            'Тональность': ['Позитивная', 'Негативная', 'Нейтральная'],
            'Количество': [456, 234, 544]
        })

        st.bar_chart(sentiment_data.set_index('Тональность'))

    with col2:
        st.subheader("Динамика тональности (7 дней)")

        # Демо данные для line chart
        dates = pd.date_range(start='2024-01-14', periods=7)
        timeline_data = pd.DataFrame({
            'Дата': dates,
            'Позитивная': [50, 65, 45, 70, 55, 60, 75],
            'Негативная': [30, 25, 40, 20, 35, 30, 25],
            'Нейтральная': [20, 25, 30, 25, 30, 25, 30]
        })

        st.line_chart(timeline_data.set_index('Дата'))

    st.markdown("---")

    # Топ тем по тональности
    st.subheader("Топ тем")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🟢 Самые позитивные темы")
        positive_topics = [
            {'Тема': 'Технологии AI', 'Индекс': 0.85},
            {'Тема': 'Экология', 'Индекс': 0.78},
            {'Тема': 'Медицина', 'Индекс': 0.72},
            {'Тема': 'Космос', 'Индекс': 0.68},
            {'Тема': 'Образование', 'Индекс': 0.65}
        ]
        st.dataframe(pd.DataFrame(positive_topics), hide_index=True)

    with col2:
        st.markdown("#### 🔴 Самые негативные темы")
        negative_topics = [
            {'Тема': 'Конфликты', 'Индекс': -0.72},
            {'Тема': 'Экономика', 'Индекс': -0.55},
            {'Тема': 'Политика', 'Индекс': -0.48},
            {'Тема': 'Преступность', 'Индекс': -0.45},
            {'Тема': 'Безработица', 'Индекс': -0.38}
        ]
        st.dataframe(pd.DataFrame(negative_topics), hide_index=True)

    # Детальный анализ по теме
    st.markdown("---")
    st.subheader("Детальный анализ")

    topic = st.selectbox(
        "Выберите тему для детального анализа",
        options=['Все темы', 'Технологии AI', 'Экономика', 'Политика', 'Здравоохранение']
    )

    if topic and topic != 'Все темы':
        st.write(f"**Анализ тональности по теме: {topic}**")

        topic_news = [
            {'Заголовок': 'AI помогает врачам диагностировать рак на ранних стадиях', 'Тональность': 'Позитивная', 'Уверенность': '92%'},
            {'Заголовок': 'Новые регуляции AI вызывают опасения у бизнеса', 'Тональность': 'Негативная', 'Уверенность': '78%'},
            {'Заголовок': 'Компании инвестируют миллиарды в AI разработки', 'Тональность': 'Позитивная', 'Уверенность': '88%'}
        ]
        st.dataframe(pd.DataFrame(topic_news), hide_index=True)


def render_chat_page():
    """Раздел: AI Ассистент"""

    st.title("🤖 AI Ассистент")

    st.markdown("""
    Задавайте вопросы о собранных новостях и трендах. Ассистент поможет проанализировать
    информацию и предоставить ключевые инсайты.
    """)

    st.markdown("---")

    # История чата
    st.subheader("История сообщений")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Ввод пользователя
    if prompt := st.chat_input("Введите ваш вопрос..."):

        # Добавление сообщения пользователя
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Генерация ответа (заглушка)
        with st.chat_message("assistant"):
            with st.spinner("Анализирую данные..."):
                import time
                time.sleep(1.5)  # Имитация обработки

                # Демо ответ
                response = f"""📊 **Результаты анализа по запросу: "{prompt}"**

За последнюю неделю в источниках было найдено **156 статей** по данной теме.

**Ключевые находки:**
1. **Основной тренд**: Обсуждение данной темы выросло на 23% по сравнению с предыдущей неделей
2. **Доминирующая тональность**: Нейтральная (54%), с тенденцией к позитивной
3. **Активные источники**: TechCrunch (45%), BBC (30%), Reuters (25%)

**Главные события:**
- Эксперты отмечают рост интереса к технологиям
- Новые партнерства в индустрии
- Регуляторные изменения

_Это демонстрационный ответ. Для получения реальных данных требуется подключение к API и базе данных._"""

                st.markdown(response)

                # Добавление ответа в историю
                st.session_state.messages.append({"role": "assistant", "content": response})

    # Примеры вопросов
    st.markdown("---")
    st.subheader("Примеры вопросов")

    example_questions = [
        "Что пишут о компании X за последнюю неделю?",
        "Суммируй основные новости по теме Y",
        "Какие источники наиболее активно освещают тему Z?",
        "Какие тренды были в политике за последний месяц?"
    ]

    cols = st.columns(2)
    for i, question in enumerate(example_questions):
        with cols[i % 2]:
            if st.button(f"💬 {question}", key=f"example_{i}"):
                st.rerun()


def render_system_page():
    """Раздел: Система и мониторинг"""

    st.title("⚙️ Система и мониторинг")

    # Статус системы
    st.subheader("Статус системы")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Статус", "🟢 Работает")
    with col2:
        st.metric("Время работы", "12ч 34м")
    with col3:
        st.metric("CPU", "45%")
    with col4:
        st.metric("RAM", "2.1 GB")

    st.markdown("---")

    # Мониторинг очереди
    st.subheader("Очередь обработки")

    col1, col2 = st.columns(2)

    with col1:
        st.progress(65, text="Обработка новостей: 65%")
        st.write("В очереди: 234 задачи")

    with col2:
        st.metric("Всего статей в БД", "12,456")
        st.metric("Размер индекса", "156 MB")

    # Логи
    st.markdown("---")
    st.subheader("Последние логи")

    logs = [
        "[2024-01-20 14:30:25] INFO: Сборщик запущен",
        "[2024-01-20 14:30:26] INFO: Подключение к RSS источнику: TechCrunch",
        "[2024-01-20 14:30:28] INFO: Получено 25 статей",
        "[2024-01-20 14:30:30] INFO: Подключение к GDELT API",
        "[2024-01-20 14:30:35] INFO: Получено 150 статей",
        "[2024-01-20 14:30:40] INFO: Анализ тональности: завершено 175 статей",
        "[2024-01-20 14:30:42] WARNING: Не удалось подключиться к источнику: Currents API (timeout)",
        "[2024-01-20 14:30:45] INFO: Дедупликация: найдено 12 дубликатов"
    ]

    st.code("\n".join(logs), language="log")

    # Кнопки управления
    st.markdown("---")
    st.subheader("Управление")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Перезапустить сборщик", use_container_width=True):
            st.success("Команда отправлена")

    with col2:
        if st.button("🧹 Очистить кэш", use_container_width=True):
            st.success("Кэш очищен")

    with col3:
        if st.button("📤 Экспорт данных", use_container_width=True):
            st.success("Экспорт начат")


def render_settings_page():
    """Раздел: Настройки"""

    st.title("⚙️ Настройки")

    # Общие настройки
    st.subheader("Общие настройки")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Интервал сбора (минуты)", value="15")
        st.selectbox("Язык интерфейса", options=["Русский", "English"], index=0)

    with col2:
        st.toggle("Тёмная тема", value=True)
        st.toggle("Уведомления в Telegram", value=False)

    st.markdown("---")

    # Настройки источников
    st.subheader("Настройки источников")

    col1, col2 = st.columns(2)

    with col1:
        st.number_input("Максимум статей за раз", min_value=10, max_value=500, value=100)
        st.number_input("Таймаут запроса (сек)", min_value=5, max_value=60, value=30)

    with col2:
        st.toggle("Автоматическая дедупликация", value=True)
        st.toggle("Обработка изображений", value=False)

    st.markdown("---")

    # Feature Flags (Пути развития)
    st.subheader("🧪 Экспериментальные функции")

    st.toggle("🤖 Мультиагентный режим (Beta)", value=False)
    st.caption("Включает систему из агентов: Сборщик, Аналитик, Детектор трендов, Верификатор")

    st.toggle("🌐 Интеграция с соцсетями", value=False)
    st.caption("Мониторинг Twitter, Reddit, Telegram-каналов")

    st.toggle("📊 Расширенная аналитика", value=False)
    st.caption("Визуализации: временные линии, карты связей, облака тегов")

    st.markdown("---")

    # Roadmap
    st.subheader("🗺️ Roadmap")

    roadmap_items = [
        {"Функция": "✅ RSS и базовые API", "Статус": "Готово"},
        {"Функция": "✅ Управление источниками", "Статус": "Готово"},
        {"Функция": "🔄 Анализ тональности", "Статус": "В разработке"},
        {"Функция": "⏳ AI Ассистент", "Статус": "Запланировано"},
        {"Функция": "⏳ Детектор трендов", "Статус": "Запланировано"},
        {"Функция": "⏳ Интеграция с соцсетями", "Статус": "Запланировано"}
    ]

    st.dataframe(pd.DataFrame(roadmap_items), hide_index=True, use_container_width=True)

    # Сохранение настроек
    st.markdown("---")
    if st.button("💾 Сохранить настройки", type="primary", use_container_width=True):
        st.success("Настройки сохранены!")


# ============================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================

def main():
    """Главная функция приложения"""

    # Рендер боковой панели и получение выбранной страницы
    current_page = render_sidebar()

    # Рендер соответствующей страницы
    if current_page == 'sources':
        render_sources_page()
    elif current_page == 'feed':
        render_feed_page()
    elif current_page == 'sentiment':
        render_sentiment_page()
    elif current_page == 'chat':
        render_chat_page()
    elif current_page == 'system':
        render_system_page()
    elif current_page == 'settings':
        render_settings_page()


if __name__ == "__main__":
    main()
