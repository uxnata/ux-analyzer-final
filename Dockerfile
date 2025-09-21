FROM python:3.9-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы
COPY requirements.txt .
COPY ux_analyzer_core_ebicya.ipynb .
COPY streamlit_app.py .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем директорию для данных
RUN mkdir -p /app/data

# Открываем порт
EXPOSE 8501

# Команда запуска
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
