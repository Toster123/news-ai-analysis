import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict
import uuid


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

def toggle_collector(action: str):
    """
    Управление сборщиком (обновленная версия)
    Теперь работает через сервис парсинга
    """
    if 'parsing_service' not in st.session_state:
        st.error("Сервис парсинга не инициализирован")
        return
    
    service = st.session_state.parsing_service
    
    if action == 'start':
        service.start_background_collection(interval_minutes=15)
        st.session_state.collector_status['running'] = True
        st.session_state.collector_status['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.success("✅ Сборщик запущен")
    elif action == 'stop':
        service.stop_background_collection()
        st.session_state.collector_status['running'] = False
        st.warning("🛑 Сборщик остановлен")