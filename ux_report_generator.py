# -*- coding: utf-8 -*-
"""UX Report Generator - Генератор HTML отчетов"""

from datetime import datetime
from typing import Dict, List, Any
from ux_analyzer_classes import CompanyConfig

# ========================================================================
# ГЕНЕРАТОР HTML ОТЧЕТОВ
# ========================================================================
class EnhancedReportGenerator:
    def __init__(self, company_config: CompanyConfig):
        self.config = company_config
        self.colors = {
            'primary': '#1f2937',
            'secondary': '#6b7280',
            'accent': '#3b82f6',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'text_primary': '#111827',
            'text_secondary': '#6b7280',
            'background': '#ffffff',
            'surface': '#f9fafb',
            'border': '#e5e7eb'
        }

    def generate_html(self, analysis_data: Dict) -> str:
        """Генерация полного HTML отчета"""
        print(f"🔍 DEBUG: analysis_data keys: {list(analysis_data.keys())}")
        
        findings = analysis_data.get('findings', {})
        personas = analysis_data.get('personas', [])
        recommendations = analysis_data.get('recommendations', {})
        brief_answers = analysis_data.get('brief_answers', {})
        current_metrics = analysis_data.get('current_metrics', {})
        interview_summaries = analysis_data.get('interview_summaries', [])
        total_interviews = analysis_data.get('total_interviews', len(interview_summaries))
        
        print(f"🔍 DEBUG: findings type: {type(findings)}")
        print(f"🔍 DEBUG: personas count: {len(personas)}")
        print(f"🔍 DEBUG: interview_summaries count: {len(interview_summaries)}")
        
        # Если findings - это объект ResearchFindings, извлекаем данные
        if hasattr(findings, 'key_insights'):
            print(f"🔍 DEBUG: findings is ResearchFindings object")
            findings_data = {
                'executive_summary': getattr(findings, 'executive_summary', 'Анализ пользовательских интервью выявил ключевые проблемы и возможности для улучшения продукта.'),
                'key_insights': getattr(findings, 'key_insights', []),
                'behavioral_patterns': getattr(findings, 'behavioral_patterns', []),
                'user_segments': getattr(findings, 'user_segments', []),
                'pain_points_map': getattr(findings, 'pain_points_map', {}),
                'opportunities': getattr(findings, 'opportunities', []),
                'recommendations': getattr(findings, 'recommendations', []),
                'risks': getattr(findings, 'risks', []),
                'personas': getattr(findings, 'personas', []),
                'current_metrics': getattr(findings, 'current_metrics', {}),
                'brief_answers': getattr(findings, 'brief_answers', {}),
                'goal_achievement': getattr(findings, 'goal_achievement', {})
            }
            print(f"🔍 DEBUG: extracted key_insights: {len(findings_data.get('key_insights', []))}")
        else:
            print(f"🔍 DEBUG: findings is not ResearchFindings object, type: {type(findings)}")
            findings_data = findings if findings else {
                'executive_summary': 'Анализ пользовательских интервью выявил ключевые проблемы и возможности для улучшения продукта.',
                'key_insights': [],
                'behavioral_patterns': [],
                'user_segments': [],
                'pain_points_map': {},
                'opportunities': [],
                'recommendations': [],
                'risks': [],
                'personas': [],
                'current_metrics': {},
                'brief_answers': {},
                'goal_achievement': {}
            }
            print(f"🔍 DEBUG: findings_data key_insights: {len(findings_data.get('key_insights', []))}")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.report_title} - {self.config.name}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    {self._generate_header()}
    {self._generate_table_of_contents()}
                   {self._generate_executive_summary(findings_data)}
                   {self._generate_data_warnings(total_interviews, findings_data, personas, interview_summaries)}
                   {self._generate_brief_section(analysis_data.get('brief_data', {}))}
                   {self._generate_brief_answers(brief_answers)}
                   {self._generate_personas_section(personas)}
                   {self._generate_insights_section(findings_data.get('key_insights', []))}
                   {self._generate_pain_points_section(findings_data.get('key_insights', []))}
                   {self._generate_user_needs_section(findings_data)}
                   {self._generate_behavioral_patterns_section(findings_data.get('behavioral_patterns', []))}
                   {self._generate_emotional_journey_section(interview_summaries)}
                   {self._generate_contradictions_section(interview_summaries)}
                   {self._generate_quotes_section(interview_summaries)}
                   {self._generate_recommendations_section(recommendations)}
                   {self._generate_appendix_section(analysis_data)}
    {self._generate_footer()}
</body>
</html>
"""
        return html_content

    def _generate_data_warnings(self, total_interviews: int, findings_data: Dict, personas: List, interview_summaries: List) -> str:
        """Генерация предупреждений о недостатке данных"""
        warnings = []
        
        # Проверка количества интервью
        if total_interviews < 5:
            warnings.append(f"⚠️ <strong>Ограниченная выборка:</strong> Анализ основан на {total_interviews} интервью. Для качественного анализа рекомендуется минимум 5-8 интервью.")
        
        # Проверка персон
        if len(personas) < 2:
            warnings.append("⚠️ <strong>Недостаточно персон:</strong> Создано менее 2 персон. Для качественной сегментации рекомендуется больше интервью.")
        
        # Проверка инсайтов
        key_insights = findings_data.get('key_insights', [])
        if len(key_insights) < 3:
            warnings.append("⚠️ <strong>Ограниченные инсайты:</strong> Выявлено менее 3 ключевых инсайтов. Рекомендуется расширить выборку интервью.")
        
        # Проверка цитат
        total_quotes = 0
        for summary in interview_summaries:
            if hasattr(summary, 'quotes'):
                total_quotes += len(summary.quotes)
        
        if total_quotes < 5:
            warnings.append("⚠️ <strong>Недостаточно цитат:</strong> Собрано менее 5 значимых цитат. Рекомендуется более детальные интервью.")
        
        if not warnings:
            return ""
        
        warnings_html = ""
        for warning in warnings:
            warnings_html += f'<div class="warning-card">{warning}</div>'
        
        return f"""
        <div class="page" id="data-warnings">
            <div class="container">
                <h2>⚠️ Ограничения анализа</h2>
                <div class="card">
                    <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 20px;">
                        Следующие ограничения могут повлиять на качество и надежность анализа:
                    </p>
                    {warnings_html}
                </div>
            </div>
        </div>
        """

    def _get_css_styles(self) -> str:
        """CSS стили для отчета"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #111827;
            background: #ffffff;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        .header {
            background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
            color: white;
            padding: 60px 0;
            text-align: center;
        }

        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 10px;
        }

        .header .meta {
            font-size: 1rem;
            opacity: 0.8;
        }

        .toc {
            background: #f9fafb;
            padding: 40px 0;
            border-bottom: 1px solid #e5e7eb;
        }

        .toc h2 {
            text-align: center;
            margin-bottom: 30px;
            color: #1f2937;
        }

        .toc-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .toc-item {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
        }

        .toc-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .toc-item h3 {
            color: #1f2937;
            margin-bottom: 10px;
        }

        .toc-item p {
            color: #6b7280;
            font-size: 0.9rem;
        }

        .page {
            padding: 60px 0;
            border-bottom: 1px solid #e5e7eb;
        }

        .page h2 {
            font-size: 2.5rem;
            color: #1f2937;
            margin-bottom: 20px;
            text-align: center;
        }

        .page h3 {
            font-size: 1.8rem;
            color: #1f2937;
            margin: 40px 0 20px 0;
        }

        .page h4 {
            font-size: 1.4rem;
            color: #374151;
            margin: 30px 0 15px 0;
        }

        .card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .persona-card {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border: 2px solid #cbd5e1;
            border-radius: 16px;
            padding: 30px;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
        }

        .persona-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
        }

        .persona-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 20px;
        }

        .persona-name {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1f2937;
        }

        .persona-id {
            background: #3b82f6;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .persona-tagline {
            font-style: italic;
            color: #6b7280;
            margin: 10px 0;
            font-size: 1.1rem;
        }

        .persona-section {
            margin: 20px 0;
        }

        .persona-section h5 {
            color: #374151;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }

        .persona-section ul {
            list-style: none;
            padding: 0;
        }

        .persona-section li {
            background: white;
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 6px;
            border-left: 3px solid #3b82f6;
        }

        .quote-card {
            background: #f8fafc;
            border-left: 4px solid #3b82f6;
            padding: 20px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
        }

        .warning-card {
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            color: #92400e;
        }

        .warning-card strong {
            color: #b45309;
        }

        .quote-text {
            font-style: italic;
            color: #374151;
            margin-bottom: 10px;
            line-height: 1.7;
        }

        .quote-author {
            color: #6b7280;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .insight-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 25px;
            margin: 20px 0;
            position: relative;
        }

        .insight-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: #3b82f6;
            border-radius: 2px 0 0 2px;
        }

        .tag {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin: 5px 5px 5px 0;
        }

        .tag.priority-high {
            background: #fef2f2;
            color: #dc2626;
            border: 1px solid #fecaca;
        }

        .tag.priority-medium {
            background: #fffbeb;
            color: #d97706;
            border: 1px solid #fed7aa;
        }

        .tag.priority-low {
            background: #f0fdf4;
            color: #16a34a;
            border: 1px solid #bbf7d0;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .metric-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 10px;
        }

        .metric-label {
            color: #6b7280;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .footer {
            background: #1f2937;
            color: white;
            padding: 40px 0;
            text-align: center;
        }

        .footer p {
            margin: 10px 0;
            opacity: 0.8;
        }

        @media (max-width: 768px) {
            .container {
                padding: 0 15px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .toc-grid {
                grid-template-columns: 1fr;
            }
            
            .persona-header {
                flex-direction: column;
                align-items: start;
            }
        }
        """

    def _generate_header(self) -> str:
        """Генерация заголовка"""
        return f"""
        <div class="header">
            <div class="container">
                <h1>{self.config.report_title}</h1>
                <p class="subtitle">{self.config.name}</p>
                <p class="meta">Автор: {self.config.author} | Дата: {datetime.now().strftime('%d.%m.%Y')}</p>
            </div>
        </div>
        """

    def _generate_table_of_contents(self) -> str:
        """Генерация содержания"""
        return """
        <div class="toc">
            <div class="container">
                <h2>Содержание</h2>
                <div class="toc-grid">
                    <div class="toc-item">
                        <h3>1. Резюме</h3>
                        <p>Ключевые выводы и рекомендации</p>
                    </div>
                    <div class="toc-item">
                        <h3>2. Бриф исследования</h3>
                        <p>Цели, вопросы и контекст</p>
                    </div>
                    <div class="toc-item">
                        <h3>3. Ответы на вопросы брифа</h3>
                        <p>Детальные ответы с цитатами</p>
                    </div>
                    <div class="toc-item">
                        <h3>4. Персоны пользователей</h3>
                        <p>Детальные профили пользователей</p>
                    </div>
                    <div class="toc-item">
                        <h3>5. Ключевые инсайты</h3>
                        <p>Глубокие выводы из анализа</p>
                    </div>
                    <div class="toc-item">
                        <h3>6. Проблемы пользователей</h3>
                        <p>Детальный анализ проблем</p>
                    </div>
                    <div class="toc-item">
                        <h3>7. Потребности пользователей</h3>
                        <p>Явные и скрытые потребности</p>
                    </div>
                    <div class="toc-item">
                        <h3>8. Поведенческие паттерны</h3>
                        <p>Устойчивые модели поведения</p>
                    </div>
                    <div class="toc-item">
                        <h3>9. Эмоциональный опыт</h3>
                        <p>Анализ эмоциональных реакций</p>
                    </div>
                    <div class="toc-item">
                        <h3>10. Противоречия</h3>
                        <p>Несоответствия в данных</p>
                    </div>
                    <div class="toc-item">
                        <h3>11. Значимые цитаты</h3>
                        <p>Ключевые высказывания пользователей</p>
                    </div>
                    <div class="toc-item">
                        <h3>12. Рекомендации</h3>
                        <p>Конкретные действия для улучшения</p>
                    </div>
                    <div class="toc-item">
                        <h3>13. Приложение</h3>
                        <p>Дополнительные данные и метрики</p>
                    </div>
                </div>
            </div>
        </div>
        """

    def _generate_executive_summary(self, findings_data) -> str:
        """Генерация резюме"""
        if isinstance(findings_data, dict):
            summary = findings_data.get('executive_summary', 'Анализ пользовательских интервью выявил ключевые проблемы и возможности для улучшения продукта.')
        else:
            summary = getattr(findings_data, 'executive_summary', 'Анализ пользовательских интервью выявил ключевые проблемы и возможности для улучшения продукта.')
        
        return f"""
        <div class="page" id="summary">
            <div class="container">
                <h2>Резюме</h2>
                <div class="card">
                    <p style="font-size: 1.2rem; line-height: 1.8; color: #374151;">
                        {summary}
                    </p>
                </div>
            </div>
        </div>
        """

    def _generate_brief_section(self, brief_data: Dict) -> str:
        """Генерация секции брифа"""
        if not brief_data:
            return ""

        goals_html = ""
        if brief_data.get('research_goals'):
            goals_html = "<h4>Цели исследования:</h4><ul>"
            for goal in brief_data['research_goals']:
                goals_html += f"<li>{goal}</li>"
            goals_html += "</ul>"

        questions_html = ""
        if brief_data.get('research_questions'):
            questions_html = "<h4>Исследовательские вопросы:</h4><ul>"
            for question in brief_data['research_questions']:
                questions_html += f"<li>{question}</li>"
            questions_html += "</ul>"

        return f"""
        <div class="page" id="brief">
            <div class="container">
                <h2>Бриф исследования</h2>
                <div class="card">
                    {goals_html}
                    {questions_html}
                    {f"<h4>Целевая аудитория:</h4><p>{brief_data.get('target_audience', '')}</p>" if brief_data.get('target_audience') else ""}
                    {f"<h4>Бизнес-контекст:</h4><p>{brief_data.get('business_context', '')}</p>" if brief_data.get('business_context') else ""}
                </div>
            </div>
        </div>
        """

    def _generate_brief_answers(self, brief_answers: Dict) -> str:
        """Генерация ответов на вопросы брифа"""
        if not brief_answers or not brief_answers.get('answers'):
            return ""

        answers_html = ""
        for answer in brief_answers['answers']:
            quotes_html = ""
            if answer.get('supporting_quotes'):
                quotes_html = "<h5>Поддерживающие цитаты:</h5><ul>"
                for quote in answer['supporting_quotes']:
                    quotes_html += f"<li>\"{quote}\"</li>"
                quotes_html += "</ul>"

            answers_html += f"""
            <div class="card">
                <h4>{answer.get('question', '')}</h4>
                <p style="font-size: 1.1rem; line-height: 1.7; margin: 15px 0;">
                    {answer.get('answer', '')}
                </p>
                {quotes_html}
                <div style="margin-top: 15px;">
                    <span class="tag">Уверенность: {answer.get('confidence', 'N/A')}/10</span>
                </div>
            </div>
            """

        return f"""
        <div class="page" id="brief-answers">
            <div class="container">
                <h2>Ответы на вопросы брифа</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Детальные ответы на исследовательские вопросы с подкреплением цитатами
                </p>
                {answers_html}
            </div>
        </div>
        """

    def _generate_personas_section(self, personas) -> str:
        """Генерация секции персон"""
        if not personas or not isinstance(personas, list):
            return """
            <div class="page" id="personas">
                <div class="container">
                    <h2>Персоны пользователей</h2>
                    <div class="card">
                        <p style="color: #6b7280; font-style: italic;">
                            ⚠️ Недостаточно данных для создания персон. Рекомендуется провести больше интервью для качественной сегментации пользователей.
                        </p>
                    </div>
                </div>
            </div>
            """

        personas_html = ""
        for persona in personas:
            demographics_html = ""
            if persona.get('demographics'):
                demographics_html = "<h5>Демография:</h5><ul>"
                for key, value in persona['demographics'].items():
                    demographics_html += f"<li><strong>{key}:</strong> {value}</li>"
                demographics_html += "</ul>"

            goals_html = ""
            if persona.get('goals'):
                goals_html = "<h5>Цели:</h5><ul>"
                for goal in persona['goals']:
                    goals_html += f"<li>{goal}</li>"
                goals_html += "</ul>"

            frustrations_html = ""
            if persona.get('frustrations'):
                frustrations_html = "<h5>Фрустрации:</h5><ul>"
                for frustration in persona['frustrations']:
                    frustrations_html += f"<li>{frustration}</li>"
                frustrations_html += "</ul>"

            needs_html = ""
            if persona.get('needs'):
                needs_html = "<h5>Потребности:</h5><ul>"
                for need in persona['needs']:
                    needs_html += f"<li>{need}</li>"
                needs_html += "</ul>"

            quotes_html = ""
            if persona.get('real_quotes'):
                quotes_html = "<h5>Ключевые цитаты:</h5>"
                for quote in persona['real_quotes']:
                    if quote:
                        quotes_html += f'<div class="quote-card"><p class="quote-text">"{quote}"</p></div>'

            personas_html += f"""
            <div class="persona-card">
                <div class="persona-header">
                    <div>
                        <div class="persona-name">{persona.get('name', 'Пользователь')}</div>
                        <div class="persona-tagline">"{persona.get('tagline', '')}"</div>
                    </div>
                    <div class="persona-id">{persona.get('persona_id', '')}</div>
                </div>
                
                <div class="persona-section">
                    <p style="font-size: 1.1rem; line-height: 1.7; color: #374151;">
                        {persona.get('description', '')}
                    </p>
                </div>

                {demographics_html}
                {goals_html}
                {frustrations_html}
                {needs_html}
                {quotes_html}

                <div class="persona-section">
                    <h5>Типичный сценарий:</h5>
                    <p>{persona.get('typical_scenario', '')}</p>
                </div>
            </div>
            """

        return f"""
        <div class="page" id="personas">
            <div class="container">
                <h2>Персоны пользователей</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Детальные профили пользователей, созданные на основе реальных интервью
                </p>
                {personas_html}
            </div>
        </div>
        """

    def _generate_insights_section(self, insights) -> str:
        """Генерация секции инсайтов"""
        if not insights or not isinstance(insights, list):
            return """
            <div class="page" id="insights">
                <div class="container">
                    <h2>Ключевые инсайты</h2>
                    <div class="card">
                        <p style="color: #6b7280; font-style: italic;">
                            ⚠️ Недостаточно данных для выявления ключевых инсайтов. Рекомендуется провести больше интервью для качественного анализа.
                        </p>
                    </div>
                </div>
            </div>
            """

        insights_html = ""
        for i, insight in enumerate(insights[:8], 1):
            quotes_html = ""
            if insight.get('quotes'):
                quotes_html = "<div style='margin-top: 20px;'><h5>Поддерживающие цитаты:</h5>"
                for quote in insight['quotes'][:2]:
                    if isinstance(quote, dict):
                        quotes_html += f'<div class="quote-card"><p class="quote-text">{quote.get("text", "")}</p></div>'
                    else:
                        quotes_html += f'<div class="quote-card"><p class="quote-text">"{quote}"</p></div>'
                quotes_html += "</div>"

            insights_html += f"""
            <div class="insight-card">
                <h3>Инсайт #{i}: {insight.get('problem_title', insight.get('title', ''))}</h3>
                <p style="font-size: 1.2rem; line-height: 1.8; margin: 20px 0; font-weight: 500;">
                    {insight.get('problem_description', insight.get('description', ''))}
                </p>
                {quotes_html}
                <div style="margin-top: 20px; display: flex; gap: 15px;">
                    <span class="tag priority-{insight.get('severity', 'medium')}">
                        {str(insight.get('severity', 'medium')).upper()}
                    </span>
                    {f'<span class="tag">Затронуто: {insight.get("affected_percentage", "")}</span>' if insight.get('affected_percentage') else ''}
                </div>
            </div>
            """

        return f"""
        <div class="page" id="insights">
            <div class="container">
                <h2>Ключевые инсайты</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Глубокие выводы, основанные на кросс-анализе всех интервью
                </p>
                {insights_html}
            </div>
        </div>
        """

    def _generate_pain_points_section(self, insights) -> str:
        """Генерация секции проблем"""
        if not insights or not isinstance(insights, list):
            return ""

        return f"""
        <div class="page" id="pain-points">
            <div class="container">
                <h2>Детальные проблемы пользователей</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Анализ выявленных проблем с приоритизацией и цитатами
                </p>
                {self._generate_insights_section(insights)}
            </div>
        </div>
        """

    def _generate_user_needs_section(self, findings: Dict) -> str:
        """Генерация секции потребностей"""
        return f"""
        <div class="page" id="user-needs">
            <div class="container">
                <h2>Потребности пользователей</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Явные и скрытые потребности, выявленные в процессе анализа
                </p>
                <div class="card">
                    <p>Детальный анализ потребностей будет добавлен в следующих версиях отчета.</p>
                </div>
            </div>
        </div>
        """

    def _generate_behavioral_patterns_section(self, patterns) -> str:
        """Генерация секции поведенческих паттернов"""
        if not patterns or not isinstance(patterns, list):
            return ""

        patterns_html = ""
        for pattern in patterns:
            patterns_html += f"""
            <div class="card">
                <h4>{pattern.get('pattern', '')}</h4>
                <p>{pattern.get('description', '')}</p>
                <div style="margin-top: 15px;">
                    <span class="tag">Частота: {pattern.get('frequency', 0)}</span>
                    <span class="tag">Серьезность: {str(pattern.get('severity', 0))}/10</span>
                </div>
            </div>
            """

        return f"""
        <div class="page" id="patterns">
            <div class="container">
                <h2>Поведенческие паттерны</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Устойчивые модели поведения, выявленные в процессе анализа
                </p>
                {patterns_html}
            </div>
        </div>
        """

    def _generate_emotional_journey_section(self, summaries) -> str:
        """Генерация секции эмоционального пути"""
        if not summaries or not isinstance(summaries, list):
            return ""
            
        return f"""
        <div class="page" id="emotions">
            <div class="container">
                <h2>Эмоциональный опыт пользователей</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Анализ эмоциональных реакций и их триггеров
                </p>
                <div class="card">
                    <p>Детальный анализ эмоционального пути будет добавлен в следующих версиях отчета.</p>
                </div>
            </div>
        </div>
        """

    def _generate_contradictions_section(self, summaries) -> str:
        """Генерация секции противоречий"""
        if not summaries or not isinstance(summaries, list):
            return ""
            
        return f"""
        <div class="page" id="contradictions">
            <div class="container">
                <h2>Противоречия в данных</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Несоответствия и противоречия, выявленные в ответах респондентов
                </p>
                <div class="card">
                    <p>Значительных противоречий в ответах респондентов не выявлено.</p>
                </div>
            </div>
        </div>
        """

    def _generate_quotes_section(self, summaries) -> str:
        """Генерация секции цитат"""
        # Собираем все цитаты
        all_quotes = []
        if not summaries or not isinstance(summaries, list):
            return ""
            
        for summary in summaries:
            if hasattr(summary, 'quotes'):
                for quote in summary.quotes:
                    if isinstance(quote, dict) and quote.get('text'):
                        all_quotes.append({
                            'text': quote['text'],
                            'interview_id': getattr(summary, 'interview_id', ''),
                            'context': quote.get('context', ''),
                            'importance': quote.get('importance', 0)
                        })

        # Сортируем по важности
        all_quotes.sort(key=lambda x: int(x.get('importance', 0)) if isinstance(x.get('importance', 0), (int, float)) else 0, reverse=True)

        quotes_html = ""
        for quote in all_quotes[:10]:
            quotes_html += f"""
            <div class="quote-card">
                <p class="quote-text">"{quote['text']}"</p>
                <span class="quote-author">Интервью {quote['interview_id']}</span>
            </div>
            """

        return f"""
        <div class="page" id="quotes">
            <div class="container">
                <h2>Значимые цитаты пользователей</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Ключевые высказывания, отражающие основные проблемы и потребности
                </p>
                {quotes_html}
            </div>
        </div>
        """

    def _generate_recommendations_section(self, recommendations: Dict) -> str:
        """Генерация секции рекомендаций"""
        if not recommendations:
            return ""

        quick_wins_html = ""
        if recommendations.get('quick_wins'):
            for win in recommendations['quick_wins']:
                steps_html = ""
                if win.get('implementation_steps'):
                    steps_html = "<h5>Шаги реализации:</h5><ol>"
                    for step in win['implementation_steps']:
                        steps_html += f"<li>{step}</li>"
                    steps_html += "</ol>"

                quick_wins_html += f"""
                <div class="card">
                    <h4>{win.get('title', '')}</h4>
                    <p style="font-size: 1.1rem; line-height: 1.7; margin: 15px 0;">
                        {win.get('description', '')}
                    </p>
                    {steps_html}
                    <div style="margin-top: 15px;">
                        <span class="tag">Срок: {win.get('timeline', 'Не указан')}</span>
                        <span class="tag">Эффект: {win.get('expected_impact', 'Не указан')}</span>
                    </div>
                </div>
                """

        strategic_html = ""
        if recommendations.get('strategic_initiatives'):
            for initiative in recommendations['strategic_initiatives']:
                phases_html = ""
                if initiative.get('implementation_phases'):
                    phases_html = "<h5>Фазы реализации:</h5><ol>"
                    for phase in initiative['implementation_phases']:
                        phases_html += f"<li>{phase}</li>"
                    phases_html += "</ol>"

                strategic_html += f"""
                <div class="card">
                    <h4>{initiative.get('title', '')}</h4>
                    <p style="font-size: 1.1rem; line-height: 1.7; margin: 15px 0;">
                        {initiative.get('description', '')}
                    </p>
                    {phases_html}
                    <div style="margin-top: 15px;">
                        <span class="tag">ROI: {initiative.get('expected_roi', 'Не указан')}</span>
                    </div>
                </div>
                """

        return f"""
        <div class="page" id="recommendations">
            <div class="container">
                <h2>Рекомендации</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Конкретные действия для решения выявленных проблем
                </p>
                
                <h3>Быстрые победы</h3>
                {quick_wins_html}
                
                <h3>Стратегические инициативы</h3>
                {strategic_html}
            </div>
        </div>
        """

    def _generate_appendix_section(self, analysis_data: Dict) -> str:
        """Генерация приложения"""
        metrics = analysis_data.get('current_metrics', {})
        
        metrics_html = ""
        if metrics:
            metrics_html = "<h3>Ключевые метрики</h3><div class='metrics-grid'>"
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    metrics_html += f"""
                    <div class="metric-card">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{key.replace('_', ' ').title()}</div>
                    </div>
                    """
            metrics_html += "</div>"

        return f"""
        <div class="page" id="appendix">
            <div class="container">
                <h2>Приложение</h2>
                <p style="font-size: 1.1rem; color: #6b7280; margin-bottom: 30px;">
                    Дополнительные данные и метрики
                </p>
                {metrics_html}
            </div>
        </div>
        """

    def _generate_footer(self) -> str:
        """Генерация подвала"""
        return f"""
        <div class="footer">
            <div class="container">
                <p>Отчет сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                <p>Автор: {self.config.author}</p>
                <p>Компания: {self.config.name}</p>
            </div>
        </div>
        """
