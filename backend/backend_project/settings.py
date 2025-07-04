"""
Django settings for backend_project project.
Generated by 'django-admin startproject' using Django 5.0.4.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-kynu+j6iyr@rb6uf(#mx-t-32nhlsgx=%*#b+@dhiibi$8+mox'
DEBUG = True
ALLOWED_HOSTS = []

# ------------------------------------------------------------------
# 1) INSTALLED_APPS Ayarı
# ------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # Genelde projede kalır (statik dosyalar için)

    'rest_framework',
    'articles',  # Kendi uygulamanız
    'corsheaders',
]

# ------------------------------------------------------------------
# 2) MIDDLEWARE Ayarı
# ------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'backend_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend_project.wsgi.application'

# ------------------------------------------------------------------
# 3) Veritabanı Ayarları
# ------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'belgeanon',  # Mevcut veritabanı adı
        'USER': 'root',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Eğer auth uygulamasını kaldırıyorsanız, şifre validasyonunu da kapatmanız gerekebilir
AUTH_PASSWORD_VALIDATORS = [
    # Boş bırakabilir veya tamamen silebilirsiniz
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
FERNET_KEY = b'2qmmrfDoM1cgPC3NXXaG5d9GqHlrNSrEu5r-026GE2c='
