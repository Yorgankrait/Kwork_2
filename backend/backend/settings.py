
import os


from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-)3e+o=#-w7#0h_-a$t+4p7t8(x)9-g_+3-jdmda3tc5pmrk#q2'
API_KEY = '447c0d33-75f4-81d9-a0d3-43e5ce98cfa0'


DEBUG = os.environ.get("DEBUG", True)

#ALLOWED_HOSTS = ['185.22.232.205', '0.0.0.0',]
ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0','185.22.232.205','offer.okonti.ru','192.168.111.14']


if os.environ.get("ALLOWED_HOSTS") is not None:
    try:
        ALLOWED_HOSTS += os.environ.get("ALLOWED_HOSTS").split(",")
    except Exception as e:
        print("Cant set ALLOWED_HOSTS, using default instead")


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_swagger',
    'corsheaders',
    'django_extensions',
    'smeta',
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


SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))
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

DB_SQLITE = "sqlite"
DB_POSTGRESQL = "postgresql"
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

DATABASES_ALL = {
    DB_SQLITE: {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    DB_POSTGRESQL: {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "NAME": os.environ.get("POSTGRES_NAME", "postgres"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
        "PORT": int(os.environ.get("POSTGRES_PORT", "5432")),
    },
}

DATABASES = {"default": DATABASES_ALL[os.environ.get("DJANGO_DB", DB_SQLITE)]}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-RU'


TIME_ZONE = 'Europe/Moscow'


USE_I18N = True


USE_L10N = True


USE_TZ = True


STATIC_URL = 'static/'
#STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
    # "/var/www/static/",
]

print(STATIC_ROOT)

#STATICFILES_DIRS = [
#    ("static", "../static"),
#]


#STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, 'static'),#
#]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# celery broker and result
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"


CSRF_TRUSTED_ORIGINS = [
    'https://offer.okonti.ru',
]


MEDIA_URL = "/upload/" #как url данных, которые требуется предоставить.
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload') #будет использоваться для управления сохраненными данными


CORS_ALLOW_ALL_ORIGINS = True
