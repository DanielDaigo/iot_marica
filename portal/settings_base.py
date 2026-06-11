import os
from pathlib import Path
import environ
from django.urls import reverse_lazy
# Constrói os caminhos base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializa o leitor de variáveis de ambiente
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Segurança e Host (Lidos do .env)
SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DJANGO_DEBUG', False)
ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS').split(',') if env('DJANGO_ALLOWED_HOSTS') else []
CSRF_TRUSTED_ORIGINS = ['https://iotmarica.duckdns.org']

# Definição dos Módulos (Apps)
INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Nossos módulos
    'portal.apps.core',
    'portal.apps.devices',
    'portal.apps.dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Gerenciador de arquivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'portal.wsgi.application'

# Banco de Dados (Lido da DATABASE_URL no .env)
DATABASES = {
    'default': env.db('DATABASE_URL')
}

# Validação de Senhas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos Estáticos (CSS, JavaScript, Imagens)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Grafana base URL (opcional, configurável por ambiente)
GRAFANA_BASE_URL = env('GRAFANA_BASE_URL', default='')

# --- Configurações do InfluxDB ---
INFLUXDB_HOST = env("INFLUXDB_HOST", default="127.0.0.1")
INFLUXDB_PORT = env.int("INFLUXDB_PORT", default=8086)
INFLUXDB_DATABASE = env("INFLUXDB_DATABASE", default="iot_data")
INFLUXDB_USER = env("INFLUXDB_USER", default="")
INFLUXDB_PASSWORD = env("INFLUXDB_PASSWORD", default="")

def environment_callback(request):
    """Badge de ambiente exibido no topo do painel."""
    import os
    if env.bool('DJANGO_DEBUG', False):
        return ["Desenvolvimento", "info"]
    return ["Produção", "danger"]

# Configuração do Tema Unfold (Admin)
UNFOLD = {
    "SITE_TITLE": "Telemetria de Sensores",
    "SITE_HEADER": "Telemetria Admin",
    "ENVIRONMENT": "portal.settings_base.environment_callback",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Gestão de Dispositivos",
                "separator": True,
                "items": [
                    {
                        "title": "Sensores",
                        "icon": "sensors",
                        "link": reverse_lazy("admin:devices_sensor_changelist"),
                    },
                    {
                        "title": "Tipos de Sensor",
                        "icon": "category",
                        "link": reverse_lazy("admin:devices_sensortype_changelist"),
                    },
                ],
            },
            {
                "title": "Segurança & Acessos",
                "separator": True,
                "items": [
                    {
                        "title": "Auditoria de Chaves",
                        "icon": "key",
                        "link": reverse_lazy("admin:devices_sensorapikeyaudit_changelist"),
                    },
                    {
                        "title": "Usuários",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                ],
            },
        ],
    },
    "USER_MENU": [
        {
            "icon": "query_stats",  # Ícone do Material Symbols
            "title": "Acessar Dashboard",
            "link": reverse_lazy("dashboard:index"),
        },
    ],
}