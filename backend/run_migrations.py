#!/usr/bin/env python
"""
Скрипт для выполнения миграций с локальными настройками
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_local')
django.setup()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    
    # Если нет аргументов, по умолчанию запускаем миграции
    if len(sys.argv) == 1:
        sys.argv.extend(['makemigrations', 'smeta'])
    
    execute_from_command_line(sys.argv) 