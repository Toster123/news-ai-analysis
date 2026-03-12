from src.news_ai_analysis.ui.utils import *


class Feed:
    def __init__(self):
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