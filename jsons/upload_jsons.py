#!/usr/bin/env python
"""
Скрипт для массовой загрузки JSON файлов в сметы
Для запуска на PythonAnywhere
"""
import os
import json
import time
import requests
from pathlib import Path

# URL сервиса
BASE_URL = "https://yorgankrait.pythonanywhere.com"

def send_json_to_server(json_data, filename):
    """Отправляет JSON данные на сервер"""
    try:
        # Подготавливаем данные для отправки
        payload = {"Данные": json.dumps(json_data)}

        # Отправляем запрос
        print(f"\n=== Отправка данных из файла: {filename} ===")
        response = requests.post(f"{BASE_URL}/api/smeta_create/", json=payload)

        print(f"Статус ответа: {response.status_code}")
        print(f"Текст ответа: {response.text}")

        if response.status_code == 201:
            print(f"✅ Смета успешно создана!")
            print(f"🔗 Ссылка на смету: {response.text}")
            return True
        else:
            print(f"❌ Ошибка создания сметы")
            return False

    except Exception as e:
        print(f"❌ Ошибка при обработке файла {filename}: {str(e)}")
        return False

def main():
    # Путь к директории с JSON файлами на PythonAnywhere
    json_dir = Path("/home/Yorgankrait/Kwork_2/jsons")

    # Создаем директорию, если её нет
    json_dir.mkdir(exist_ok=True)

    # Получаем список JSON файлов
    json_files = sorted(json_dir.glob("*.json"))
    total_files = len(json_files)

    print(f"\nНайдено файлов для отправки: {total_files}")

    # Счетчики успешных и неуспешных отправок
    success_count = 0
    failed_count = 0

    # Отправляем каждый файл
    for i, file_path in enumerate(json_files, 1):
        print(f"\nОбработка файла {i}/{total_files}: {file_path.name}")

        try:
            # Читаем JSON файл
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if send_json_to_server(data, file_path.name):
                success_count += 1
            else:
                failed_count += 1

        except Exception as e:
            print(f"❌ Ошибка при чтении файла {file_path.name}: {str(e)}")
            failed_count += 1

        # Делаем паузу между запросами
        if i < total_files:
            time.sleep(2)

    # Выводим итоговую статистику
    print("\n=== Итоги отправки ===")
    print(f"Всего файлов: {total_files}")
    print(f"Успешно отправлено: {success_count}")
    print(f"Ошибок: {failed_count}")

if __name__ == "__main__":
    main()