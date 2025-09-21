import streamlit as st
import pandas as pd
import io
import traceback
from pathlib import Path
import sys

# Добавляем текущую директорию в путь для импорта
sys.path.append('.')

# Импортируем классы из ноутбука
try:
    # Сначала нужно извлечь код из ноутбука
    import json
    import re
    
    # Читаем ноутбук
    with open('ux_analyzer_core_ebicya.ipynb', 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Извлекаем код из ячеек
    code_cells = []
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            code_cells.extend(cell['source'])
    
    # Объединяем код
    full_code = ''.join(code_cells)
    
    # Выполняем код
    exec(full_code, globals())
    
except Exception as e:
    st.error(f"Ошибка загрузки анализатора: {e}")
    st.stop()

# Настройка страницы
st.set_page_config(
    page_title="UX Анализатор",
    page_icon="🔬",
    layout="wide"
)

# Заголовок
st.title("🔬 UX Анализатор V24.0")
st.markdown("---")

# Создаем интерфейс
if 'analyzer_interface' not in st.session_state:
    st.session_state.analyzer_interface = UXAnalyzerInterface()

interface = st.session_state.analyzer_interface

# Секция настроек
st.header("⚙️ Настройки")

col1, col2 = st.columns(2)

with col1:
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Введите ваш Gemini API ключ",
        help="Получите ключ на https://makersuite.google.com/app/apikey"
    )
    
    company_name = st.text_input(
        "Название компании",
        value="Company",
        placeholder="Название компании"
    )

with col2:
    report_title = st.text_input(
        "Название отчета",
        value="UX Research Report",
        placeholder="Название отчета"
    )
    
    author = st.text_input(
        "Автор отчета",
        value="Research Team",
        placeholder="Автор отчета"
    )

# Секция загрузки данных
st.header("📤 Загрузка данных")

col1, col2 = st.columns(2)

with col1:
    uploaded_files = st.file_uploader(
        "Загрузите транскрипты",
        type=['txt', 'md'],
        accept_multiple_files=True,
        help="Выберите файлы с транскриптами интервью"
    )

with col2:
    uploaded_brief = st.file_uploader(
        "Загрузите бриф (опционально)",
        type=['txt', 'md'],
        help="Бриф с целями исследования"
    )

# Обработка загруженных файлов
if uploaded_files:
    st.success(f"✅ Загружено {len(uploaded_files)} файлов")
    interface.transcripts = []
    for file in uploaded_files:
        content = file.read().decode('utf-8')
        interface.transcripts.append(content)
    interface.analyze_btn.disabled = False

if uploaded_brief:
    st.success("✅ Бриф загружен")
    interface.brief_content = uploaded_brief.read().decode('utf-8')

# Секция анализа
st.header("🔬 Анализ")

if st.button("🚀 Начать анализ", type="primary", disabled=not uploaded_files):
    if not api_key:
        st.error("❌ Введите API ключ!")
    elif not uploaded_files:
        st.error("❌ Загрузите транскрипты!")
    else:
        # Обновляем конфигурацию
        interface.company_config.name = company_name
        interface.company_config.report_title = report_title
        interface.company_config.author = author
        
        # Устанавливаем API ключ
        interface.api_key = api_key
        
        # Показываем прогресс
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Создаем анализатор
            status_text.text("🔧 Инициализация анализатора...")
            progress_bar.progress(10)
            
            interface.analyzer = AdvancedGeminiAnalyzer(api_key)
            
            # Устанавливаем бриф если есть
            if uploaded_brief:
                interface.analyzer.set_brief(interface.brief_content)
            
            status_text.text("🔬 Запуск анализа...")
            progress_bar.progress(30)
            
            # Запускаем анализ
            results = interface.analyzer.analyze_transcripts_parallel(interface.transcripts)
            
            status_text.text("📊 Генерация отчетов...")
            progress_bar.progress(80)
            
            # Генерируем отчеты
            interface._generate_reports(results)
            
            progress_bar.progress(100)
            status_text.text("✅ Анализ завершен!")
            
            st.success("🎉 Анализ успешно завершен! Результаты отображены ниже.")
            
        except Exception as e:
            st.error(f"❌ Ошибка при анализе: {e}")
            st.code(traceback.format_exc())

# Секция результатов
if hasattr(interface, 'output_widget') and interface.output_widget:
    st.header("📊 Результаты")
    # Здесь будут отображаться результаты анализа
    st.info("Результаты анализа появятся здесь после завершения обработки")

# Информация о системе
st.sidebar.header("ℹ️ Информация")
st.sidebar.info("""
**UX Анализатор V24.0**

Этот инструмент анализирует транскрипты пользовательских интервью и генерирует детальные отчеты с инсайтами и рекомендациями.

**Возможности:**
- Анализ транскриптов интервью
- Генерация инсайтов и рекомендаций
- Создание детальных отчетов
- Поддержка брифа исследования
""")

st.sidebar.header("🔧 Техническая информация")
st.sidebar.code(f"""
Версия: 24.0
Загружено файлов: {len(uploaded_files) if uploaded_files else 0}
Бриф: {'✅' if uploaded_brief else '❌'}
""")
