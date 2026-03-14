from news_ai_analysis.ui.utils import *


class Chat:
    def __init__(self):
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
                    # response = self.__assistant.create_chat_completion(st.session_state.messages)

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