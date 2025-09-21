#!/usr/bin/env python3
"""
Простой веб-интерфейс для UX Анализатора
Запуск: python3 simple_web_app.py
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import traceback
from pathlib import Path
import sys

# Добавляем текущую директорию в путь для импорта
sys.path.append('.')

app = Flask(__name__)

# Импортируем классы из ноутбука
try:
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
    
    print("✅ Анализатор загружен успешно")
    
except Exception as e:
    print(f"❌ Ошибка загрузки анализатора: {e}")
    traceback.print_exc()

# Глобальные переменные для хранения состояния
analyzer_instance = None
analysis_results = None

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API для анализа транскриптов"""
    global analyzer_instance, analysis_results
    
    try:
        data = request.get_json()
        
        # Получаем данные из запроса
        api_key = data.get('api_key')
        company_name = data.get('company_name', 'Company')
        report_title = data.get('report_title', 'UX Research Report')
        author = data.get('author', 'Research Team')
        transcripts = data.get('transcripts', [])
        brief_content = data.get('brief_content', '')
        
        if not api_key:
            return jsonify({'error': 'API ключ не предоставлен'}), 400
        
        if not transcripts:
            return jsonify({'error': 'Транскрипты не предоставлены'}), 400
        
        # Создаем анализатор
        analyzer_instance = AdvancedGeminiAnalyzer(api_key)
        
        # Устанавливаем бриф если есть
        if brief_content:
            analyzer_instance.set_brief(brief_content)
        
        # Обновляем конфигурацию
        analyzer_instance.company_config.name = company_name
        analyzer_instance.company_config.report_title = report_title
        analyzer_instance.company_config.author = author
        
        # Запускаем анализ
        analysis_results = analyzer_instance.analyze_transcripts_parallel(transcripts)
        
        return jsonify({
            'success': True,
            'message': 'Анализ завершен успешно',
            'results': analysis_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/status')
def status():
    """Проверка статуса анализатора"""
    return jsonify({
        'status': 'ready',
        'analyzer_loaded': analyzer_instance is not None
    })

if __name__ == '__main__':
    # Создаем директорию для шаблонов
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Запуск простого веб-интерфейса...")
    print("📱 Откройте http://localhost:5000 в браузере")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
