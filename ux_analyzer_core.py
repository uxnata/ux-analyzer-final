# -*- coding: utf-8 -*-
"""UX Analyzer Core - Основная логика анализа"""

import json
import re
import time
from typing import Dict, List, Any
from collections import defaultdict
from ux_analyzer_classes import (
    OpenRouterAPIWrapper, BriefManager, InterviewSummary, 
    ResearchFindings, CacheManager
)

# ========================================================================
# ОСНОВНОЙ КЛАСС АНАЛИЗАТОРА
# ========================================================================
class AdvancedUXAnalyzer:
    def __init__(self, api_key: str):
        self.api_wrapper = OpenRouterAPIWrapper(api_key)
        self.brief_manager = BriefManager()
        self.cache = CacheManager()
        self.interview_summaries = []

    def set_brief(self, brief_content: str):
        """Установка брифа исследования"""
        self.brief_manager.load_brief(brief_content)

    def analyze_transcripts(self, transcripts: List[str]) -> Dict:
        """Комплексный анализ транскриптов"""
        print("🧠 Начинаю глубокий анализ...")

        # Проверка количества интервью
        if len(transcripts) < 3:
            print(f"⚠️  ВНИМАНИЕ: Рекомендуется минимум 3 интервью для качественного анализа!")
            print(f"   У вас: {len(transcripts)} интервью")

        # Анализ каждого интервью
        interview_summaries = []
        for i, transcript in enumerate(transcripts):
            summary = self._deep_analyze_interview(transcript, i+1)
            interview_summaries.append(summary)

        self.interview_summaries = interview_summaries

        # Продолжение анализа
        return self._continue_analysis(interview_summaries, len(transcripts))

    def _deep_analyze_interview(self, transcript: str, interview_id: int) -> InterviewSummary:
        """Глубокий анализ одного интервью"""
        context = self.brief_manager.get_brief_context()
        
        prompt = f"""{context}

ПРОАНАЛИЗИРУЙ ЭТО ИНТЕРВЬЮ #{interview_id} И СОЗДАЙ ДЕТАЛЬНОЕ САММАРИ.

ТРАНСКРИПТ ИНТЕРВЬЮ:
{transcript[:8000]}

СОЗДАЙ JSON СТРУКТУРУ:
{{
    "respondent_profile": {{
        "age_range": "возрастная группа",
        "profession": "профессия",
        "tech_literacy": "уровень технической грамотности",
        "experience_level": "опыт использования продукта",
        "main_goals": ["цель 1", "цель 2"],
        "pain_level": "уровень фрустрации (1-10)"
    }},
    "key_themes": [
        {{
            "theme": "название темы",
            "description": "описание",
            "quotes": ["цитата 1", "цитата 2"],
            "importance": "важность (1-10)"
        }}
    ],
    "pain_points": [
        {{
            "pain": "описание проблемы",
            "severity": "серьезность (1-10)",
            "frequency": "частота упоминаний",
            "quotes": ["цитата 1", "цитата 2"],
            "impact": "влияние на пользователя"
        }}
    ],
    "needs": [
        {{
            "need": "потребность",
            "type": "явная/скрытая",
            "priority": "приоритет (1-10)",
            "quotes": ["цитата 1", "цитата 2"]
        }}
    ],
    "insights": [
        "инсайт 1",
        "инсайт 2",
        "инсайт 3"
    ],
    "emotional_journey": [
        {{
            "moment": "момент в путешествии",
            "emotion": "эмоция",
            "trigger": "триггер",
            "intensity": "интенсивность (1-10)",
            "quote": "цитата"
        }}
    ],
    "contradictions": [
        "противоречие 1",
        "противоречие 2"
    ],
    "quotes": [
        {{
            "text": "полная цитата (минимум 50 слов)",
            "context": "контекст",
            "importance": "важность (1-10)",
            "theme": "к какой теме относится"
        }}
    ],
    "business_pains": [
        {{
            "pain": "бизнес-проблема",
            "impact": "влияние на бизнес",
            "quotes": ["цитата 1", "цитата 2"]
        }}
    ],
    "user_problems": [
        {{
            "problem": "пользовательская проблема",
            "severity": "серьезность (1-10)",
            "quotes": ["цитата 1", "цитата 2"]
        }}
    ],
    "opportunities": [
        "возможность 1",
        "возможность 2"
    ],
    "sentiment_score": "общий сентимент (-10 до +10)",
    "brief_related_findings": {{
        "goals_mentioned": ["цель 1", "цель 2"],
        "questions_answered": ["вопрос 1", "вопрос 2"],
        "metrics_impact": ["метрика 1", "метрика 2"]
    }}
}}

КРИТИЧЕСКИ ВАЖНО:
- Используй ТОЛЬКО факты из интервью
- Каждая цитата должна быть ТОЧНОЙ (минимум 50 слов)
- НЕ придумывай детали - только из данных
- Связывай с целями и вопросами брифа
- Анализируй эмоциональное состояние респондента"""

        try:
            response = self.api_wrapper.generate_content(prompt, max_tokens=4000)
            data = self.api_wrapper.extract_json(response)
            
            # Создаем InterviewSummary
            return InterviewSummary(
                interview_id=interview_id,
                respondent_profile=data.get('respondent_profile', {}),
                key_themes=data.get('key_themes', []),
                pain_points=data.get('pain_points', []),
                needs=data.get('needs', []),
                insights=data.get('insights', []),
                emotional_journey=data.get('emotional_journey', []),
                contradictions=data.get('contradictions', []),
                quotes=data.get('quotes', []),
                business_pains=data.get('business_pains', []),
                user_problems=data.get('user_problems', []),
                opportunities=data.get('opportunities', []),
                sentiment_score=float(data.get('sentiment_score', 0)),
                brief_related_findings=data.get('brief_related_findings', {})
            )
        except Exception as e:
            print(f"❌ Ошибка при анализе интервью {interview_id}: {e}")
            return self._create_empty_summary(interview_id)

    def _create_empty_summary(self, interview_id: int) -> InterviewSummary:
        """Создание пустого саммари при ошибке"""
        return InterviewSummary(
            interview_id=interview_id,
            respondent_profile={},
            key_themes=[],
            pain_points=[],
            needs=[],
            insights=[],
            emotional_journey=[],
            contradictions=[],
            quotes=[],
            business_pains=[],
            user_problems=[],
            opportunities=[],
            sentiment_score=0.0,
            brief_related_findings={}
        )

    def _continue_analysis(self, interview_summaries: List[InterviewSummary], total_interviews: int) -> Dict:
        """Продолжение анализа после обработки интервью"""
        print("🔄 Продолжаю анализ...")

        # Генерация текущих метрик
        current_metrics = self._generate_current_metrics(interview_summaries)

        # Кросс-анализ интервью
        cross_analysis = self._cross_analyze_interviews(interview_summaries)

        # Выявление поведенческих паттернов
        patterns = self._identify_behavioral_patterns(interview_summaries, cross_analysis)

        # Сегментация аудитории
        segments = self._segment_audience(interview_summaries, patterns)

        # Создание персон
        personas = self._create_personas(segments, interview_summaries)

        # Генерация финальных находок
        findings = self._generate_final_findings(
            interview_summaries, cross_analysis, patterns, segments, personas
        )

        findings.current_metrics = current_metrics

        # Генерация рекомендаций
        recommendations = self._generate_recommendations(findings.key_insights)

        # Ответы на вопросы брифа
        brief_answers = self._analyze_brief_questions(interview_summaries, findings)
        findings.brief_answers = brief_answers

        # Оценка достижения целей
        goal_achievement = self._assess_goal_achievement(findings, interview_summaries)
        findings.goal_achievement = goal_achievement

        return {
            'base_analysis': {
                'segments': segments,
                'problems': findings.key_insights,
                'insights': self._format_insights_for_report(findings.key_insights),
                'user_journey_issues': []
            },
            'recommendations': recommendations,
            'interview_summaries': interview_summaries,
            'findings': findings,
            'total_interviews': total_interviews,
            'current_metrics': current_metrics,
            'personas': personas,
            'brief_data': self.brief_manager.brief_data if self.brief_manager.has_brief else None,
            'brief_answers': brief_answers,
            'goal_achievement': goal_achievement
        }

    def _generate_current_metrics(self, summaries: List[InterviewSummary]) -> Dict:
        """Генерация текущих метрик"""
        if not summaries:
            return {}

        total_pains = sum(len(s.pain_points) for s in summaries)
        total_needs = sum(len(s.needs) for s in summaries)
        total_emotions = sum(len(s.emotional_journey) for s in summaries)
        
        positive_emotions = sum(1 for s in summaries for e in s.emotional_journey 
                              if isinstance(e, dict) and isinstance(e.get('intensity', 0), (int, float)) and e.get('intensity', 0) > 5)
        negative_emotions = sum(1 for s in summaries for e in s.emotional_journey 
                              if isinstance(e, dict) and isinstance(e.get('intensity', 0), (int, float)) and e.get('intensity', 0) < 5)

        # Оценка NPS
        sentiments = [s.sentiment_score for s in summaries if s.sentiment_score != 0]
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            estimated_nps = int(avg_sentiment * 10)
        else:
            estimated_nps = 'Недостаточно данных'

        # Риск оттока
        avg_pains = total_pains / len(summaries) if summaries else 0
        if isinstance(estimated_nps, int):
            if estimated_nps < -30 or avg_pains > 7:
                churn_risk = 'Критический'
            elif estimated_nps < 0 or avg_pains > 5:
                churn_risk = 'Высокий'
            elif estimated_nps < 30 or avg_pains > 3:
                churn_risk = 'Средний'
            else:
                churn_risk = 'Низкий'
        else:
            churn_risk = 'Средний' if avg_pains > 4 else 'Низкий'

        return {
            'estimated_nps': estimated_nps,
            'churn_risk': churn_risk,
            'avg_pains_per_user': round(avg_pains, 1),
            'avg_needs_per_user': round(total_needs / len(summaries), 1) if summaries else 0,
            'negative_emotion_ratio': round(negative_emotions / total_emotions * 100 if total_emotions > 0 else 0),
            'total_emotions_analyzed': total_emotions,
            'sample_size': len(summaries)
        }

    def _cross_analyze_interviews(self, summaries: List[InterviewSummary]) -> Dict:
        """Кросс-анализ интервью"""
        try:
            # Собираем все проблемы
            all_pains = []
            for summary in summaries:
                if hasattr(summary, 'pain_points') and summary.pain_points:
                    for pain in summary.pain_points:
                        if isinstance(pain, dict):
                            all_pains.append({
                                'pain': pain.get('pain', ''),
                                'severity': pain.get('severity', 0),
                                'interview_id': getattr(summary, 'interview_id', 0),
                                'quotes': pain.get('quotes', [])
                            })
        except Exception as e:
            print(f"Ошибка при сборе проблем: {e}")
            all_pains = []

        try:
            # Группируем похожие проблемы
            from collections import defaultdict
            pain_groups = defaultdict(list)
            for pain in all_pains:
                pain_text = pain.get('pain', '').lower() if pain.get('pain') else ''
                # Простая группировка по ключевым словам
                for key in ['интерфейс', 'навигация', 'скорость', 'ошибка', 'сложно', 'непонятно']:
                    if key in pain_text:
                        pain_groups[key].append(pain)
                        break
                else:
                    pain_groups['другое'].append(pain)

            return {
                'pain_groups': dict(pain_groups),
                'total_pains': len(all_pains),
                'unique_pains': len(pain_groups)
            }
        except Exception as e:
            print(f"Ошибка при группировке проблем: {e}")
            return {
                'pain_groups': {},
                'total_pains': 0,
                'unique_pains': 0
            }

    def _identify_behavioral_patterns(self, summaries: List[InterviewSummary], cross_analysis: Dict) -> List[Dict]:
        """Выявление поведенческих паттернов"""
        patterns = []
        
        # Паттерн: повторяющиеся проблемы
        for group_name, pains in cross_analysis.get('pain_groups', {}).items():
            if len(pains) > 1:
                # Безопасно получаем максимальную серьезность
                severities = []
                for p in pains:
                    severity = p.get('severity', 0)
                    if isinstance(severity, str):
                        try:
                            severity = int(severity)
                        except (ValueError, TypeError):
                            severity = 0
                    severities.append(severity)
                
                patterns.append({
                    'pattern': f"Повторяющаяся проблема: {group_name}",
                    'frequency': len(pains),
                    'severity': max(severities) if severities else 0,
                    'description': f"Проблема '{group_name}' встречается в {len(pains)} интервью"
                })

        return patterns

    def _segment_audience(self, summaries: List[InterviewSummary], patterns: List[Dict]) -> List[Dict]:
        """Сегментация аудитории"""
        segments = []
        
        # Простая сегментация по уровню фрустрации
        high_frustration = [s for s in summaries if isinstance(s.sentiment_score, (int, float)) and s.sentiment_score < -3]
        medium_frustration = [s for s in summaries if isinstance(s.sentiment_score, (int, float)) and -3 <= s.sentiment_score <= 3]
        low_frustration = [s for s in summaries if isinstance(s.sentiment_score, (int, float)) and s.sentiment_score > 3]

        if high_frustration:
            segments.append({
                'name': 'Высокая фрустрация',
                'size': len(high_frustration),
                'characteristics': 'Пользователи с высоким уровнем недовольства',
                'needs': 'Срочные улучшения интерфейса'
            })

        if medium_frustration:
            segments.append({
                'name': 'Средняя фрустрация',
                'size': len(medium_frustration),
                'characteristics': 'Пользователи с умеренным уровнем удовлетворенности',
                'needs': 'Постепенные улучшения'
            })

        if low_frustration:
            segments.append({
                'name': 'Низкая фрустрация',
                'size': len(low_frustration),
                'characteristics': 'Довольные пользователи',
                'needs': 'Поддержание качества'
            })

        return segments

    def _create_personas(self, segments: List[Dict], summaries: List[InterviewSummary]) -> List[Dict]:
        """Создание персон"""
        personas = []
        
        for i, segment in enumerate(segments, 1):
            # Находим репрезентативные интервью для сегмента
            segment_summaries = []
            if segment['name'] == 'Высокая фрустрация':
                segment_summaries = [s for s in summaries if isinstance(s.sentiment_score, (int, float)) and s.sentiment_score < -3]
            elif segment['name'] == 'Средняя фрустрация':
                segment_summaries = [s for s in summaries if isinstance(s.sentiment_score, (int, float)) and -3 <= s.sentiment_score <= 3]
            else:
                segment_summaries = [s for s in summaries if isinstance(s.sentiment_score, (int, float)) and s.sentiment_score > 3]

            if segment_summaries:
                # Берем первое интервью как основу для персоны
                base_summary = segment_summaries[0]
                profile = base_summary.respondent_profile

                persona = {
                    'persona_id': f'P{i:03d}',
                    'name': f"Пользователь {i}",
                    'based_on_interviews': [s.interview_id for s in segment_summaries[:3]],
                    'tagline': f"Представитель сегмента '{segment['name']}'",
                    'description': f"Пользователь из сегмента '{segment['name']}' с {segment['characteristics']}",
                    'demographics': {
                        'age_range': profile.get('age_range', 'Не указано'),
                        'profession': profile.get('profession', 'Не указано'),
                        'tech_literacy': profile.get('tech_literacy', 'Не указано')
                    },
                    'goals': profile.get('main_goals', []),
                    'frustrations': [p.get('pain', '') for p in base_summary.pain_points[:3]],
                    'needs': [n.get('need', '') for n in base_summary.needs[:3]],
                    'real_quotes': [q.get('text', '') for q in base_summary.quotes[:3] if q.get('text')],
                    'typical_scenario': f"Типичный сценарий для {segment['name']}"
                }
                personas.append(persona)

        return personas

    def _generate_final_findings(self, summaries: List[InterviewSummary], cross_analysis: Dict, 
                                patterns: List[Dict], segments: List[Dict], personas: List[Dict]) -> ResearchFindings:
        """Генерация финальных находок"""
        
        # Собираем все инсайты
        all_insights = []
        for summary in summaries:
            for insight in summary.insights:
                all_insights.append(insight)

        # Собираем все проблемы
        all_pains = []
        for summary in summaries:
            for pain in summary.pain_points:
                if isinstance(pain, dict):
                    # Безопасно получаем severity
                    severity = pain.get('severity', 5)
                    if isinstance(severity, str):
                        try:
                            severity = int(severity)
                        except (ValueError, TypeError):
                            severity = 5
                    
                    all_pains.append({
                        'problem_title': pain.get('pain', ''),
                        'problem_description': pain.get('impact', ''),
                        'severity': severity,
                        'quotes': pain.get('quotes', []),
                        'affected_percentage': f"{len([s for s in summaries if any(p.get('pain', '') == pain.get('pain', '') for p in s.pain_points)]) / len(summaries) * 100:.0f}%"
                    })

        return ResearchFindings(
            executive_summary="Анализ пользовательских интервью выявил ключевые проблемы и возможности для улучшения продукта.",
            key_insights=all_pains,
            behavioral_patterns=patterns,
            user_segments=segments,
            pain_points_map=cross_analysis.get('pain_groups', {}),
            opportunities=[o for s in summaries for o in s.opportunities],
            recommendations=[],
            risks=[],
            personas=personas
        )

    def _generate_recommendations(self, insights: List[Dict]) -> Dict:
        """Генерация рекомендаций"""
        context = self.brief_manager.get_brief_context()
        
        prompt = f"""{context}

На основе выявленных проблем создай КОНКРЕТНЫЕ рекомендации.

КЛЮЧЕВЫЕ ПРОБЛЕМЫ:
{json.dumps(insights[:5], ensure_ascii=False, indent=2)}

Верни JSON:
{{
    "quick_wins": [
        {{
            "title": "Конкретное решение",
            "description": "Что именно сделать",
            "implementation_steps": ["Шаг 1", "Шаг 2", "Шаг 3"],
            "expected_impact": "Ожидаемый эффект",
            "timeline": "Срок реализации"
        }}
    ],
    "strategic_initiatives": [
        {{
            "title": "Стратегическая инициатива",
            "description": "Детальное описание",
            "expected_roi": "Ожидаемая отдача",
            "implementation_phases": ["Фаза 1", "Фаза 2"]
        }}
    ]
}}"""

        try:
            response = self.api_wrapper.generate_content(prompt, max_tokens=3000)
            return self.api_wrapper.extract_json(response)
        except Exception as e:
            print(f"❌ Ошибка при генерации рекомендаций: {e}")
            return {"quick_wins": [], "strategic_initiatives": []}

    def _analyze_brief_questions(self, summaries: List[InterviewSummary], findings: ResearchFindings) -> Dict:
        """Анализ ответов на вопросы брифа"""
        if not self.brief_manager.has_brief:
            return {}

        questions = self.brief_manager.get_questions_for_analysis()
        if not questions:
            return {}

        # Собираем все цитаты для контекста
        all_quotes = []
        for summary in summaries:
            for quote in summary.quotes:
                if isinstance(quote, dict) and quote.get('text'):
                    all_quotes.append(f"Интервью {summary.interview_id}: {quote['text']}")

        prompt = f"""Ответь на каждый вопрос из брифа на основе анализа интервью.

ВОПРОСЫ БРИФА:
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions))}

ДАННЫЕ ИЗ ИНТЕРВЬЮ:
{chr(10).join(all_quotes[:10])}

Верни JSON:
{{
    "answers": [
        {{
            "question": "Вопрос из брифа",
            "answer": "Подробный ответ с цитатами",
            "supporting_quotes": ["цитата 1", "цитата 2"],
            "confidence": "уровень уверенности (1-10)"
        }}
    ]
}}"""

        try:
            response = self.api_wrapper.generate_content(prompt, max_tokens=4000)
            return self.api_wrapper.extract_json(response)
        except Exception as e:
            print(f"❌ Ошибка при анализе вопросов брифа: {e}")
            return {"answers": []}

    def _assess_goal_achievement(self, findings: ResearchFindings, summaries: List[InterviewSummary]) -> Dict:
        """Оценка достижения целей"""
        if not self.brief_manager.has_brief:
            return {}

        goals = self.brief_manager.get_goals_for_analysis()
        if not goals:
            return {}

        return {
            "goals": [
                {
                    "goal": goal,
                    "achieved": "Частично",
                    "evidence": "Найдены соответствующие данные в интервью",
                    "next_steps": "Требуется дополнительный анализ"
                }
                for goal in goals
            ]
        }

    def _format_insights_for_report(self, insights: List[Dict]) -> List[Dict]:
        """Форматирование инсайтов для отчета"""
        formatted_insights = []

        for insight in insights:
            formatted_insights.append({
                "title": insight.get("problem_title", ""),
                "description": insight.get("problem_description", ""),
                "severity": insight.get("severity", "medium"),
                "quotes": insight.get("quotes", []),
                "affected_percentage": insight.get("affected_percentage", "")
            })

        return formatted_insights
