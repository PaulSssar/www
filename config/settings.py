
from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-4b-y4(ef+^5eh!*x3(c@l4=!&^kqbazsggyjlq68^74u%u)$t#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['rosritual-online.ru', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'drf_yasg',
    'filer',
    'easy_thumbnails',
    'mptt',

    'ritual',
    'ritual_performer',
    'order',
    'settings',
    'pay'
]
# BASIC_AUTH_USERNAME = 'username'
# BASIC_AUTH_PASSWORD = 'password-18'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'config.middleware.BasicAuthMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Убедитесь, что это правильный путь
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'demodb',
#         'USER': 'demouser',
#         'PASSWORD': 'neighbours2290',
#         'HOST': 'postgres',
#         # 'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Увеличьте тайм-аут блокировки (значение в секундах)
        }
    }
}


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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Asia/Yekaterinburg'

USE_I18N = True

USE_TZ = True

MINIO_ACCESS_KEY = None
MINIO_SECRET_KEY = None

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.AllowAny',
        ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 100,
    # 'PAGE_SIZE_PARAM': 'page_size'
}
AUTHENTICATION_BACKENDS = [
    # другие бэкенды аутентификации
    'django.contrib.auth.backends.ModelBackend',
    'ritual.views.CustomBackend',
]
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=3000),  # Продолжительность жизни токена доступа
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),  # Продолжительность жизни токена обновления
    'ROTATE_REFRESH_TOKENS': False,  # Обновлять ли refresh token при каждом запросе
    'BLACKLIST_AFTER_ROTATION': True,  # Добавлять ли старый токен в черный список при обновлении
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800
DATA_UPLOAD_MAX_NUMBER_FIELDS = 15000


AUTH_USER_MODEL = 'ritual.UserAccounts'


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


import os

# ...

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
APPEND_SLASH = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'rosrituals@ya.ru'
EMAIL_HOST_PASSWORD = 'usxuususjzzokyjr'

YOOKASSA_SHOP_ID = 285554
YOOKASSA_SECRET_KEY = 'test_MeMDVxc5xOc2EaeyI6t5EtPxMwJGBZYL92Mrp1Yw640'