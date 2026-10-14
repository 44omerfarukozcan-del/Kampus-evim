import os
from pathlib import Path

# BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# GÜVENLİK ANAHTARI
SECRET_KEY = 'django-insecure-kampusevim-gizli-anahtar-12345'

# 10. HAFTA CANLIYA ALMA AYARLARI (GÜVENLİK İÇİN DEBUG KAPATILDI, TÜM HOSTLARA İZİN VERİLDİ)
DEBUG = False
ALLOWED_HOSTS = ['*']

# UYGULAMALAR
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Kendi Uygulamamız
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# VERİTABANI
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 1-5. HAFTA: ÖZEL KULLANICI MODELİMİZ (.edu.tr İÇİN)
AUTH_USER_MODEL = 'core.Kullanici'

# ŞİFRE DOĞRULAYICILAR
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# DİL VE SAAT DİLİMİ (TÜRKİYE İÇİN AYARLI)
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# STATİK DOSYALAR (CSS, JavaScript, Resimler)
STATIC_URL = 'static/'
# 10. HAFTA: CANLI SUNUCUNUN (PYTHONANYWHERE) STATİK DOSYALARI BULABİLMESİ İÇİN EKLENDİ
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# MEDYA DOSYALARI (Kullanıcıların yüklediği Profil Resimleri ve Adli Sicil Belgeleri)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# VARSAYILAN KİMLİK ALANI TİPİ
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'