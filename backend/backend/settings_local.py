"""
Локальные настройки для разработки.
Этот файл не должен храниться в git репозитории.
"""
import os
from pathlib import Path

# Базовые настройки из основного файла settings.py
from .settings import *

# Включаем режим отладки
DEBUG = True

# Используем SQLite для локальной разработки
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Изменяем URL для локальной разработки
SITE_URL = "http://127.0.0.1:8000"

# Настройки для Redis и Celery для локальной разработки
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# Разрешаем доступ с localhost
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']

# Директория для хранения логов в локальной разработке
LOG_DIR = BASE_DIR / 'logs_dev'
LOG_DIR.mkdir(exist_ok=True)

# Настройки логирования для разработки
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'app.log',
            'maxBytes': 1024 * 1024,  # 1MB
            'backupCount': 3,  # Храним до 3 файлов
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
} 