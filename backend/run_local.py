#!/usr/bin/env python
"""
Скрипт для запуска Django сервера с локальными настройками
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_local')
django.setup()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    
    # По умолчанию запускаем сервер разработки
    if len(sys.argv) == 1:
        sys.argv.append('runserver')
        sys.argv.append('0.0.0.0:8000')
        
    execute_from_command_line(sys.argv) 