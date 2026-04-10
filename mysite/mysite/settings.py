from pathlib import Path
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}



BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-fjm7vbd1j4&x6%8x1(!m1a=#pnag^z+(f!w&@arfi=2g8$ebu7'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']


# ---------------------------------------------------------
# APPs
# ---------------------------------------------------------
INSTALLED_APPS = [
    # Mūsų app’ai
    'main.apps.MainConfig',
    'services',
    'orders',
    'reviews',
    'gallery',


    # Trečiųjų šalių app’ai
    'crispy_forms',
    'crispy_bootstrap5',
    'tinymce',

    # Django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]


# ---------------------------------------------------------
# Crispy Forms
# ---------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'mysite.urls'


# ---------------------------------------------------------
# Templates
# ---------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'main' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.company_info',
            ],
        },
    },
]


WSGI_APPLICATION = 'mysite.wsgi.application'


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ---------------------------------------------------------
# Password validation
# ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------
# Internationalization
# ---------------------------------------------------------
LANGUAGE_CODE = 'lt'
LANGUAGES = [
    ('lt', 'Lietuvių'),
    ('en', 'English'),
    ('ru', 'Русский'),
]
TIME_ZONE = 'Europe/Vilnius'
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'main' / 'locale',
]

LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 31536000
LANGUAGE_COOKIE_PATH = '/'


# ---------------------------------------------------------
# Static & Media
# ---------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

ADMIN_CSS = "admin/css/premium_admin.css"


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------
# Login / Logout
# ---------------------------------------------------------
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'


# ---------------------------------------------------------
# PDF generavimas (WeasyPrint)
# ---------------------------------------------------------
WEASYPRINT_BASEURL = BASE_DIR


# ---------------------------------------------------------
# Įmonės rekvizitai (naudojami PDF ir Kontaktai puslapyje)
# ---------------------------------------------------------
COMPANY_INFO = {
    "name": 'H-Pro',
    "full_name": 'UAB "HARLEMO PROJEKTAI"',
    "address": 'Kolektyvo g. 158-1, LT-08350 Vilnius',
    "seller_code": '306148489',
    "vat_code": 'LT100016122613',
    "account_number": 'LT337300010184042606',
    "bank_name": 'SWEDBANK AB',
    "phone": '068965681',
    "email": 'harlemoprojektai@gmail.com',
    "manager": 'Adrianas Panovas',
}

# ---------------------------------------------------------
# TinyMCE
# ---------------------------------------------------------
TINYMCE_DEFAULT_CONFIG = {
    'height': 400,
    'width': '100%',
    'cleanup_on_startup': True,
    'selector': 'textarea',
    'theme': 'silver',
    'plugins': (
        'textcolor link image media table code lists fullscreen '
        'insertdatetime wordcount visualblocks charmap anchor advlist '
        'searchreplace'
    ),
    'toolbar': (
        'undo redo | bold italic underline | fontselect fontsizeselect | '
        'forecolor backcolor | alignleft aligncenter alignright alignjustify | '
        'bullist numlist | link image media | table | code | fullscreen'
    ),
    'menubar': True,
    'statusbar': True,
    'relative_urls': False,
    'remove_script_host': False,
    'convert_urls': True,
}
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = False
