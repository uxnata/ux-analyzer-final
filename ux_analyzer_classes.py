# -*- coding: utf-8 -*-
"""UX Analyzer Classes - Основные классы для анализа"""

import json
import re
import time
import hashlib
import pickle
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from collections import defaultdict
import requests

# ========================================================================
# ДАТАКЛАССЫ
# ========================================================================
@dataclass
class CompanyConfig:
    name: str = "Company"
    report_title: str = "UX Research Report"
    author: str = "Research Team"

@dataclass
class InterviewSummary:
    """Структура саммари интервью"""
    interview_id: int
    respondent_profile: Dict[str, Any]
    key_themes: List[Dict[str, Any]]
    pain_points: List[Dict[str, Any]]
    needs: List[Dict[str, Any]]
    insights: List[str]
    emotional_journey: List[Dict[str, Any]]
    contradictions: List[str]
    quotes: List[Dict[str, Any]]
    business_pains: List[Dict[str, Any]] = field(default_factory=list)
    user_problems: List[Dict[str, Any]] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    sentiment_score: float = field(default=0.0)
    brief_related_findings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResearchFindings:
    """Структура результатов исследования"""
    executive_summary: str
    key_insights: List[Dict[str, Any]]
    behavioral_patterns: List[Dict[str, Any]]
    user_segments: List[Dict[str, Any]]
    pain_points_map: Dict[str, List[Dict[str, Any]]]
    opportunities: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    risks: List[Dict[str, Any]]
    personas: List[Dict[str, Any]]
    current_metrics: Dict[str, Any] = field(default_factory=dict)
    brief_answers: Dict[str, Any] = field(default_factory=dict)
    goal_achievement: Dict[str, Any] = field(default_factory=dict)

# ========================================================================
# КЛАСС ДЛЯ УПРАВЛЕНИЯ БРИФОМ
# ========================================================================
class BriefManager:
    """Класс для управления брифом исследования"""

    def __init__(self):
        self.brief_data = {
            'research_goals': [],
            'research_questions': [],
            'target_audience': '',
            'business_context': '',
            'success_metrics': [],
            'constraints': []
        }
        self.has_brief = False

    def load_brief(self, content: str):
        """Загрузка и парсинг брифа"""
        self.has_brief = True

        # Простой парсер для текстового брифа
        lines = content.strip().split('\n')
        current_section = None

        section_markers = {
            'цели': 'research_goals',
            'goals': 'research_goals',
            'вопросы': 'research_questions',
            'questions': 'research_questions',
            'аудитория': 'target_audience',
            'audience': 'target_audience',
            'контекст': 'business_context',
            'context': 'business_context',
            'метрики': 'success_metrics',
            'metrics': 'success_metrics',
            'ограничения': 'constraints',
            'constraints': 'constraints'
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Проверяем, не начало ли это новой секции
            line_lower = line.lower()
            for marker, section in section_markers.items():
                if marker in line_lower:
                    current_section = section
                    break
            else:
                # Это контент секции
                if current_section:
                    if current_section == 'target_audience' or current_section == 'business_context':
                        # Для этих секций сохраняем как строку
                        if self.brief_data[current_section]:
                            self.brief_data[current_section] += ' ' + line
                        else:
                            self.brief_data[current_section] = line
                    else:
                        # Для остальных - как список
                        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                            line = line[1:].strip()
                        if line:
                            self.brief_data[current_section].append(line)

    def get_brief_context(self):
        """Получение контекста брифа для промптов"""
        if not self.has_brief:
            return ""

        context = "<research_context>\n"
        context += "КРИТИЧЕСКИ ВАЖНО: Все выводы должны отвечать на вопросы и достигать целей из этого брифа!\n\n"

        if self.brief_data['research_goals']:
            context += f"ЦЕЛИ ИССЛЕДОВАНИЯ (ОБЯЗАТЕЛЬНО достичь каждую):\n"
            for i, goal in enumerate(self.brief_data['research_goals'], 1):
                context += f"{i}. {goal}\n"

        if self.brief_data['research_questions']:
            context += f"\nИССЛЕДОВАТЕЛЬСКИЕ ВОПРОСЫ (ОБЯЗАТЕЛЬНО ответить на каждый):\n"
            for i, question in enumerate(self.brief_data['research_questions'], 1):
                context += f"{i}. {question}\n"

        if self.brief_data['target_audience']:
            context += f"\nЦЕЛЕВАЯ АУДИТОРИЯ:\n{self.brief_data['target_audience']}\n"

        if self.brief_data['business_context']:
            context += f"\nБИЗНЕС-КОНТЕКСТ:\n{self.brief_data['business_context']}\n"

        if self.brief_data['success_metrics']:
            context += f"\nМЕТРИКИ УСПЕХА (оценить влияние на каждую):\n"
            for metric in self.brief_data['success_metrics']:
                context += f"- {metric}\n"

        context += "\nВАЖНО: Каждый вывод должен быть подкреплен ТОЧНЫМИ ЦИТАТАМИ из интервью!\n"
        context += "</research_context>\n\n"

        return context

    def get_questions_for_analysis(self):
        """Получение вопросов для анализа"""
        return self.brief_data['research_questions']

    def get_goals_for_analysis(self):
        """Получение целей для анализа"""
        return self.brief_data['research_goals']

# ========================================================================
# OPENROUTER API WRAPPER
# ========================================================================
class OpenRouterAPIWrapper:
    """Обертка для безопасных вызовов OpenRouter API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate_content(self, prompt: str, model: str = "anthropic/claude-3.5-sonnet", max_tokens: int = 6000) -> str:
        """Генерация контента через OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    def extract_json(self, text: str) -> Dict:
        """Извлечение JSON из текста ответа"""
        try:
            # Ищем JSON в тексте
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Если JSON не найден, возвращаем структурированный ответ
                return {"content": text}
        except Exception:
            return {"content": text}

# ========================================================================
# КЛАСС ДЛЯ КЭШИРОВАНИЯ
# ========================================================================
class CacheManager:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def get_hash(self, data: str) -> str:
        """Генерация хеша для данных"""
        return hashlib.md5(data.encode()).hexdigest()

    def get(self, key: str):
        """Получить из кэша"""
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None

    def set(self, key: str, value: Any):
        """Сохранить в кэш"""
        cache_file = self.cache_dir / f"{key}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(value, f)
