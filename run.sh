#!/bin/bash

echo "🚀 Запуск UX Анализатора..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.9+"
    exit 1
fi

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден. Установите pip"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt

# Запускаем Streamlit
echo "🌐 Запуск веб-интерфейса..."
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
