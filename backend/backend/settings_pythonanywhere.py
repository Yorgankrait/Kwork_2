"""
Настройки для PythonAnywhere.
"""
import os
from pathlib import Path

# Путь к проекту
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ
SECRET_KEY = '&$r8)##ij4jwj@(=$aj^5!pl)=@sw8n6bjan&uja5kaj_ex)d6'

# Отключаем режим отладки
DEBUG = False

# Установки приложений
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_celery_beat',
    'drf_yasg',
    'corsheaders',
    'django_extensions',
    'smeta.apps.SmetaConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# База данных SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# URL сайта
SITE_URL = "https://yorgankrait.pythonanywhere.com"

# Настройки для Redis и Celery
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ['json']

# Разрешенные хосты
ALLOWED_HOSTS = ['yorgankrait.pythonanywhere.com']
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['https://yorgankrait.pythonanywhere.com']

# Настройки языка и времени
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Директория для хранения логов
LOG_DIR = '/home/Yorgankrait/Kwork_2/logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Настройки статических файлов
STATIC_URL = '/static/'
STATIC_ROOT = '/home/Yorgankrait/Kwork_2/static'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/Yorgankrait/Kwork_2/media'

# Настройки безопасности
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'app.log'),
            'maxBytes': 1024 * 1024,  # 1MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Настройки Celery для периодических задач
CELERY_BEAT_SCHEDULE = {
    'delete_old_logs_task': {
        'task': 'smeta.tasks.delete_old_logs_task',
        'schedule': 'crontab(hour=0, minute=0)',  # Запуск каждый день в полночь
    },
    'scan_logs_directory_task': {
        'task': 'smeta.tasks.scan_logs_task',
        'schedule': 'crontab(minute="*/60")',  # Запуск каждые 60 минут
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'