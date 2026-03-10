from src.news_ai_analysis.ui.utils import *

class System:
    def __init__(self):
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
