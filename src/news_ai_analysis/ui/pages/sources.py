from news_ai_analysis.ui.utils import *


class Sources:
    def __init__(self):
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