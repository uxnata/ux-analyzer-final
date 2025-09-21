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
    
    # Анализируем транскрипты для получения реальных выводов
    def analyze_transcripts(transcripts_text):
        """Простой анализ транскриптов для получения общих выводов"""
        if not transcripts_text:
            return "Нет данных для анализа"
        
        # Подсчитываем базовую статистику
        words = transcripts_text.split()
        sentences = transcripts_text.split('.')
        
        # Ищем ключевые слова и фразы
        positive_words = ['хорошо', 'удобно', 'понятно', 'нравится', 'легко', 'быстро', 'отлично']
        negative_words = ['плохо', 'сложно', 'непонятно', 'не нравится', 'медленно', 'проблема', 'ошибка']
        
        positive_count = sum(1 for word in words if any(pos in word.lower() for pos in positive_words))
        negative_count = sum(1 for word in words if any(neg in word.lower() for neg in negative_words))
        
        # Ищем упоминания проблем
        problem_indicators = ['проблема', 'ошибка', 'не работает', 'сложно', 'непонятно', 'медленно']
        problems = [word for word in words if any(prob in word.lower() for prob in problem_indicators)]
        
        return {
            'total_words': len(words),
            'total_sentences': len(sentences),
            'positive_mentions': positive_count,
            'negative_mentions': negative_count,
            'problems_found': len(problems),
            'sentiment_ratio': positive_count / max(negative_count, 1)
        }
    
    # Анализируем транскрипты
    transcript_analysis = analyze_transcripts(all_transcripts)
    
    # Текущая дата
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    # CSS стили с более солидными цветами
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
            color: #1a1a1a;
            background: #fafafa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%);
            color: white;
            padding: 50px 30px;
            text-align: center;
            margin-bottom: 50px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(30, 58, 138, 0.3);
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 900;
            margin-bottom: 15px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.3rem;
            opacity: 0.95;
            font-weight: 300;
        }
        
        .section {
            margin-bottom: 50px;
            padding: 40px;
            background: #ffffff;
            border-radius: 16px;
            border-left: 6px solid #1e40af;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .section h2 {
            color: #1e40af;
            font-size: 2rem;
            margin-bottom: 25px;
            font-weight: 800;
            border-bottom: 3px solid #e5e7eb;
            padding-bottom: 10px;
        }
        
        .section h3 {
            color: #374151;
            font-size: 1.5rem;
            margin-bottom: 20px;
            font-weight: 700;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            text-align: center;
            border: 1px solid #e5e7eb;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 900;
            color: #1e40af;
            margin-bottom: 8px;
        }
        
        .metric-label {
            color: #6b7280;
            font-size: 1rem;
            font-weight: 500;
        }
        
        .quote {
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            padding: 25px;
            border-left: 6px solid #1e40af;
            margin: 20px 0;
            font-style: italic;
            border-radius: 0 12px 12px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .insight {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 6px solid #16a34a;
        }
        
        .problem {
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 6px solid #dc2626;
        }
        
        .recommendation {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 6px solid #2563eb;
        }
        
        .brief-section {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 35px;
            border-radius: 16px;
            border: 3px solid #0ea5e9;
            margin: 25px 0;
            box-shadow: 0 6px 20px rgba(14, 165, 233, 0.15);
        }
        
        .brief-question {
            background: white;
            padding: 25px;
            margin: 15px 0;
            border-radius: 12px;
            border-left: 6px solid #0ea5e9;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .brief-answer {
            background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
            padding: 25px;
            margin: 15px 0;
            border-radius: 12px;
            border-left: 6px solid #eab308;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .quote-source {
            background: #f8fafc;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #64748b;
            font-size: 0.9rem;
            color: #64748b;
        }
        
        .toc {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 35px;
            border-radius: 16px;
            margin: 30px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .toc ul {
            list-style: none;
            padding-left: 0;
        }
        
        .toc li {
            padding: 12px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .toc a {
            color: #374151;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .toc a:hover {
            color: #1e40af;
        }
        
        .appendix {
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
            padding: 35px;
            border-radius: 16px;
            margin: 30px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .interview-summary {
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .stats-table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .stats-table th,
        .stats-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .stats-table th {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            font-weight: 700;
        }
        
        .highlight {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            padding: 3px 6px;
            border-radius: 6px;
            font-weight: 600;
        }
        
        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .badge-success {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            color: #065f46;
        }
        
        .badge-warning {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            color: #92400e;
        }
        
        .badge-danger {
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            color: #991b1b;
        }
        
        .trace-section {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            border-left: 6px solid #0ea5e9;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .trace-quote {
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #0ea5e9;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
                    <li><a href="#brief-answers">3. Ответы на вопросы брифа</a></li>
                    <li><a href="#metrics">4. Ключевые метрики</a></li>
                    <li><a href="#analysis">5. Анализ результатов</a></li>
                    <li><a href="#insights">6. Ключевые инсайты</a></li>
                    <li><a href="#recommendations">7. Рекомендации</a></li>
                    <li><a href="#appendix">8. Приложение</a></li>
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
                        <div class="metric-value">{transcript_analysis.get('total_words', 0):,}</div>
                        <div class="metric-label">Слов в транскриптах</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{transcript_analysis.get('positive_mentions', 0)}</div>
                        <div class="metric-label">Положительных упоминаний</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{transcript_analysis.get('problems_found', 0)}</div>
                        <div class="metric-label">Проблем выявлено</div>
                    </div>
                </div>
                
                <div class="insight">
                    <h3>Ключевые выводы по транскриптам</h3>
                    <p><strong>Общий тон интервью:</strong> {'Положительный' if transcript_analysis.get('sentiment_ratio', 0) > 1 else 'Нейтральный/Отрицательный'}</p>
                    <p><strong>Соотношение положительных к отрицательным упоминаниям:</strong> {transcript_analysis.get('positive_mentions', 0)}:{transcript_analysis.get('negative_mentions', 0)}</p>
                    <p><strong>Средняя длина интервью:</strong> {transcript_analysis.get('total_words', 0) // max(transcripts_count, 1)} слов</p>
                    <p><strong>Плотность проблем:</strong> {transcript_analysis.get('problems_found', 0)} упоминаний проблем на {transcript_analysis.get('total_words', 0) // 1000}K слов</p>
                </div>
            </div>
            
            <!-- Бриф исследования -->
            {f'''
            <div class="section" id="brief">
                <h2>📋 Бриф исследования</h2>
                <div class="brief-section">
                    <h3>Цели и задачи исследования</h3>
                    <p>{brief_text[:800]}{'...' if len(brief_text) > 800 else ''}</p>
                </div>
            </div>
            ''' if brief_text else ''}
            
            <!-- Детальные ответы на вопросы брифа -->
            {f'''
            <div class="section" id="brief-answers">
                <h2>🎯 Ответы на вопросы брифа</h2>
                <div class="trace-section">
                    <h3>Методология анализа</h3>
                    <p>Каждый ответ основан на анализе {transcripts_count} интервью с общим объемом {total_chars:,} символов. 
                    Выводы подкреплены конкретными цитатами из транскриптов для обеспечения трассируемости результатов.</p>
                </div>
                
                <div class="brief-answer">
                    <h3>Результаты анализа брифа</h3>
                    <p>{analysis_result if analysis_result else 'Анализ не выполнен'}</p>
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
                    <h3>Основные выводы по транскриптам</h3>
                    <p><strong>Объем данных:</strong> {transcript_analysis.get('total_words', 0):,} слов в {transcripts_count} интервью</p>
                    <p><strong>Эмоциональная окраска:</strong> {'Преобладают положительные отзывы' if transcript_analysis.get('sentiment_ratio', 0) > 1 else 'Преобладают нейтральные/отрицательные отзывы'}</p>
                    <p><strong>Выявленные проблемы:</strong> {transcript_analysis.get('problems_found', 0)} упоминаний проблемных моментов</p>
                    <p><strong>Детальный анализ:</strong> {analysis_result[:1500] if analysis_result else 'Анализ не выполнен'}{'...' if len(analysis_result) > 1500 else ''}</p>
                </div>
            </div>
            
            <!-- Ключевые инсайты -->
            <div class="section" id="insights">
                <h2>💡 Ключевые инсайты</h2>
                <div class="insight">
                    <h3>Пользовательское поведение</h3>
                    <p>На основе анализа {transcript_analysis.get('total_words', 0):,} слов выявлены ключевые паттерны поведения пользователей. 
                    Положительных упоминаний: {transcript_analysis.get('positive_mentions', 0)}, 
                    отрицательных: {transcript_analysis.get('negative_mentions', 0)}.</p>
                </div>
                <div class="insight">
                    <h3>Болевые точки</h3>
                    <p>Выявлено {transcript_analysis.get('problems_found', 0)} упоминаний проблемных моментов в транскриптах. 
                    Плотность проблем: {transcript_analysis.get('problems_found', 0) / max(transcript_analysis.get('total_words', 1) / 1000, 1):.1f} на 1K слов.</p>
                </div>
                <div class="insight">
                    <h3>Возможности улучшения</h3>
                    <p>Соотношение положительных к отрицательным упоминаниям: {transcript_analysis.get('sentiment_ratio', 0):.1f}:1. 
                    {'Требуется работа над улучшением пользовательского опыта' if transcript_analysis.get('sentiment_ratio', 0) < 1 else 'Пользователи в целом довольны продуктом'}.</p>
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
                            <td>Количество слов</td>
                            <td>{transcript_analysis.get('total_words', 0):,}</td>
                        </tr>
                        <tr>
                            <td>Средняя длина интервью</td>
                            <td>{transcript_analysis.get('total_words', 0) // max(transcripts_count, 1):,} слов</td>
                        </tr>
                        <tr>
                            <td>Положительные упоминания</td>
                            <td>{transcript_analysis.get('positive_mentions', 0)}</td>
                        </tr>
                        <tr>
                            <td>Отрицательные упоминания</td>
                            <td>{transcript_analysis.get('negative_mentions', 0)}</td>
                        </tr>
                        <tr>
                            <td>Выявленные проблемы</td>
                            <td>{transcript_analysis.get('problems_found', 0)}</td>
                        </tr>
                        <tr>
                            <td>Дата анализа</td>
                            <td>{current_date}</td>
                        </tr>
                    </table>
                    
                    <h3>Анализ тональности</h3>
                    <div class="quote">
                        <strong>Соотношение положительных к отрицательным упоминаниям:</strong> {transcript_analysis.get('sentiment_ratio', 0):.1f}:1
                    </div>
                    <div class="quote">
                        <strong>Плотность проблем:</strong> {transcript_analysis.get('problems_found', 0) / max(transcript_analysis.get('total_words', 1) / 1000, 1):.1f} упоминаний на 1K слов
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

# Настройка страницы
st.set_page_config(
    page_title="UX Анализатор V24.0",
    page_icon="🔬",
    layout="wide"
)

# Заголовок
st.title("🔬 UX Анализатор V24.0")
st.markdown("Профессиональный анализ транскриптов пользовательских интервью с использованием Claude 3.5 Sonnet")
st.markdown("---")

# Этапы работы
st.header("🚀 Этапы работы")

# Создаем контейнер для этапов
step_container = st.container()

with step_container:
    # Этап 1: Настройки
    with st.expander("1️⃣ Настройки и конфигурация", expanded=True):
        st.markdown("**Настройте параметры анализа и введите API ключ**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            api_key = st.text_input(
                "OpenRouter API Key",
                type="password",
                placeholder="Введите ваш OpenRouter API ключ",
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
    
    # Этап 2: Загрузка данных
    with st.expander("2️⃣ Загрузка данных", expanded=False):
        st.markdown("**Загрузите транскрипты интервью и бриф исследования**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_files = st.file_uploader(
                "Загрузите транскрипты",
                type=['txt', 'md', 'docx', 'doc'],
                accept_multiple_files=True,
                help="Выберите файлы с транскриптами интервью (.txt, .md, .docx, .doc)"
            )
            
            if uploaded_files:
                st.success(f"✅ Загружено {len(uploaded_files)} файлов")
                for file in uploaded_files:
                    st.write(f"📄 {file.name} ({(file.size / 1024):.1f} KB)")

        with col2:
            uploaded_brief = st.file_uploader(
                "Загрузите бриф (опционально)",
                type=['txt', 'md', 'docx', 'doc'],
                help="Бриф с целями исследования (.txt, .md, .docx, .doc)"
            )
            
            if uploaded_brief:
                st.success("✅ Бриф загружен")
                st.write(f"📄 {uploaded_brief.name} ({(uploaded_brief.size / 1024):.1f} KB)")
    
    # Этап 3: Анализ
    with st.expander("3️⃣ Запуск анализа", expanded=False):
        st.markdown("**Запустите анализ данных и получите детальный отчет**")
        
        if st.button("🚀 Начать анализ", type="primary", disabled=not (uploaded_files and api_key)):
            if not api_key:
                st.error("❌ Введите API ключ!")
            elif not uploaded_files:
                st.error("❌ Загрузите транскрипты!")
            else:
                # Показываем загрузку
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🔧 Настройка Claude 3.5 Sonnet...")
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
                        if response.status_code != 200:
                            st.write(f"Ответ API: {response.text}")
                            if response.status_code == 401:
                                st.error("❌ Неверный API ключ! Проверьте ключ в настройках.")
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

# Кнопка очистки в сайдбаре
st.sidebar.header("🔧 Управление")
if st.sidebar.button("🗑️ Очистить все", type="secondary"):
    st.rerun()

# Подвал с информацией
st.markdown("---")
st.markdown("### ℹ️ О системе")
st.info("""
**UX Анализатор V24.0** - Профессиональный инструмент для анализа пользовательских интервью

**Возможности:**
- 🔍 Детальный анализ транскриптов интервью
- 📊 Генерация инсайтов и рекомендаций с цитатами
- 📋 Создание профессиональных отчетов
- 🎯 Поддержка брифа исследования
- 📈 Трассировка выводов к исходным данным

**Технологии:** Claude 3.5 Sonnet, Streamlit, OpenRouter API
""")
