from news_ai_analysis.ui.utils import *


class Sentiment:
    def __init__(self):
        """Раздел: Анализ тональности"""

        st.title("💭 Анализ тональности")

        st.subheader("🔑 Ключевые слова для анализа тональности")

        if 'sentiment_keywords' not in st.session_state:
            st.session_state.sentiment_keywords = []

        selected_keywords = []
        for idx, keyword in enumerate(st.session_state.sentiment_keywords):
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                if st.checkbox("Выбрать", key=f"del_keyword_{idx}"):
                    selected_keywords.append(keyword)
            with col2:
                st.write(keyword)

        if selected_keywords:
            if st.button("🗑️ Удалить выбранные ключевые слова", key="remove_selected_keywords"):
                st.session_state.sentiment_keywords = [kw for kw in st.session_state.sentiment_keywords if kw not in selected_keywords]
                st.success("Ключевые слова удалены!")
                st.rerun()
        else:
            st.info("Выберите ключевые слова для удаления")

        with st.form("add_keyword_form"):
            new_keyword = st.text_input("Новое ключевое слово", placeholder="Введите ключевое слово...")
            submitted = st.form_submit_button("Добавить")
            if submitted:
                if new_keyword and new_keyword.strip():
                    if new_keyword.strip() not in st.session_state.sentiment_keywords:
                        st.session_state.sentiment_keywords.append(new_keyword.strip())
                        st.success(f"Ключевое слово '{new_keyword}' добавлено!")
                        st.rerun()
                    else:
                        st.error("Это ключевое слово уже есть в списке.")
                else:
                    st.error("Пожалуйста, введите ключевое слово.")

        st.markdown("---")

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