# 🔬 UX Анализатор V24.0

Веб-интерфейс для анализа транскриптов пользовательских интервью с использованием Google Gemini AI.

## 🚀 Быстрый запуск

### Вариант 1: Универсальный скрипт (рекомендуется)

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Запустите с выбором интерфейса
python3 start.py --interface streamlit  # Streamlit (по умолчанию)
python3 start.py --interface flask      # Flask + HTML
python3 start.py --interface docker     # Docker контейнер
```

### Вариант 2: Прямой запуск

```bash
# Streamlit (самый быстрый)
streamlit run streamlit_app.py

# Flask + HTML
python3 simple_web_app.py

# Готовый скрипт
./run.sh
```

### Вариант 3: Docker (для изоляции)

```bash
# Сборка и запуск
docker-compose up --build

# Или только сборка
docker build -t ux-analyzer .
docker run -p 8501:8501 ux-analyzer
```

## 📋 Требования

- Python 3.9+
- Google Gemini API ключ (получить на https://makersuite.google.com/app/apikey)

## 🎯 Как использовать

1. **Откройте интерфейс** в браузере (обычно http://localhost:8501)
2. **Введите API ключ** Gemini
3. **Настройте параметры** (название компании, отчета, автор)
4. **Загрузите транскрипты** интервью (файлы .txt или .md)
5. **Загрузите бриф** (опционально)
6. **Нажмите "Начать анализ"**

## 📁 Структура файлов

```
ebicya/
├── ux_analyzer_core_ebicya.ipynb  # Основной анализатор (Jupyter)
├── streamlit_app.py               # Веб-интерфейс
├── requirements.txt               # Python зависимости
├── Dockerfile                     # Docker конфигурация
├── docker-compose.yml            # Docker Compose
├── run.sh                        # Скрипт запуска
└── README.md                     # Документация
```

## 🔧 Возможности

- **Анализ транскриптов** пользовательских интервью
- **Генерация инсайтов** и рекомендаций
- **Создание детальных отчетов** с визуализациями
- **Поддержка брифа** исследования
- **Параллельная обработка** для ускорения анализа
- **Веб-интерфейс** для удобного использования

## 🌐 Доступ к интерфейсу

После запуска интерфейс будет доступен по адресу:

### Streamlit (рекомендуется)
- **Локально**: http://localhost:8501
- **В сети**: http://YOUR_IP:8501
- **Особенности**: Современный интерфейс, автоматическое обновление, встроенные виджеты

### Flask + HTML
- **Локально**: http://localhost:5000
- **В сети**: http://YOUR_IP:5000
- **Особенности**: Простой HTML интерфейс, drag & drop загрузка файлов

### Docker
- **Локально**: http://localhost:8501
- **В сети**: http://YOUR_IP:8501
- **Особенности**: Изолированная среда, легкое развертывание

## 🐳 Docker команды

```bash
# Сборка образа
docker build -t ux-analyzer .

# Запуск контейнера
docker run -p 8501:8501 ux-analyzer

# Остановка
docker stop $(docker ps -q --filter ancestor=ux-analyzer)

# Удаление
docker rmi ux-analyzer
```

## 📞 Поддержка

При возникновении проблем проверьте:
1. Установлены ли все зависимости
2. Корректность API ключа Gemini
3. Формат загружаемых файлов (.txt, .md)
4. Логи в консоли для диагностики ошибок
