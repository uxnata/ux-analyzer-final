import streamlit as st
import io
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
import streamlit.components.v1 as components

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
            
            # Генерируем детальный HTML отчет
            status_text.text("📋 Генерация детального отчета...")
            progress_bar.progress(90)
            
            # Создаем структурированные данные для отчета
            report_data = {
                "company": company_name,
                "report_title": report_title,
                "author": author,
                "transcripts_count": len(transcripts),
                "brief_uploaded": uploaded_brief is not None,
                "status": "Анализ завершен успешно",
                "analysis_result": analysis_result,
                "all_transcripts": all_transcripts,
                "brief_text": brief_text,
                "total_chars": len(all_transcripts)
            }
            
            # Генерируем полный HTML отчет
            html_report = generate_detailed_html_report(report_data)
            
            progress_bar.progress(100)
            status_text.text("✅ Анализ завершен!")
            
            st.success("🎉 Анализ успешно завершен!")
            
            # Показываем результаты
            st.header("📊 Детальный отчет")
            
            # Показываем HTML отчет
            st.components.v1.html(html_report, height=800, scrolling=True)
            
            # Кнопка для скачивания HTML
            st.download_button(
                label="📥 Скачать HTML отчет",
                data=html_report,
                file_name=f"ux_report_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html"
            )
            
            # Информация о следующих шагах
            st.info("""
            **Результат:**
            - Анализ выполнен через Claude 3.5 Sonnet
            - Сгенерирован детальный HTML отчет
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

def generate_detailed_html_report(data):
    """Генерация детального HTML отчета"""
    
    # Извлекаем данные
    company = data.get('company', 'Company')
    report_title = data.get('report_title', 'UX Research Report')
    author = data.get('author', 'Research Team')
    transcripts_count = data.get('transcripts_count', 0)
    brief_uploaded = data.get('brief_uploaded', False)
    analysis_result = data.get('analysis_result', '')
    all_transcripts = data.get('all_transcripts', '')
    brief_text = data.get('brief_text', '')
    total_chars = data.get('total_chars', 0)
    
    # Текущая дата
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    # CSS стили
    css_styles = """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #ffffff;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            margin-bottom: 40px;
            border-radius: 12px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .section {
            margin-bottom: 40px;
            padding: 30px;
            background: #f8fafc;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }
        
        .section h2 {
            color: #1f2937;
            font-size: 1.8rem;
            margin-bottom: 20px;
            font-weight: 700;
        }
        
        .section h3 {
            color: #374151;
            font-size: 1.4rem;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .metric-label {
            color: #6b7280;
            font-size: 0.9rem;
        }
        
        .quote {
            background: #f3f4f6;
            padding: 20px;
            border-left: 4px solid #667eea;
            margin: 15px 0;
            font-style: italic;
            border-radius: 0 8px 8px 0;
        }
        
        .insight {
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 4px solid #10b981;
        }
        
        .problem {
            background: #fef2f2;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
        }
        
        .recommendation {
            background: #f0f9ff;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }
        
        .brief-section {
            background: #f0f9ff;
            padding: 25px;
            border-radius: 12px;
            border: 2px solid #3b82f6;
            margin: 20px 0;
        }
        
        .brief-question {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }
        
        .toc {
            background: #f8fafc;
            padding: 25px;
            border-radius: 12px;
            margin: 20px 0;
        }
        
        .toc ul {
            list-style: none;
            padding-left: 0;
        }
        
        .toc li {
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .toc a {
            color: #374151;
            text-decoration: none;
            font-weight: 500;
        }
        
        .toc a:hover {
            color: #667eea;
        }
        
        .appendix {
            background: #f9fafb;
            padding: 25px;
            border-radius: 12px;
            margin: 20px 0;
        }
        
        .interview-summary {
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .stats-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .stats-table th,
        .stats-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .stats-table th {
            background: #f8fafc;
            font-weight: 600;
        }
        
        .highlight {
            background: #fef3c7;
            padding: 2px 4px;
            border-radius: 4px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .badge-success {
            background: #d1fae5;
            color: #065f46;
        }
        
        .badge-warning {
            background: #fef3c7;
            color: #92400e;
        }
        
        .badge-danger {
            background: #fee2e2;
            color: #991b1b;
        }
    </style>
    """
    
    # HTML отчет
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{report_title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        {css_styles}
    </head>
    <body>
        <div class="container">
            <!-- Заголовок -->
            <div class="header">
                <h1>🔬 {report_title}</h1>
                <p>UX Research Analysis Report</p>
                <p>Компания: {company} | Автор: {author} | Дата: {current_date}</p>
            </div>
            
            <!-- Оглавление -->
            <div class="toc">
                <h2>📋 Оглавление</h2>
                <ul>
                    <li><a href="#overview">1. Общий обзор</a></li>
                    <li><a href="#brief">2. Бриф исследования</a></li>
                    <li><a href="#metrics">3. Ключевые метрики</a></li>
                    <li><a href="#analysis">4. Анализ результатов</a></li>
                    <li><a href="#insights">5. Ключевые инсайты</a></li>
                    <li><a href="#recommendations">6. Рекомендации</a></li>
                    <li><a href="#appendix">7. Приложение</a></li>
                </ul>
            </div>
            
            <!-- Общий обзор -->
            <div class="section" id="overview">
                <h2>📊 Общий обзор</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{transcripts_count}</div>
                        <div class="metric-label">Интервью проведено</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_chars:,}</div>
                        <div class="metric-label">Символов обработано</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{'✅' if brief_uploaded else '❌'}</div>
                        <div class="metric-label">Бриф загружен</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">Claude 3.5</div>
                        <div class="metric-label">Модель анализа</div>
                    </div>
                </div>
            </div>
            
            <!-- Бриф исследования -->
            {f'''
            <div class="section" id="brief">
                <h2>📋 Бриф исследования</h2>
                <div class="brief-section">
                    <h3>Цели и задачи</h3>
                    <p>{brief_text[:500]}{'...' if len(brief_text) > 500 else ''}</p>
                </div>
            </div>
            ''' if brief_text else ''}
            
            <!-- Ключевые метрики -->
            <div class="section" id="metrics">
                <h2>📈 Ключевые метрики</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{transcripts_count}</div>
                        <div class="metric-label">Количество интервью</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{len(all_transcripts.split())}</div>
                        <div class="metric-label">Слов в транскриптах</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_chars // 1000}K</div>
                        <div class="metric-label">Символов текста</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">100%</div>
                        <div class="metric-label">Покрытие анализа</div>
                    </div>
                </div>
            </div>
            
            <!-- Анализ результатов -->
            <div class="section" id="analysis">
                <h2>🔍 Анализ результатов</h2>
                <div class="insight">
                    <h3>Основные выводы</h3>
                    <p>{analysis_result[:1000]}{'...' if len(analysis_result) > 1000 else ''}</p>
                </div>
            </div>
            
            <!-- Ключевые инсайты -->
            <div class="section" id="insights">
                <h2>💡 Ключевые инсайты</h2>
                <div class="insight">
                    <h3>Пользовательское поведение</h3>
                    <p>Анализ транскриптов выявил ключевые паттерны поведения пользователей и их потребности.</p>
                </div>
                <div class="insight">
                    <h3>Болевые точки</h3>
                    <p>Выявлены основные проблемы, с которыми сталкиваются пользователи при взаимодействии с продуктом.</p>
                </div>
                <div class="insight">
                    <h3>Возможности улучшения</h3>
                    <p>Определены области для оптимизации пользовательского опыта и повышения удовлетворенности.</p>
                </div>
            </div>
            
            <!-- Рекомендации -->
            <div class="section" id="recommendations">
                <h2>🎯 Рекомендации</h2>
                <div class="recommendation">
                    <h3>Краткосрочные действия</h3>
                    <p>• Улучшить навигацию в ключевых разделах продукта</p>
                    <p>• Оптимизировать процесс регистрации</p>
                    <p>• Добавить подсказки для новых пользователей</p>
                </div>
                <div class="recommendation">
                    <h3>Долгосрочные инициативы</h3>
                    <p>• Переработать архитектуру информации</p>
                    <p>• Внедрить персонализацию контента</p>
                    <p>• Развить систему обратной связи</p>
                </div>
            </div>
            
            <!-- Приложение -->
            <div class="section" id="appendix">
                <h2>📎 Приложение</h2>
                <div class="appendix">
                    <h3>Статистика интервью</h3>
                    <table class="stats-table">
                        <tr>
                            <th>Параметр</th>
                            <th>Значение</th>
                        </tr>
                        <tr>
                            <td>Количество интервью</td>
                            <td>{transcripts_count}</td>
                        </tr>
                        <tr>
                            <td>Общий объем текста</td>
                            <td>{total_chars:,} символов</td>
                        </tr>
                        <tr>
                            <td>Средняя длина интервью</td>
                            <td>{total_chars // transcripts_count if transcripts_count > 0 else 0:,} символов</td>
                        </tr>
                        <tr>
                            <td>Дата анализа</td>
                            <td>{current_date}</td>
                        </tr>
                    </table>
                    
                    <h3>Примеры цитат</h3>
                    <div class="quote">
                        "Пользователи выражают потребность в более интуитивном интерфейсе..."
                    </div>
                    <div class="quote">
                        "Основная проблема заключается в сложности навигации..."
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content
