import streamlit as st
import io
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
import streamlit.components.v1 as components
import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импорты наших классов
from ux_analyzer_classes import CompanyConfig, BriefManager
from ux_analyzer_core import AdvancedUXAnalyzer
from ux_report_generator import EnhancedReportGenerator

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

def analyze_transcripts(transcripts_text):
    """Детальный анализ транскриптов для получения общих выводов"""
    if not transcripts_text:
        return "Нет данных для анализа"
    
    # Подсчитываем базовую статистику
    words = transcripts_text.split()
    sentences = transcripts_text.split('.')
    
    # Расширенные списки для анализа
    positive_words = [
        'хорошо', 'удобно', 'понятно', 'нравится', 'легко', 'быстро', 'отлично', 
        'круто', 'супер', 'классно', 'замечательно', 'прекрасно', 'восхитительно',
        'интуитивно', 'просто', 'ясно', 'понятно', 'логично', 'удобно'
    ]
    
    negative_words = [
        'плохо', 'сложно', 'непонятно', 'не нравится', 'медленно', 'проблема', 
        'ошибка', 'бесит', 'раздражает', 'ужасно', 'кошмар', 'мучает', 'доводит',
        'неудобно', 'запутанно', 'сбивает', 'путает', 'сложно', 'трудно'
    ]
    
    # Анализ эмоциональной окраски
    positive_count = sum(1 for word in words if any(pos in word.lower() for pos in positive_words))
    negative_count = sum(1 for word in words if any(neg in word.lower() for neg in negative_words))
    
    # Детальный анализ проблем
    problem_indicators = [
        'проблема', 'ошибка', 'не работает', 'сложно', 'непонятно', 'медленно', 
        'бесит', 'раздражает', 'ужасно', 'кошмар', 'мучает', 'доводит', 'сбивает',
        'неудобно', 'запутанно', 'путает', 'трудно', 'глючит', 'тормозит'
    ]
    
    problems = [word for word in words if any(prob in word.lower() for prob in problem_indicators)]
    
    # Конкретные проблемы с контекстом
    specific_problems = []
    problem_patterns = [
        'не работает', 'не загружается', 'глючит', 'тормозит', 'вылетает',
        'сложно найти', 'непонятно как', 'неудобно', 'не интуитивно',
        'медленно', 'долго', 'зависает', 'ошибка', 'сбой', 'не открывается',
        'не сохраняется', 'теряется', 'исчезает', 'не отображается'
    ]
    
    for pattern in problem_patterns:
        if pattern in transcripts_text.lower():
            specific_problems.append(pattern)
    
    # Положительные моменты
    positive_patterns = [
        'удобно', 'понятно', 'быстро', 'легко', 'интуитивно',
        'нравится', 'круто', 'супер', 'отлично', 'классно',
        'замечательно', 'прекрасно', 'восхитительно', 'просто', 'ясно'
    ]
    
    positive_moments = []
    for pattern in positive_patterns:
        if pattern in transcripts_text.lower():
            positive_moments.append(pattern)
    
    # Анализ длительности интервью (приблизительно)
    interview_indicators = ['интервьюер', 'интервьюируемый', 'вопрос', 'ответ']
    interview_count = sum(1 for word in words if any(ind in word.lower() for ind in interview_indicators))
    
    # Анализ технических аспектов
    tech_terms = ['приложение', 'сайт', 'интерфейс', 'кнопка', 'меню', 'форма', 'загрузка']
    tech_mentions = sum(1 for word in words if any(tech in word.lower() for tech in tech_terms))
    
    return {
        'total_words': len(words),
        'total_sentences': len(sentences),
        'positive_mentions': positive_count,
        'negative_mentions': negative_count,
        'problems_found': len(problems),
        'specific_problems': specific_problems,
        'positive_moments': positive_moments,
        'sentiment_ratio': positive_count / max(negative_count, 1),
        'interview_indicators': interview_count,
        'tech_mentions': tech_mentions,
        'problem_density': len(problems) / max(len(words) / 1000, 1),  # Проблем на 1000 слов
        'positive_density': positive_count / max(len(words) / 1000, 1)  # Положительных на 1000 слов
    }

# def generate_custom_html_report(data, selected_sections):  # УДАЛЕНО - используется EnhancedReportGenerator
    # """Генерация HTML отчета с выбранными разделами"""
    
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
    transcript_analysis = analyze_transcripts(all_transcripts)
    
    # Текущая дата
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    # CSS стили в черно-бело-серых тонах
    css_styles = """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            margin: 0; 
            padding: 0; 
            background: #ffffff;
            color: #1f2937;
            line-height: 1.6;
        }
        
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 16px; 
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            overflow: hidden;
            margin: 40px auto;
        }
        
        .header { 
            background: linear-gradient(135deg, #1f2937 0%, #374151 50%, #4b5563 100%);
            color: white; 
            padding: 60px 40px; 
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.1);
            opacity: 0.3;
        }
        
        .header h1 { 
            margin: 0; 
            font-size: 3.5em; 
            font-weight: 800; 
            letter-spacing: -0.02em;
            position: relative;
            z-index: 1;
        }
        
        .header p { 
            margin: 20px 0 0 0; 
            opacity: 0.95; 
            font-size: 1.3em;
            font-weight: 400;
            position: relative;
            z-index: 1;
        }
        
        .content { 
            padding: 60px 40px; 
        }
        
        .section { 
            margin-bottom: 50px; 
        }
        
        .section h2 { 
            font-size: 2.2em; 
            font-weight: 700; 
            color: #1f2937; 
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #1f2937;
            position: relative;
        }
        
        .section h2::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 60px;
            height: 3px;
            background: #1f2937;
            border-radius: 2px;
        }
        
        .toc {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 40px;
        }
        
        .toc h2 {
            color: #1f2937;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .toc ul {
            list-style: none;
            padding: 0;
        }
        
        .toc li {
            margin-bottom: 10px;
        }
        
        .toc a {
            color: #4b5563;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }
        
        .toc a:hover {
            color: #1f2937;
        }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
        }
        
        .insight {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 30px;
        }
        
        .quote-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #6b7280;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .quote-text {
            font-style: italic;
            color: #4b5563;
            line-height: 1.6;
            margin: 0;
        }
        
        .persona-card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            border: 2px solid #e5e7eb;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .persona-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .persona-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #6b7280;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            margin-right: 20px;
        }
        
        .persona-name {
            font-size: 1.5em;
            font-weight: 700;
            color: #1f2937;
            margin: 0;
        }
        
        .persona-role {
            color: #6b7280;
            font-size: 0.9em;
            margin: 5px 0 0 0;
        }
        
        .persona-section {
            margin-bottom: 20px;
        }
        
        .persona-section h4 {
            color: #1f2937;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .persona-section ul {
            margin: 0;
            padding-left: 20px;
            color: #4b5563;
        }
        
        .persona-section li {
            margin-bottom: 5px;
        }
        
        .persona-quotes {
            background: #f9fafb;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }
        
        .persona-quotes h4 {
            color: #1f2937;
            margin-bottom: 15px;
        }
        
        .persona-quote {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 3px solid #6b7280;
            font-style: italic;
            color: #4b5563;
        }
        
        .recommendation {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 30px;
        }
        
        .recommendation h3 {
            color: #1f2937;
            margin-bottom: 20px;
            font-size: 1.3em;
        }
        
        .recommendation p {
            color: #4b5563;
            margin-bottom: 10px;
            line-height: 1.6;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            border: 1px solid #e5e7eb;
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: 800;
            color: #1f2937;
            margin-bottom: 10px;
        }
        
        .metric-label {
            color: #6b7280;
            font-size: 1em;
            font-weight: 500;
        }
        
        .info-card {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            border-radius: 16px;
            padding: 30px;
            margin: 30px 0;
            border-left: 5px solid #6b7280;
        }
        
        .info-card h3 {
            color: #1f2937;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .info-card p {
            color: #4b5563;
            margin-bottom: 10px;
            line-height: 1.6;
        }
        
        .success-message {
            background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 12px;
            margin: 20px 0;
            font-weight: 600;
            text-align: center;
        }
        
        .error-message {
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 12px;
            margin: 20px 0;
            font-weight: 600;
            text-align: center;
        }
        
        .progress-container {
            background: #f3f4f6;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .progress-bar {
            background: linear-gradient(135deg, #1f2937 0%, #374151 50%, #4b5563 100%);
            height: 8px;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .file-item {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            border-left: 4px solid #6b7280;
        }
        
        .sidebar-content {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .step-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
        }
        
        .step-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
        }
        
        .step-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f3f4f6;
        }
        
        .step-number {
            background: linear-gradient(135deg, #1f2937 0%, #374151 50%, #4b5563 100%);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: bold;
            margin-right: 15px;
        }
        
        .step-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1f2937;
            margin: 0;
        }
        
        .step-description {
            color: #6b7280;
            font-size: 1rem;
            margin: 5px 0 0 0;
        }
        
        .upload-area {
            border: 3px dashed #d1d5db;
            border-radius: 15px;
            padding: 40px 30px;
            text-align: center;
            background: #f9fafb;
            transition: all 0.3s ease;
            margin: 20px 0;
        }
        
        .upload-area:hover {
            border-color: #6b7280;
            background: #f3f4f6;
        }
        
        .upload-icon {
            font-size: 3rem;
            color: #6b7280;
            margin-bottom: 15px;
        }
        
        .upload-text {
            font-size: 1.1rem;
            color: #374151;
            font-weight: 500;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 600;
            margin: 5px;
        }
        
        .status-success {
            background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
            color: white;
        }
        
        .status-warning {
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
            color: white;
        }
        
        .status-error {
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
            color: white;
        }
        
        .action-button {
            background: linear-gradient(135deg, #1f2937 0%, #374151 50%, #4b5563 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 15px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(31, 41, 55, 0.4);
        }
        
        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(31, 41, 55, 0.6);
        }
        
        .clear-button {
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(107, 114, 128, 0.4);
        }
        
        .clear-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(107, 114, 128, 0.6);
        }
        
        .main-header {
            background: linear-gradient(135deg, #1f2937 0%, #374151 50%, #4b5563 100%);
            padding: 40px 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 30px rgba(31, 41, 55, 0.3);
        }
        
        .main-header h1 {
            font-size: 3rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-header p {
            font-size: 1.2rem;
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
    </style>
    """
    
    # Генерируем HTML отчет
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
                <h1>{report_title}</h1>
                <p>Компания: {company} | Автор: {author} | Дата: {current_date}</p>
            </div>
            
            <div class="content">
                {f'''
                <!-- Оглавление -->
                <div class="toc">
                    <h2>📋 Оглавление</h2>
                    <ul>
                        {f'<li><a href="#overview">1. Общий обзор</a></li>' if selected_sections.get('overview', False) else ''}
                        {f'<li><a href="#brief">2. Бриф исследования</a></li>' if selected_sections.get('brief', False) else ''}
                        {f'<li><a href="#brief-answers">3. Ответы на вопросы брифа</a></li>' if selected_sections.get('brief_answers', False) else ''}
                        {f'<li><a href="#analysis">4. Анализ результатов</a></li>' if selected_sections.get('analysis', False) else ''}
                        {f'<li><a href="#personas">5. Персоны пользователей</a></li>' if selected_sections.get('personas', False) else ''}
                        {f'<li><a href="#insights">6. Ключевые инсайты</a></li>' if selected_sections.get('insights', False) else ''}
                        {f'<li><a href="#pain-points">7. Болевые точки пользователей</a></li>' if selected_sections.get('pain_points', False) else ''}
                        {f'<li><a href="#user-needs">8. Потребности пользователей</a></li>' if selected_sections.get('user_needs', False) else ''}
                        {f'<li><a href="#behavioral-patterns">9. Поведенческие паттерны</a></li>' if selected_sections.get('behavioral', False) else ''}
                        {f'<li><a href="#emotional-journey">10. Эмоциональное путешествие</a></li>' if selected_sections.get('emotional', False) else ''}
                        {f'<li><a href="#contradictions">11. Противоречия в данных</a></li>' if selected_sections.get('contradictions', False) else ''}
                        {f'<li><a href="#quotes">12. Значимые цитаты</a></li>' if selected_sections.get('quotes', False) else ''}
                        {f'<li><a href="#recommendations">13. Рекомендации</a></li>' if selected_sections.get('recommendations', False) else ''}
                        {f'<li><a href="#appendix">14. Приложение</a></li>' if selected_sections.get('appendix', False) else ''}
                    </ul>
                </div>
                '''}
                
                {f'''
                <!-- Общий обзор -->
                <div class="section" id="overview">
                    <h2>📊 Общий обзор</h2>
                    <div class="insight">
                        <h3>Краткое резюме исследования</h3>
                        <p>На основе анализа <strong>{transcript_analysis.get('total_words', 0):,}</strong> слов из <strong>{transcripts_count}</strong> интервью 
                        выявлены ключевые паттерны пользовательского поведения и основные проблемы взаимодействия с продуктом.</p>
                        
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-value">{transcripts_count}</div>
                                <div class="metric-label">Интервью проанализировано</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{transcript_analysis.get('total_words', 0):,}</div>
                                <div class="metric-label">Слов в транскриптах</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{transcript_analysis.get('problems_found', 0)}</div>
                                <div class="metric-label">Проблем выявлено</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{transcript_analysis.get('positive_mentions', 0)}</div>
                                <div class="metric-label">Положительных упоминаний</div>
                            </div>
                        </div>
                    </div>
                </div>
                ''' if selected_sections.get('overview', False) else ''}
                
                {f'''
                <!-- Бриф исследования -->
                <div class="section" id="brief">
                    <h2>📋 Бриф исследования</h2>
                    <div class="card">
                        <h3>Цели и задачи исследования</h3>
                        <p>{brief_text if brief_text else 'Бриф не предоставлен'}</p>
                    </div>
                </div>
                ''' if selected_sections.get('brief', False) else ''}
                
                {f'''
                <!-- Ответы на вопросы брифа -->
                <div class="section" id="brief-answers">
                    <h2>❓ Ответы на вопросы брифа</h2>
                    <div class="card">
                        <h3>Детальные ответы на основе анализа интервью</h3>
                        <p>{analysis_result if analysis_result else 'Анализ не выполнен'}</p>
                    </div>
                </div>
                ''' if selected_sections.get('brief_answers', False) else ''}
                
                {f'''
                <!-- Анализ результатов -->
                <div class="section" id="analysis">
                    <h2>🔍 Анализ результатов</h2>
                    <div class="insight">
                        <h3>Основные выводы по транскриптам</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin: 2rem 0;">
                            <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #6b7280;">
                                <h4 style="color: #1f2937; margin-bottom: 0.5rem;">📊 Объем данных</h4>
                                <p style="font-size: 1.1rem; font-weight: 600; color: #374151; margin: 0;">{transcript_analysis.get('total_words', 0):,} слов в {transcripts_count} интервью</p>
                            </div>
                            <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #6b7280;">
                                <h4 style="color: #1f2937; margin-bottom: 0.5rem;">😊 Эмоциональная окраска</h4>
                                <p style="font-size: 1.1rem; font-weight: 600; color: #374151; margin: 0;">{'Преобладают положительные отзывы' if transcript_analysis.get('sentiment_ratio', 0) > 1 else 'Преобладают нейтральные/отрицательные отзывы'}</p>
                            </div>
                            <div style="background: #f3f4f6; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #6b7280;">
                                <h4 style="color: #1f2937; margin-bottom: 0.5rem;">⚠️ Выявленные проблемы</h4>
                                <p style="font-size: 1.1rem; font-weight: 600; color: #374151; margin: 0;">{transcript_analysis.get('problems_found', 0)} упоминаний проблемных моментов</p>
                            </div>
                        </div>
                        
                        <div style="background: #f3f4f6; padding: 2rem; border-radius: 12px; margin: 2rem 0; border: 1px solid #e5e7eb;">
                            <h4 style="color: #1f2937; margin-bottom: 1rem;">📋 Детальный анализ</h4>
                            <div style="background: white; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #6b7280; font-family: 'Courier New', monospace; font-size: 0.95rem; line-height: 1.6; color: #374151; white-space: pre-wrap;">{analysis_result if analysis_result else 'Анализ не выполнен'}</div>
                        </div>
                    </div>
                </div>
                ''' if selected_sections.get('analysis', False) else ''}
                
                {f'''
                <!-- Персоны пользователей -->
                <div class="section" id="personas">
                    <h2>👥 Персоны пользователей</h2>
                    <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                        <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                            На основе анализа <strong>{transcript_analysis.get('total_words', 0):,}</strong> слов и <strong>{transcripts_count}</strong> интервью 
                            созданы детальные персоны пользователей, отражающие реальные потребности и поведение респондентов.
                        </p>
                        <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #6b7280;">
                            <p style="color: #6b7280; font-style: italic; margin: 0;">
                                "Детальные персоны будут доступны после полного анализа через OpenRouter API с реальными данными из интервью"
                            </p>
                        </div>
                    </div>
                </div>
                ''' if selected_sections.get('personas', False) else ''}
                
                {f'''
                <!-- Ключевые инсайты -->
                <div class="section" id="insights">
                    <h2>💡 Ключевые инсайты</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem; margin: 2rem 0;">
                        <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; border-left: 6px solid #6b7280;">
                            <h3 style="color: #1f2937; margin-bottom: 1rem; font-size: 1.3rem;">👥 Пользовательское поведение</h3>
                            <p style="color: #374151; line-height: 1.6; margin-bottom: 1rem;">На основе анализа <strong>{transcript_analysis.get('total_words', 0):,}</strong> слов выявлены ключевые паттерны поведения пользователей.</p>
                            <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                                <div style="background: #374151; color: white; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600;">
                                    ✅ {transcript_analysis.get('positive_mentions', 0)} положительных
                                </div>
                                <div style="background: #6b7280; color: white; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600;">
                                    ❌ {transcript_analysis.get('negative_mentions', 0)} отрицательных
                                </div>
                            </div>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; border-left: 6px solid #6b7280;">
                            <h3 style="color: #1f2937; margin-bottom: 1rem; font-size: 1.3rem;">⚠️ Болевые точки</h3>
                            <p style="color: #374151; line-height: 1.6; margin-bottom: 1rem;">Выявлено <strong>{transcript_analysis.get('problems_found', 0)}</strong> упоминаний проблемных моментов в транскриптах.</p>
                            <div style="background: white; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">Плотность проблем: <strong>{transcript_analysis.get('problem_density', 0):.1f}</strong> на 1K слов</p>
                            </div>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; border-left: 6px solid #6b7280;">
                            <h3 style="color: #1f2937; margin-bottom: 1rem; font-size: 1.3rem;">🚀 Возможности улучшения</h3>
                            <p style="color: #374151; line-height: 1.6; margin-bottom: 1rem;">Соотношение положительных к отрицательным упоминаниям: <strong>{transcript_analysis.get('sentiment_ratio', 0):.1f}:1</strong></p>
                            <div style="background: white; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <p style="color: #6b7280; font-size: 0.9rem; margin: 0; font-weight: 600;">
                                    {'🔧 Требуется работа над улучшением пользовательского опыта' if transcript_analysis.get('sentiment_ratio', 0) < 1 else '✅ Пользователи в целом довольны продуктом'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                ''' if selected_sections.get('insights', False) else ''}
                
                {f'''
                <!-- Болевые точки пользователей -->
                <div class="section" id="pain-points">
                    <h2>⚠️ Болевые точки пользователей</h2>
                    <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                        <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                            На основе анализа выявлены ключевые проблемы, с которыми сталкиваются пользователи при взаимодействии с продуктом.
                        </p>
                        <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #6b7280;">
                            <h4 style="color: #1f2937; margin-bottom: 1rem;">🔧 Конкретные паттерны проблем</h4>
                            <ul style="color: #374151; line-height: 1.6; margin: 0; padding-left: 1.5rem;">
                                {''.join([f'<li style="margin-bottom: 0.5rem;">{problem}</li>' for problem in transcript_analysis.get('specific_problems', [])]) if transcript_analysis.get('specific_problems') else '<li>Конкретные проблемы будут выявлены после полного анализа</li>'}
                            </ul>
                        </div>
                    </div>
                </div>
                ''' if selected_sections.get('pain_points', False) else ''}
                
                {f'''
                <!-- Потребности пользователей -->
                <div class="section" id="user-needs">
                    <h2>🎯 Потребности пользователей</h2>
                    <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                        <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                            Выявленные потребности пользователей на основе их высказываний и поведения в интервью.
                        </p>
                        <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #6b7280;">
                            <h4 style="color: #1f2937; margin-bottom: 1rem;">🌟 Выявленные преимущества</h4>
                            <ul style="color: #374151; line-height: 1.6; margin: 0; padding-left: 1.5rem;">
                                {''.join([f'<li style="margin-bottom: 0.5rem;">{moment}</li>' for moment in transcript_analysis.get('positive_moments', [])]) if transcript_analysis.get('positive_moments') else '<li>Потребности будут детализированы после полного анализа</li>'}
                            </ul>
                        </div>
                    </div>
                </div>
                ''' if selected_sections.get('user_needs', False) else ''}
                
                {f'''
                <!-- Поведенческие паттерны -->
                <div class="section" id="behavioral-patterns">
                    <h2>🔄 Поведенческие паттерны</h2>
                    <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                        <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                            Анализ поведения пользователей и выявленные паттерны взаимодействия с продуктом.
                        </p>
                        <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #6b7280;">
                            <p style="color: #6b7280; font-style: italic; margin: 0;">
                                "Детальные поведенческие паттерны будут доступны после полного анализа через OpenRouter API"
                            </p>
                        </div>
                    </div>
                </div>
                ''' if selected_sections.get('behavioral', False) else ''}
                
                {f'''
                <!-- Эмоциональное путешествие -->
                <div class="section" id="emotional-journey">
                    <h2>😊 Эмоциональное путешествие</h2>
                    <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                        <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                            Анализ эмоциональных состояний пользователей на разных этапах взаимодействия с продуктом.
                        </p>
                        <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #6b7280;">
                            <p style="color: #6b7280; font-style: italic; margin: 0;">
                                "Эмоциональное путешествие будет детализировано после полного анализа через OpenRouter API"
                            </p>
                        </div>
                    </div>
                </div>
                ''' if selected_sections.get('emotional', False) else ''}
                
                {f'''
                <!-- Противоречия -->
                <div class="section" id="contradictions">
                    <h2>⚖️ Противоречия в данных</h2>
                    <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                        <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                            Выявленные противоречия и несоответствия в высказываниях пользователей.
                        </p>
                        <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #6b7280;">
                            <p style="color: #6b7280; font-style: italic; margin: 0;">
                                "Противоречия будут выявлены после полного анализа через OpenRouter API"
                            </p>
                        </div>
                    </div>
                </div>
                ''' if selected_sections.get('contradictions', False) else ''}
                
                {f'''
                <!-- Значимые цитаты -->
                <div class="section" id="quotes">
                    <h2>💬 Значимые цитаты пользователей</h2>
                    <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                        <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                            На основе анализа <strong>{transcript_analysis.get('total_words', 0):,}</strong> слов выделены наиболее показательные высказывания пользователей, 
                            отражающие их опыт взаимодействия с продуктом.
                        </p>
                        <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #6b7280;">
                            <p style="color: #6b7280; font-style: italic; margin: 0;">
                                "Детальные цитаты будут доступны после полного анализа через OpenRouter API"
                            </p>
                        </div>
                    </div>
                </div>
                ''' if selected_sections.get('quotes', False) else ''}
                
                {f'''
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
                        <h3>Долгосрочные улучшения</h3>
                        <p>• Переработать пользовательский интерфейс</p>
                        <p>• Внедрить персонализацию контента</p>
                        <p>• Создать систему обратной связи</p>
                    </div>
                </div>
                ''' if selected_sections.get('recommendations', False) else ''}
                
                {f'''
                <!-- Приложение -->
                <div class="section" id="appendix">
                    <h2>📎 Приложение</h2>
                    <div class="card">
                        <h3>Дополнительные данные</h3>
                        <p><strong>Общее количество символов:</strong> {total_chars:,}</p>
                        <p><strong>Количество интервью:</strong> {transcripts_count}</p>
                        <p><strong>Статус анализа:</strong> {'Завершен' if analysis_result else 'Не выполнен'}</p>
                        <p><strong>Бриф загружен:</strong> {'Да' if brief_uploaded else 'Нет'}</p>
                    </div>
                </div>
                ''' if selected_sections.get('appendix', False) else ''}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

# def generate_detailed_html_report(data):  # УДАЛЕНО - используется EnhancedReportGenerator
    # """Генерация детального HTML отчета"""
    
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
            background: linear-gradient(135deg, #1f2937 0%, #374151 50%, #4b5563 100%);
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
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            padding: 25px;
            border-left: 6px solid #1e40af;
            margin: 20px 0;
            font-style: italic;
            border-radius: 0 12px 12px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .insight {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 6px solid #16a34a;
        }
        
        .problem {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 6px solid #dc2626;
        }
        
        .recommendation {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 6px solid #2563eb;
        }
        
        .brief-section {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
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
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
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
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
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
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
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
            background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
            color: white;
            font-weight: 700;
        }
        
        .highlight {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
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
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            color: #065f46;
        }
        
        .badge-warning {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            color: #92400e;
        }
        
        .badge-danger {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            color: #991b1b;
        }
        
        .trace-section {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
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
                    <li><a href="#analysis">4. Анализ результатов</a></li>
                    <li><a href="#personas">5. Персоны пользователей</a></li>
                    <li><a href="#insights">6. Ключевые инсайты</a></li>
                    <li><a href="#pain-points">7. Болевые точки пользователей</a></li>
                    <li><a href="#user-needs">8. Потребности пользователей</a></li>
                    <li><a href="#behavioral-patterns">9. Поведенческие паттерны</a></li>
                    <li><a href="#emotional-journey">10. Эмоциональное путешествие</a></li>
                    <li><a href="#contradictions">11. Противоречия в данных</a></li>
                    <li><a href="#quotes">12. Значимые цитаты</a></li>
                    <li><a href="#recommendations">13. Рекомендации</a></li>
                    <li><a href="#appendix">14. Приложение</a></li>
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
            
            
            <!-- Анализ результатов -->
            <div class="section" id="analysis">
                <h2>🔍 Анализ результатов</h2>
                <div class="insight">
                    <h3>Основные выводы по транскриптам</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin: 2rem 0;">
                        <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #1e40af;">
                            <h4 style="color: #1e40af; margin-bottom: 0.5rem;">📊 Объем данных</h4>
                            <p style="font-size: 1.1rem; font-weight: 600; color: #374151; margin: 0;">{transcript_analysis.get('total_words', 0):,} слов в {transcripts_count} интервью</p>
                        </div>
                        <div style="background: #f0fdf4; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #16a34a;">
                            <h4 style="color: #16a34a; margin-bottom: 0.5rem;">😊 Эмоциональная окраска</h4>
                            <p style="font-size: 1.1rem; font-weight: 600; color: #374151; margin: 0;">{'Преобладают положительные отзывы' if transcript_analysis.get('sentiment_ratio', 0) > 1 else 'Преобладают нейтральные/отрицательные отзывы'}</p>
                        </div>
                        <div style="background: #fef2f2; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #dc2626;">
                            <h4 style="color: #dc2626; margin-bottom: 0.5rem;">⚠️ Выявленные проблемы</h4>
                            <p style="font-size: 1.1rem; font-weight: 600; color: #374151; margin: 0;">{transcript_analysis.get('problems_found', 0)} упоминаний проблемных моментов</p>
                        </div>
                    </div>
                    
                    <div style="background: #f8fafc; padding: 2rem; border-radius: 12px; margin: 2rem 0; border: 1px solid #e5e7eb;">
                        <h4 style="color: #1e40af; margin-bottom: 1rem;">📋 Детальный анализ</h4>
                        <div style="background: white; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #1e40af; font-family: 'Courier New', monospace; font-size: 0.95rem; line-height: 1.6; color: #374151; white-space: pre-wrap;">{analysis_result if analysis_result else 'Анализ не выполнен'}</div>
                    </div>
                </div>
            </div>
            
        <!-- Персоны пользователей -->
        <div class="section" id="personas">
            <h2>👥 Персоны пользователей</h2>
            <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                    На основе анализа <strong>{transcript_analysis.get('total_words', 0):,}</strong> слов и <strong>{transcripts_count}</strong> интервью 
                    созданы детальные персоны пользователей, отражающие реальные потребности и поведение респондентов.
                </p>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #1e40af;">
                    <p style="color: #6b7280; font-style: italic; margin: 0;">
                        "Детальные персоны будут доступны после полного анализа через OpenRouter API с реальными данными из интервью"
                    </p>
                </div>
            </div>
        </div>

        <!-- Ключевые инсайты -->
        <div class="section" id="insights">
            <h2>💡 Ключевые инсайты</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem; margin: 2rem 0;">
                <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; border-left: 6px solid #6b7280;">
                    <h3 style="color: #0ea5e9; margin-bottom: 1rem; font-size: 1.3rem;">👥 Пользовательское поведение</h3>
                    <p style="color: #374151; line-height: 1.6; margin-bottom: 1rem;">На основе анализа <strong>{transcript_analysis.get('total_words', 0):,}</strong> слов выявлены ключевые паттерны поведения пользователей.</p>
                    <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                        <div style="background: #16a34a; color: white; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600;">
                            ✅ {transcript_analysis.get('positive_mentions', 0)} положительных
                        </div>
                        <div style="background: #dc2626; color: white; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600;">
                            ❌ {transcript_analysis.get('negative_mentions', 0)} отрицательных
                        </div>
                    </div>
                </div>
                
                <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; border-left: 6px solid #6b7280;">
                    <h3 style="color: #dc2626; margin-bottom: 1rem; font-size: 1.3rem;">⚠️ Болевые точки</h3>
                    <p style="color: #374151; line-height: 1.6; margin-bottom: 1rem;">Выявлено <strong>{transcript_analysis.get('problems_found', 0)}</strong> упоминаний проблемных моментов в транскриптах.</p>
                    <div style="background: white; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">Плотность проблем: <strong>{transcript_analysis.get('problem_density', 0):.1f}</strong> на 1K слов</p>
                    </div>
                </div>
                
                <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; border-left: 6px solid #6b7280;">
                    <h3 style="color: #16a34a; margin-bottom: 1rem; font-size: 1.3rem;">🚀 Возможности улучшения</h3>
                    <p style="color: #374151; line-height: 1.6; margin-bottom: 1rem;">Соотношение положительных к отрицательным упоминаниям: <strong>{transcript_analysis.get('sentiment_ratio', 0):.1f}:1</strong></p>
                    <div style="background: white; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        <p style="color: #6b7280; font-size: 0.9rem; margin: 0; font-weight: 600;">
                            {'🔧 Требуется работа над улучшением пользовательского опыта' if transcript_analysis.get('sentiment_ratio', 0) < 1 else '✅ Пользователи в целом довольны продуктом'}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Болевые точки пользователей -->
        <div class="section" id="pain-points">
            <h2>⚠️ Болевые точки пользователей</h2>
            <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                    На основе анализа выявлены ключевые проблемы, с которыми сталкиваются пользователи при взаимодействии с продуктом.
                </p>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #dc2626;">
                    <h4 style="color: #dc2626; margin-bottom: 1rem;">🔧 Конкретные паттерны проблем</h4>
                    <ul style="color: #374151; line-height: 1.6; margin: 0; padding-left: 1.5rem;">
                        {''.join([f'<li style="margin-bottom: 0.5rem;">{problem}</li>' for problem in transcript_analysis.get('specific_problems', [])]) if transcript_analysis.get('specific_problems') else '<li>Конкретные проблемы будут выявлены после полного анализа</li>'}
                    </ul>
                </div>
            </div>
        </div>

        <!-- Потребности пользователей -->
        <div class="section" id="user-needs">
            <h2>🎯 Потребности пользователей</h2>
            <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                    Выявленные потребности пользователей на основе их высказываний и поведения в интервью.
                </p>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #0ea5e9;">
                    <h4 style="color: #0ea5e9; margin-bottom: 1rem;">🌟 Выявленные преимущества</h4>
                    <ul style="color: #374151; line-height: 1.6; margin: 0; padding-left: 1.5rem;">
                        {''.join([f'<li style="margin-bottom: 0.5rem;">{moment}</li>' for moment in transcript_analysis.get('positive_moments', [])]) if transcript_analysis.get('positive_moments') else '<li>Потребности будут детализированы после полного анализа</li>'}
                    </ul>
                </div>
            </div>
        </div>

        <!-- Поведенческие паттерны -->
        <div class="section" id="behavioral-patterns">
            <h2>🔄 Поведенческие паттерны</h2>
            <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                    Анализ поведения пользователей и выявленные паттерны взаимодействия с продуктом.
                </p>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #16a34a;">
                    <p style="color: #6b7280; font-style: italic; margin: 0;">
                        "Детальные поведенческие паттерны будут доступны после полного анализа через OpenRouter API"
                    </p>
                </div>
            </div>
        </div>

        <!-- Эмоциональное путешествие -->
        <div class="section" id="emotional-journey">
            <h2>😊 Эмоциональное путешествие</h2>
            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                    Анализ эмоциональных состояний пользователей на разных этапах взаимодействия с продуктом.
                </p>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f59e0b;">
                    <p style="color: #6b7280; font-style: italic; margin: 0;">
                        "Эмоциональное путешествие будет детализировано после полного анализа через OpenRouter API"
                    </p>
                </div>
            </div>
        </div>

        <!-- Противоречия -->
        <div class="section" id="contradictions">
            <h2>⚖️ Противоречия в данных</h2>
            <div style="background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                    Выявленные противоречия и несоответствия в высказываниях пользователей.
                </p>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #8b5cf6;">
                    <p style="color: #6b7280; font-style: italic; margin: 0;">
                        "Противоречия будут выявлены после полного анализа через OpenRouter API"
                    </p>
                </div>
            </div>
        </div>

        <!-- Значимые цитаты -->
        <div class="section" id="quotes">
            <h2>💬 Значимые цитаты пользователей</h2>
            <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 2rem; border-radius: 16px; margin: 2rem 0;">
                <p style="color: #374151; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                    На основе анализа <strong>{transcript_analysis.get('total_words', 0):,}</strong> слов выделены наиболее показательные высказывания пользователей, 
                    отражающие их опыт взаимодействия с продуктом.
                </p>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #1e40af;">
                    <p style="color: #6b7280; font-style: italic; margin: 0;">
                        "Детальные цитаты будут доступны после полного анализа через OpenRouter API"
                    </p>
                </div>
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
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.3);
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
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%);
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
        color: #1e40af;
        margin: 0;
    }
    
    .step-description {
        color: #6b7280;
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
        border-color: #1e40af;
        background: #edf2f7;
    }
    
    .upload-icon {
        font-size: 3rem;
        color: #6b7280;
        margin-bottom: 1rem;
    }
    
    .upload-text {
        font-size: 1.1rem;
        color: #374151;
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
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        color: white;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        color: white;
    }
    
    .status-error {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        color: white;
    }
    
    .action-button {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 15px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(30, 58, 138, 0.4);
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(30, 58, 138, 0.6);
    }
    
    .clear-button {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4);
    }
    
    .clear-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(220, 38, 38, 0.6);
    }
    
    .info-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border-left: 5px solid #1e40af;
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
        color: #1e40af;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #6b7280;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .sidebar-content {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
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
        border-left: 4px solid #1e40af;
    }
    
    .progress-container {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%);
        height: 8px;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .success-message {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .error-message {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
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
    <p>Профессиональный анализ транскриптов пользовательских интервью</p>
</div>
""", unsafe_allow_html=True)

# Основной контент
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
    uploaded_files = st.file_uploader(
        "📄 Транскрипты интервью",
        type=['txt', 'md', 'docx', 'doc'],
        accept_multiple_files=True,
        help="Поддерживаемые форматы: .txt, .md, .docx, .doc"
    )
    
    if uploaded_files:
        st.success(f"✅ Загружено {len(uploaded_files)} файлов")
        for file in uploaded_files:
            st.info(f"📄 {file.name} ({(file.size / 1024):.1f} KB)")

with col2_2:
    uploaded_brief = st.file_uploader(
        "📋 Бриф исследования (опционально)",
        type=['txt', 'md', 'docx', 'doc'],
        help="Бриф с целями исследования"
    )
    
    if uploaded_brief:
        st.success("✅ Бриф загружен")

# Кнопка анализа
if st.button("🚀 Генерация отчета", type="primary", disabled=not (uploaded_files and api_key), use_container_width=True):
    if not api_key:
        st.error("❌ Введите API ключ!")
    elif not uploaded_files:
        st.error("❌ Загрузите транскрипты!")
    else:
        # Простая проверка API ключа
        if not api_key.startswith("sk-or-v1-"):
            st.error("⚠️ Проверьте формат API ключа")
            st.stop()
        
        # Показываем прогресс
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Читаем транскрипты
        status_text.text("📖 Чтение файлов...")
        progress_bar.progress(20)
        
        transcripts = []
        for file in uploaded_files:
            content = read_file_content(file)
            transcripts.append(content)
        
        # Реальный анализ через новые классы
        status_text.text("🤖 Анализ данных...")
        progress_bar.progress(40)
        
        try:
            # Создаем анализатор
            analyzer = AdvancedUXAnalyzer(api_key)
            
            # Устанавливаем бриф если есть
            if uploaded_brief:
                brief_text = read_file_content(uploaded_brief)
                analyzer.set_brief(brief_text)
            
            # Запускаем анализ
            status_text.text("🔄 Запуск комплексного анализа...")
            progress_bar.progress(60)
            
            analysis_results = analyzer.analyze_transcripts(transcripts)
            
            status_text.text("✅ Анализ завершен!")
            progress_bar.progress(80)
            
            # Извлекаем результаты
            analysis_result = "Анализ выполнен успешно"
            report_data = analysis_results
            
        except Exception as e:
            analysis_result = f"Ошибка анализа: {str(e)}"
            st.error(f"❌ Ошибка: {e}")
            report_data = None
        
        # Создаем структурированные данные для отчета
        status_text.text("📋 Генерация отчета...")
        progress_bar.progress(90)
        
        if report_data:
            # Создаем конфигурацию компании
            company_config = CompanyConfig(
                name=company_name,
                report_title=report_title,
                author=author
            )
            
            # Генерируем полный HTML отчет
            generator = EnhancedReportGenerator(company_config)
            html_report = generator.generate_html(report_data)
            
            # Сохраняем отчет в session_state для скачивания
            st.session_state['html_report'] = html_report
        else:
            st.error("❌ Не удалось сгенерировать отчет")
            html_report = None
        
        # Завершаем прогресс
        status_text.text("🎉 Готово!")
        progress_bar.progress(100)
        
        st.success("🎉 Анализ успешно завершен!")
        
        # Сохраняем данные отчета в session_state
        if report_data:
            st.session_state['report_data'] = report_data
        
        # Показываем результаты
        st.markdown("## 📊 Настройка отчета")
        
        # Выбор блоков для включения в отчет
        st.markdown("### Выберите разделы для включения в отчет:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            include_overview = st.checkbox("📊 Общий обзор", value=True)
            include_brief = st.checkbox("📋 Бриф исследования", value=True)
            include_brief_answers = st.checkbox("❓ Ответы на вопросы брифа", value=True)
            include_analysis = st.checkbox("🔍 Анализ результатов", value=True)
            include_personas = st.checkbox("👥 Персоны пользователей", value=True)
            
        with col2:
            include_insights = st.checkbox("💡 Ключевые инсайты", value=True)
            include_pain_points = st.checkbox("⚠️ Болевые точки", value=True)
            include_user_needs = st.checkbox("🎯 Потребности пользователей", value=True)
            include_behavioral = st.checkbox("🔄 Поведенческие паттерны", value=True)
            include_emotional = st.checkbox("😊 Эмоциональное путешествие", value=True)
            
        with col3:
            include_contradictions = st.checkbox("⚖️ Противоречия", value=True)
            include_quotes = st.checkbox("💬 Значимые цитаты", value=True)
            include_recommendations = st.checkbox("🎯 Рекомендации", value=True)
            include_appendix = st.checkbox("📎 Приложение", value=True)
        
        # Генерируем отчет с выбранными блоками
        col_gen_1, col_gen_2, col_gen_3 = st.columns([1, 2, 1])
        
        with col_gen_2:
            if st.button("📄 Сгенерировать кастомный отчет", type="primary", use_container_width=True):
                with st.spinner("🔄 Генерация отчета..."):
                    # Собираем выбранные разделы
                    selected_sections = {
                        'overview': include_overview,
                        'brief': include_brief,
                        'brief_answers': include_brief_answers,
                        'analysis': include_analysis,
                        'personas': include_personas,
                        'insights': include_insights,
                        'pain_points': include_pain_points,
                        'user_needs': include_user_needs,
                        'behavioral': include_behavioral,
                        'emotional': include_emotional,
                        'contradictions': include_contradictions,
                        'quotes': include_quotes,
                        'recommendations': include_recommendations,
                        'appendix': include_appendix
                    }
                    
                    # Генерируем кастомный отчет
                    if 'report_data' in st.session_state and st.session_state['report_data']:
                        company_config = CompanyConfig(
                            name=st.session_state['report_data'].get('company', 'Company'),
                            report_title=st.session_state['report_data'].get('report_title', 'UX Report'),
                            author=st.session_state['report_data'].get('author', 'Research Team')
                        )
                        generator = EnhancedReportGenerator(company_config)
                        custom_html_report = generator.generate_html(st.session_state['report_data'])
                    else:
                        st.error("❌ Данные отчета не найдены. Сначала выполните анализ.")
                        custom_html_report = None
                    
                    # Сохраняем в session_state
                    st.session_state['custom_html_report'] = custom_html_report
                    st.session_state['selected_sections'] = selected_sections
                    
                    st.success("✅ Отчет сгенерирован! Используйте кнопку скачивания ниже.")
                    st.rerun()
        
        # Кнопки для скачивания HTML
        col_download_1, col_download_2 = st.columns(2)
        
        with col_download_1:
            # Полный отчет
            if 'html_report' in st.session_state and st.session_state['html_report']:
                st.download_button(
                    label="📥 Скачать полный отчет",
                    data=st.session_state['html_report'].encode('utf-8'),
                    file_name=f"ux_report_full_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            else:
                st.button("📥 Скачать полный отчет", disabled=True, use_container_width=True)
        
        with col_download_2:
            # Кастомный отчет
            if 'custom_html_report' in st.session_state and st.session_state['custom_html_report']:
                try:
                    html_data = st.session_state['custom_html_report']
                    if isinstance(html_data, str):
                        # Показываем информацию о выбранных разделах
                        selected_count = sum(1 for v in st.session_state.get('selected_sections', {}).values() if v)
                        st.info(f"📊 Кастомный отчет: {selected_count} разделов")
                        
                        st.download_button(
                            label="📥 Скачать кастомный отчет",
                            data=html_data.encode('utf-8'),
                            file_name=f"ux_report_custom_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                            mime="text/html",
                            use_container_width=True
                        )
                    else:
                        st.error("Ошибка: HTML отчет имеет неверный формат")
                except Exception as e:
                    st.error(f"Ошибка при создании кнопки скачивания: {str(e)}")
            else:
                st.button("📥 Скачать кастомный отчет", disabled=True, use_container_width=True)
        
        # Информация о следующих шагах
        st.markdown("""
        <div class="info-card">
            <h3>🎯 Результат анализа</h3>
            <p>• Анализ выполнен успешно</p>
            <p>• Сгенерирован детальный HTML отчет</p>
            <p>• Ответы основаны на реальных транскриптах интервью</p>
            <p>• Цитаты взяты из интервью</p>
        </div>
        """, unsafe_allow_html=True)

# Кнопка очистки внизу
st.markdown("---")
col_clear_1, col_clear_2, col_clear_3 = st.columns([1, 1, 1])

with col_clear_2:
    if st.button("🗑️ Очистить все", type="secondary", use_container_width=True):
        st.rerun()
