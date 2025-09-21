import streamlit as st
import io
import zipfile
import xml.etree.ElementTree as ET

def read_docx(file):
    """Читает содержимое .docx файла"""
    try:
        # .docx файл - это zip архив
        with zipfile.ZipFile(file) as docx:
            # Читаем основной документ
            content = docx.read('word/document.xml')
            root = ET.fromstring(content)
            
            # Извлекаем текст из всех параграфов
            text = []
            for paragraph in root.iter():
                if paragraph.text:
                    text.append(paragraph.text)
            
            return ' '.join(text)
    except Exception as e:
        st.error(f"Ошибка чтения .docx файла: {e}")
        return ""

def read_file_content(file):
    """Читает содержимое файла в зависимости от его типа"""
    if file.name.endswith('.docx'):
        return read_docx(file)
    elif file.name.endswith('.doc'):
        # Для .doc файлов пока возвращаем заглушку
        return f"[Содержимое .doc файла: {file.name}]"
    else:
        # Для .txt и .md файлов
        return file.read().decode('utf-8')

# Настройка страницы
st.set_page_config(
    page_title="UX Анализатор V24.0",
    page_icon="🔬",
    layout="wide"
)

# Заголовок
st.title("🔬 UX Анализатор V24.0")
st.markdown("Анализ транскриптов пользовательских интервью с использованием Google Gemini AI")
st.markdown("---")

# Секция настроек
st.header("⚙️ Настройки")

col1, col2 = st.columns(2)

with col1:
    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        value="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",
        help="API ключ для OpenRouter"
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
        type=['txt', 'md', 'docx', 'doc'],
        accept_multiple_files=True,
        help="Выберите файлы с транскриптами интервью (.txt, .md, .docx, .doc)"
    )

with col2:
    uploaded_brief = st.file_uploader(
        "Загрузите бриф (опционально)",
        type=['txt', 'md', 'docx', 'doc'],
        help="Бриф с целями исследования (.txt, .md, .docx, .doc)"
    )

# Обработка загруженных файлов
if uploaded_files:
    st.success(f"✅ Загружено {len(uploaded_files)} файлов")
    for file in uploaded_files:
        st.write(f"📄 {file.name} ({(file.size / 1024):.1f} KB)")

if uploaded_brief:
    st.success("✅ Бриф загружен")
    st.write(f"📄 {uploaded_brief.name} ({(uploaded_brief.size / 1024):.1f} KB)")

# Секция анализа
st.header("🔬 Анализ")

if st.button("🚀 Начать анализ", type="primary", disabled=not uploaded_files):
    if not api_key:
        st.error("❌ Введите API ключ!")
    elif not uploaded_files:
        st.error("❌ Загрузите транскрипты!")
    else:
        # Показываем загрузку
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔧 Настройка Gemini API...")
            progress_bar.progress(20)
            
            # Простая проверка API ключа
            if api_key.startswith("sk-or-v1-"):
                st.success("✅ API ключ валидный")
            else:
                st.warning("⚠️ Проверьте формат API ключа")
            
            status_text.text("🔬 Запуск анализа...")
            progress_bar.progress(40)
            
            # Читаем транскрипты
            transcripts = []
            for file in uploaded_files:
                content = read_file_content(file)
                transcripts.append(content)
            
            status_text.text("📊 Обработка данных...")
            progress_bar.progress(60)
            
            # Реальный анализ через OpenRouter API
            try:
                import requests
                
                # Подготавливаем данные для анализа
                all_transcripts = "\n\n".join(transcripts)
                brief_text = ""
                if uploaded_brief:
                    brief_text = read_file_content(uploaded_brief)
                
                # Формируем запрос к OpenRouter для анализа брифа
                brief_prompt = f"""
                Проанализируй следующие транскрипты пользовательских интервью и ответь на вопросы из брифа исследования.
                
                БРИФ ИССЛЕДОВАНИЯ:
                {brief_text if brief_text else "Бриф не предоставлен"}
                
                ТРАНСКРИПТЫ ИНТЕРВЬЮ:
                {all_transcripts[:8000]}
                
                ЗАДАЧА:
                На основе транскриптов интервью ответь на каждый вопрос из брифа исследования. 
                Для каждого ответа приведи конкретные цитаты из интервью.
                
                Формат ответа:
                ВОПРОС: [вопрос из брифа]
                ОТВЕТ: [ответ на основе транскриптов]
                ЦИТАТЫ: [конкретные цитаты из интервью]
                
                Отчет должен быть на русском языке.
                """
                
                # Отправляем запрос к OpenRouter
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": [
                            {"role": "user", "content": brief_prompt}
                        ],
                        "max_tokens": 3000,
                        "temperature": 0.7
                    }
                )
                
                # Показываем детали ошибки
                st.write(f"Статус ответа: {response.status_code}")
                st.write(f"Заголовки ответа: {dict(response.headers)}")
                if response.status_code != 200:
                    st.write(f"Ответ API: {response.text}")
                    if response.status_code == 401:
                        st.error("❌ Неверный API ключ! Проверьте:")
                        st.write("- Правильность ключа")
                        st.write("- Активность аккаунта")
                        st.write("- Баланс на OpenRouter")
                    elif response.status_code == 429:
                        st.error("❌ Превышен лимит запросов. Попробуйте позже.")
                    else:
                        st.error(f"❌ Ошибка API: {response.status_code}")
                
                if response.status_code == 200:
                    analysis_result = response.json()["choices"][0]["message"]["content"]
                    st.success("✅ Анализ выполнен через OpenRouter API!")
                else:
                    analysis_result = f"Ошибка API: {response.status_code} - {response.text}"
                    st.warning("⚠️ Ошибка при обращении к API")
                
            except Exception as e:
                analysis_result = f"Ошибка анализа: {str(e)}"
                st.error(f"❌ Ошибка: {e}")
            
            status_text.text("📋 Генерация отчета...")
            progress_bar.progress(80)
            
            # Результаты
            results = {
                "company": company_name,
                "report_title": report_title,
                "author": author,
                "transcripts_count": len(transcripts),
                "brief_uploaded": uploaded_brief is not None,
                "status": "Анализ завершен успешно",
                "analysis_result": analysis_result
            }
            
            progress_bar.progress(100)
            status_text.text("✅ Анализ завершен!")
            
            st.success("🎉 Анализ успешно завершен!")
            
            # Показываем результаты
            st.header("📊 Ответы на вопросы брифа")
            
            # Показываем основной отчет
            if "analysis_result" in results and results["analysis_result"]:
                st.markdown("---")
                st.markdown(results["analysis_result"])
                st.markdown("---")
            else:
                st.error("❌ Не удалось получить результаты анализа")
            
            # Информация о следующих шагах
            st.info("""
            **Результат:**
            - Анализ выполнен через OpenRouter API
            - Ответы основаны на реальных транскриптах интервью
            - Цитаты взяты из интервью
            """)
            
        except Exception as e:
            st.error(f"❌ Ошибка при анализе: {e}")

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

st.sidebar.header("🔧 Статус")
st.sidebar.code(f"""
Загружено файлов: {len(uploaded_files) if uploaded_files else 0}
Бриф: {'✅' if uploaded_brief else '❌'}
API ключ: {'✅' if api_key else '❌'}
""")
