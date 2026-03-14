from news_ai_analysis.ui.utils import *


class Settings:
    def __init__(self):
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
