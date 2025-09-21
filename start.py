#!/usr/bin/env python3
"""
Скрипт запуска UX Анализатора
Поддерживает несколько вариантов интерфейса
"""

import sys
import subprocess
import os
import argparse

def check_dependencies():
    """Проверка зависимостей"""
    try:
        import streamlit
        import flask
        import google.generativeai
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False

def run_streamlit():
    """Запуск Streamlit интерфейса"""
    print("🚀 Запуск Streamlit интерфейса...")
    print("📱 Откройте http://localhost:8501 в браузере")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"])

def run_flask():
    """Запуск Flask интерфейса"""
    print("🚀 Запуск Flask интерфейса...")
    print("📱 Откройте http://localhost:5000 в браузере")
    subprocess.run([sys.executable, "simple_web_app.py"])

def run_docker():
    """Запуск Docker контейнера"""
    print("🐳 Запуск Docker контейнера...")
    print("📱 Откройте http://localhost:8501 в браузере")
    subprocess.run(["docker-compose", "up", "--build"])

def main():
    parser = argparse.ArgumentParser(description="UX Анализатор V24.0")
    parser.add_argument("--interface", "-i", 
                       choices=["streamlit", "flask", "docker"], 
                       default="streamlit",
                       help="Выберите интерфейс (streamlit, flask, docker)")
    parser.add_argument("--check", "-c", action="store_true",
                       help="Только проверить зависимости")
    
    args = parser.parse_args()
    
    print("🔬 UX Анализатор V24.0")
    print("=" * 50)
    
    if args.check:
        check_dependencies()
        return
    
    if not check_dependencies():
        return
    
    if args.interface == "streamlit":
        run_streamlit()
    elif args.interface == "flask":
        run_flask()
    elif args.interface == "docker":
        run_docker()

if __name__ == "__main__":
    main()
