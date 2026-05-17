from pathlib import Path
import os  
import dj_database_url
import environ




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env") 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = env("DEBUG")

#ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"])
ALLOWED_HOSTS = ['*']




DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração do banco de dados
# No Heroku, DATABASE_URL é definida automaticamente pelo add-on Postgres.
# Localmente, usa SQLite como fallback.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=False,
    )
}



STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
AWS_ACCESS_KEY_ID       = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY   = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION_NAME      = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
AWS_DEFAULT_ACL         = None
AWS_S3_FILE_OVERWRITE   = False
AWS_QUERYSTRING_AUTH    = False  # URLs diretas sem assinatura (bucket público)
AWS_S3_CUSTOM_DOMAIN    = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'

if AWS_ACCESS_KEY_ID and AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
         'rest_framework_simplejwt.authentication.JWTAuthentication',
         ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',

    ## Rate limiting para usuários anônimos     
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Máximo 100 requisições por hora para usuários anônimos
        'user': '1000/hour'  # Mais permissivo para usuários autenticados
    }

     }

SPECTACULAR_SETTINGS = {
    'TITLE': 'Notifygen API',
    'DESCRIPTION': 'Documentação OpenAPI das APIs web e mobile do sistema.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api/v1',
    'COMPONENT_SPLIT_REQUEST': True,
}

# Permissão para POST, PUT, DELETE
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000','https://divprom.herokuapp.com']  # ajuste se necessário
CSRF_COOKIE_HTTPONLY = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'divprom.urls'


INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crr',
    'notificacao',
    'import_export',
    'rest_framework',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'authentication',
    "bootstrap5",
    'storages',

]

# Configuração do Jazzmin
JAZZMIN_SETTINGS = {
    "site_title": "Notifygen",
    "site_header": "Notifygen",
    "site_brand": "Notifygen",
    "welcome_sign": "Bem-vindo ao Sistema Notifygen",
    "copyright": "Prefeitura Municipal de São Sebastião",
    "search_model": ["crr.Crr"],
    "topmenu_links": [
        {"name": "Admin", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "CRR", "url": "crr:crr_list", "permissions": ["auth.view_user"]},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "crr.Crr": "fas fa-file-alt",
        "crr.TabelaEnquadramento": "fas fa-table",
        "crr.TabelaArrendatario": "fas fa-building",
        "notificacao.Notificacao": "fas fa-envelope",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "use_google_fonts_cdn": True,
    "changeform_format": "vertical_tabs",
    "changeform_format_overrides": {
        "crr.crr": "vertical_tabs",
    },
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'crr' / 'templates'],
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

WSGI_APPLICATION = 'divprom.wsgi.application'



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Formatação de datas
DATE_INPUT_FORMATS = ['%d/%m/%Y']
TIME_INPUT_FORMATS = ['%H:%M']
SHORT_DATE_FORMAT = 'd/m/Y'
TIME_FORMAT = 'H:i'

# Autenticação: usar login do Django Admin
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/crr/'

# Sessão: expira após 30 minutos de inatividade
SESSION_COOKIE_AGE = 1800          # 30 minutos em segundos
SESSION_SAVE_EVERY_REQUEST = True  # Renova o timer a cada requisição
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# Email (configurar via variáveis de ambiente no Heroku)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS       = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL       = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('EMAIL_FROM', os.environ.get('EMAIL_HOST_USER', ''))
EMAIL_PATIO_DESTINO = os.environ.get('EMAIL_PATIO_DESTINO', '')
EMAIL_TIMEOUT       = 15










