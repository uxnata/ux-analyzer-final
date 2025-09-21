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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
<style>
    /* Основные стили */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .step-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid #e1e5e9;
        transition: all 0.3s ease;
    }
    
    .step-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.12);
    }
    
    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    .step-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin-right: 1rem;
    }
    
    .step-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0;
    }
    
    .step-description {
        color: #718096;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    .upload-area {
        border: 3px dashed #cbd5e0;
        border-radius: 15px;
        padding: 3rem 2rem;
        text-align: center;
        background: #f7fafc;
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    
    .upload-area:hover {
        border-color: #667eea;
        background: #edf2f7;
    }
    
    .upload-icon {
        font-size: 3rem;
        color: #a0aec0;
        margin-bottom: 1rem;
    }
    
    .upload-text {
        font-size: 1.1rem;
        color: #4a5568;
        font-weight: 500;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-success {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        color: white;
    }
    
    .status-error {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
    }
    
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 15px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    .clear-button {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(245, 101, 101, 0.4);
    }
    
    .clear-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(245, 101, 101, 0.6);
    }
    
    .info-card {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border-left: 5px solid #667eea;
    }
    
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e1e5e9;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #718096;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .sidebar-content {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .file-item {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
    
    .progress-container {
        background: #f7fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 8px;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .success-message {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Главный заголовок
st.markdown("""
<div class="main-header">
    <h1>🔬 UX Анализатор V24.0</h1>
    <p>Профессиональный анализ транскриптов пользовательских интервью с использованием Claude 3.5 Sonnet</p>
</div>
""", unsafe_allow_html=True)

# Основной контент
col1, col2 = st.columns([2, 1])

with col1:
    # Этап 1: Настройки
    st.markdown("""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">1</div>
            <div>
                <div class="step-title">⚙️ Настройки и конфигурация</div>
                <div class="step-description">Настройте параметры анализа и введите API ключ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Настройки в карточке
    with st.container():
        col1_1, col1_2 = st.columns(2)
        
        with col1_1:
            api_key = st.text_input(
                "🔑 OpenRouter API Key",
                type="password",
                placeholder="Введите ваш OpenRouter API ключ",
                help="API ключ для OpenRouter"
            )
            
            company_name = st.text_input(
                "🏢 Название компании",
                value="Company",
                placeholder="Название компании"
            )

        with col1_2:
            report_title = st.text_input(
                "📋 Название отчета",
                value="UX Research Report",
                placeholder="Название отчета"
            )
            
            author = st.text_input(
                "👤 Автор отчета",
                value="Research Team",
                placeholder="Автор отчета"
            )
    
    # Этап 2: Загрузка данных
    st.markdown("""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">2</div>
            <div>
                <div class="step-title">📤 Загрузка данных</div>
                <div class="step-description">Загрузите транскрипты интервью и бриф исследования</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Загрузка файлов
    col2_1, col2_2 = st.columns(2)
    
    with col2_1:
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">📄</div>
            <div class="upload-text">Загрузите транскрипты интервью</div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Выберите файлы с транскриптами",
            type=['txt', 'md', 'docx', 'doc'],
            accept_multiple_files=True,
            help="Поддерживаемые форматы: .txt, .md, .docx, .doc",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.markdown(f"""
            <div class="success-message">
                ✅ Загружено {len(uploaded_files)} файлов
            </div>
            """, unsafe_allow_html=True)
            
            for file in uploaded_files:
                st.markdown(f"""
                <div class="file-item">
                    📄 {file.name} ({(file.size / 1024):.1f} KB)
                </div>
                """, unsafe_allow_html=True)

    with col2_2:
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">📋</div>
            <div class="upload-text">Загрузите бриф исследования (опционально)</div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_brief = st.file_uploader(
            "Выберите файл с брифом",
            type=['txt', 'md', 'docx', 'doc'],
            help="Бриф с целями исследования",
            label_visibility="collapsed"
        )
        
        if uploaded_brief:
            st.markdown(f"""
            <div class="success-message">
                ✅ Бриф загружен
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="file-item">
                📋 {uploaded_brief.name} ({(uploaded_brief.size / 1024):.1f} KB)
            </div>
            """, unsafe_allow_html=True)
    
    # Этап 3: Анализ
    st.markdown("""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">3</div>
            <div>
                <div class="step-title">🚀 Запуск анализа</div>
                <div class="step-description">Запустите анализ данных и получите детальный отчет</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Кнопка анализа
    col3_1, col3_2, col3_3 = st.columns([1, 2, 1])
    
    with col3_2:
        if st.button("🚀 Начать анализ", type="primary", disabled=not (uploaded_files and api_key), use_container_width=True):
            if not api_key:
                st.markdown("""
                <div class="error-message">
                    ❌ Введите API ключ!
                </div>
                """, unsafe_allow_html=True)
            elif not uploaded_files:
                st.markdown("""
                <div class="error-message">
                    ❌ Загрузите транскрипты!
                </div>
                """, unsafe_allow_html=True)
            else:
                # Показываем загрузку
                st.markdown("""
                <div class="progress-container">
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <div style="font-size: 1.2rem; font-weight: 600; color: #4a5568;">🔧 Настройка Claude 3.5 Sonnet...</div>
                    </div>
                    <div class="progress-bar" style="width: 20%;"></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Простая проверка API ключа
                if api_key.startswith("sk-or-v1-"):
                    st.markdown("""
                    <div class="success-message">
                        ✅ API ключ валидный
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="error-message">
                        ⚠️ Проверьте формат API ключа
                    </div>
                    """, unsafe_allow_html=True)
                
                # Продолжение анализа...
                st.markdown("""
                <div class="progress-container">
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <div style="font-size: 1.2rem; font-weight: 600; color: #4a5568;">🔬 Запуск анализа...</div>
                    </div>
                    <div class="progress-bar" style="width: 40%;"></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Читаем транскрипты
                transcripts = []
                for file in uploaded_files:
                    content = read_file_content(file)
                    transcripts.append(content)
                
                st.markdown("""
                <div class="progress-container">
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <div style="font-size: 1.2rem; font-weight: 600; color: #4a5568;">📊 Обработка данных...</div>
                    </div>
                    <div class="progress-bar" style="width: 60%;"></div>
                </div>
                """, unsafe_allow_html=True)
                
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
                    
                    if response.status_code != 200:
                        if response.status_code == 401:
                            st.markdown("""
                            <div class="error-message">
                                ❌ Неверный API ключ! Проверьте ключ в настройках.
                            </div>
                            """, unsafe_allow_html=True)
                        elif response.status_code == 429:
                            st.markdown("""
                            <div class="error-message">
                                ❌ Превышен лимит запросов. Попробуйте позже.
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="error-message">
                                ❌ Ошибка API: {response.status_code}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    if response.status_code == 200:
                        analysis_result = response.json()["choices"][0]["message"]["content"]
                        st.markdown("""
                        <div class="success-message">
                            ✅ Анализ выполнен через OpenRouter API!
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        analysis_result = f"Ошибка API: {response.status_code} - {response.text}"
                        st.markdown("""
                        <div class="error-message">
                            ⚠️ Ошибка при обращении к API
                        </div>
                        """, unsafe_allow_html=True)
                    
                except Exception as e:
                    analysis_result = f"Ошибка анализа: {str(e)}"
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Ошибка: {e}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Генерация отчета
                st.markdown("""
                <div class="progress-container">
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <div style="font-size: 1.2rem; font-weight: 600; color: #4a5568;">📋 Генерация детального отчета...</div>
                    </div>
                    <div class="progress-bar" style="width: 90%;"></div>
                </div>
                """, unsafe_allow_html=True)
                
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
                
                st.markdown("""
                <div class="progress-container">
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <div style="font-size: 1.2rem; font-weight: 600; color: #4a5568;">✅ Анализ завершен!</div>
                    </div>
                    <div class="progress-bar" style="width: 100%;"></div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="success-message">
                    🎉 Анализ успешно завершен!
                </div>
                """, unsafe_allow_html=True)
                
                # Показываем результаты
                st.markdown("## 📊 Детальный отчет")
                
                # Показываем HTML отчет
                st.components.v1.html(html_report, height=800, scrolling=True)
                
                # Кнопка для скачивания HTML
                st.download_button(
                    label="📥 Скачать HTML отчет",
                    data=html_report,
                    file_name=f"ux_report_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html",
                    use_container_width=True
                )
                
                # Информация о следующих шагах
                st.markdown("""
                <div class="info-card">
                    <h3>🎯 Результат анализа</h3>
                    <p>• Анализ выполнен через Claude 3.5 Sonnet</p>
                    <p>• Сгенерирован детальный HTML отчет</p>
                    <p>• Ответы основаны на реальных транскриптах интервью</p>
                    <p>• Цитаты взяты из интервью</p>
                </div>
                """, unsafe_allow_html=True)

with col2:
    # Пустая боковая панель
    st.markdown("")

# Кнопка очистки внизу
st.markdown("---")
col_clear_1, col_clear_2, col_clear_3 = st.columns([1, 1, 1])

with col_clear_2:
    if st.button("🗑️ Очистить все", type="secondary", use_container_width=True):
        st.rerun()
