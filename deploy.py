#!/usr/bin/env python3
"""
Автоматическое развертывание UX Анализатора на Streamlit Cloud
"""

import requests
import json
import time
import webbrowser
from pathlib import Path

def main():
    print("🚀 UX Анализатор V24.0 - Автоматическое развертывание")
    print("=" * 60)
    
    # Информация о репозитории
    repo_url = "https://github.com/uxnata/ux-analyzer"
    main_file = "app.py"
    
    print(f"📁 Репозиторий: {repo_url}")
    print(f"📄 Главный файл: {main_file}")
    print()
    
    # Проверяем файлы
    if not Path("app.py").exists():
        print("❌ Файл app.py не найден!")
        return
    
    if not Path("requirements.txt").exists():
        print("❌ Файл requirements.txt не найден!")
        return
    
    print("✅ Все необходимые файлы найдены")
    print()
    
    # Открываем Streamlit Cloud
    print("🌐 Открываем Streamlit Cloud...")
    streamlit_url = "https://share.streamlit.io"
    webbrowser.open(streamlit_url)
    
    print("📋 Инструкции для развертывания:")
    print("-" * 40)
    print("1. Нажмите 'New app'")
    print("2. Выберите репозиторий: uxnata/ux-analyzer")
    print("3. Главный файл: app.py")
    print("4. Нажмите 'Deploy'")
    print("-" * 40)
    print()
    
    # Ждем немного
    print("⏳ Ожидание развертывания...")
    print("(Это может занять 2-3 минуты)")
    
    # Проверяем статус развертывания
    for i in range(30):  # 30 попыток по 10 секунд = 5 минут
        try:
            # Пробуем получить информацию о приложении
            app_url = f"https://ux-analyzer-uxnata.streamlit.app"
            
            response = requests.get(app_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Приложение развернуто успешно!")
                print(f"🔗 Ссылка: {app_url}")
                print()
                print("🎉 Готово! Отправьте эту ссылку коллегам:")
                print(f"   {app_url}")
                return
            
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Попытка {i+1}/30...")
        time.sleep(10)
    
    print("⚠️  Автоматическая проверка не удалась")
    print("🔗 Проверьте вручную: https://share.streamlit.io")
    print("📱 Ищите приложение: ux-analyzer-uxnata")

if __name__ == "__main__":
    main()
