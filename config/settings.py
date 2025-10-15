"""
Django settings for SabPaisa Reports API project.
"""

from pathlib import Path
from datetime import timedelta
from decouple import config, AutoConfig
import os

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Explicitly load .env file from the project root
config = AutoConfig(search_path=BASE_DIR)

# Security settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',

    # Local apps
    'apps.authentication',
    'apps.transactions',
    'apps.settlements',
    'apps.analytics',
    'apps.reports',
    'apps.notifications',
    'apps.qwikforms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',  # Commented out - not needed for development
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # PERFORMANCE: Disabled heavy logging middleware (adds 50-200ms per request)
    # Enable only when debugging specific issues
    # 'apps.core.middleware.RequestLoggingMiddleware',
    # 'apps.core.middleware.PerformanceMonitoringMiddleware',

    # NEW FEATURE ENHANCEMENTS: Response Headers (adds headers only, body unchanged)
    'apps.core.middleware.RequestCorrelationMiddleware',  # Adds X-Request-ID, X-Response-Time
    'apps.core.middleware.PerformanceHeaderMiddleware',   # Adds X-Performance
    'apps.core.middleware.RateLimitHeaderMiddleware',     # Adds X-RateLimit-* headers
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Database Configuration - Multi-database setup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_PRIMARY_NAME', default='sabpaisa2_stage_sabpaisa'),
        'USER': config('DB_PRIMARY_USER', default='root'),
        'PASSWORD': config('DB_PRIMARY_PASSWORD', default=None) or '',
        'HOST': config('DB_PRIMARY_HOST', default='localhost'),
        'PORT': config('DB_PRIMARY_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'; SET SESSION wait_timeout=300; SET SESSION interactive_timeout=300;",
            'connect_timeout': 10,
            'read_timeout': 120,  # Increased to 120s for large aggregations
            'write_timeout': 120,
            'autocommit': True,
        },
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'ATOMIC_REQUESTS': False,  # Disabled - causes issues with read-only queries
    },
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_LEGACY_NAME', default='sabpaisa2_stage_legacy'),
        'USER': config('DB_LEGACY_USER', default='root'),
        'PASSWORD': config('DB_LEGACY_PASSWORD', default=None) or '',
        'HOST': config('DB_LEGACY_HOST', default='localhost'),
        'PORT': config('DB_LEGACY_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'; SET SESSION wait_timeout=300; SET SESSION interactive_timeout=300;",
            'connect_timeout': 10,
            'read_timeout': 120,  # Increased to 120s for large aggregations
            'write_timeout': 120,
            'autocommit': True,
        },
        'CONN_MAX_AGE': 600,
        'ATOMIC_REQUESTS': False,
    },
    'user_management': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_USER_NAME', default='spclientonboard'),
        'USER': config('DB_USER_USER', default='root'),
        'PASSWORD': config('DB_USER_PASSWORD', default=None) or '',
        'HOST': config('DB_USER_HOST', default='localhost'),
        'PORT': config('DB_USER_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'; SET SESSION wait_timeout=300; SET SESSION interactive_timeout=300;",
            'connect_timeout': 10,
            'read_timeout': 120,  # Increased to 120s for large aggregations
            'write_timeout': 120,
            'autocommit': True,
        },
        'CONN_MAX_AGE': 600,
        'ATOMIC_REQUESTS': False,
    },
    'qwikforms_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('QWIKFORMS_DB_NAME', default='spQwikForm'),
        'USER': config('QWIKFORMS_DB_USER', default='root'),
        'PASSWORD': config('QWIKFORMS_DB_PASSWORD', default=None) or '',
        'HOST': config('QWIKFORMS_DB_HOST', default='localhost'),
        'PORT': config('QWIKFORMS_DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'; SET SESSION wait_timeout=300; SET SESSION interactive_timeout=300;",
            'connect_timeout': 10,
            'read_timeout': 120,  # Increased to 120s for large aggregations
            'write_timeout': 120,
            'autocommit': True,
        },
        'CONN_MAX_AGE': 600,
        'ATOMIC_REQUESTS': False,
    }
}

# Database routing
DATABASE_ROUTERS = [
    'config.db_router.QwikFormsRouter',
    'apps.core.routers.MultiDatabaseRouter'
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'authentication.LoginMaster'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.authentication.backends.CustomJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.CustomPostPagination',
    'PAGE_SIZE': config('PAGINATION_PAGE_SIZE', default=50, cast=int),  # Reduced for better performance
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'apps.core.throttling.CustomAnonThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'anon_custom': '100/hour',
        'user': '1000/hour',
        'merchant': '5000/hour',
        'report_generation': '10/hour',
    },
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # Required for drf-spectacular
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=1440, cast=int)),  # 24 hours
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=config('JWT_REFRESH_TOKEN_LIFETIME', default=10080, cast=int)),  # 7 days
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'SabPaisa',

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'username',  # Changed to username since we don't have integer IDs
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
}

# Cache Configuration - Using in-memory cache (NO database changes required)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # Don't break if Redis is down
        },
        'KEY_PREFIX': 'sabpaisa',
        'TIMEOUT': config('CACHE_TTL', default=300, cast=int),  # 5 minutes default
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True

# Celery Configuration (Optional - comment out if not using Celery)
# CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
# CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
# For development without Celery, tasks will run synchronously
CELERY_TASK_ALWAYS_EAGER = True  # Execute tasks synchronously in development
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_BEAT_SCHEDULE = {
    'cleanup-old-reports': {
        'task': 'apps.reports.tasks.cleanup_old_reports',
        'schedule': timedelta(days=1),
    },
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'detailed': {
            'format': '[{levelname}] {asctime} | {name} | {funcName}() | Line: {lineno} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'sabpaisa_api.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'detailed',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'detailed',
        },
        'transaction_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'transactions.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            'backupCount': 20,
            'formatter': 'detailed',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'detailed',
        },
        'performance_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'performance.log'),
            'maxBytes': 1024 * 1024 * 20,  # 20MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'] if DEBUG else ['file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.authentication': {
            'handlers': ['console', 'file', 'security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.transactions': {
            'handlers': ['console', 'transaction_file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.settlements': {
            'handlers': ['console', 'transaction_file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.analytics': {
            'handlers': ['console', 'file', 'performance_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.reports': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.core.middleware': {
            'handlers': ['console', 'performance_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'performance': {
            'handlers': ['performance_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# CORS Configuration
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# API Documentation (DRF Spectacular)
SPECTACULAR_SETTINGS = {
    'TITLE': 'SabPaisa Reports API',
    'DESCRIPTION': 'Comprehensive transaction reporting and analytics API for SabPaisa payment gateway',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
}

# Application-specific settings
MAX_UPLOAD_SIZE = config('MAX_UPLOAD_SIZE', default=52428800, cast=int)  # 50MB
REPORT_GENERATION_TIMEOUT = config('REPORT_GENERATION_TIMEOUT', default=300, cast=int)  # 5 minutes

# AWS Configuration (for production)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_S3_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_REGION', default='ap-south-1')

# SMS Configuration (Gupshup)
GUPSHUP_API_KEY = config('GUPSHUP_API_KEY', default='')
GUPSHUP_SENDER_ID = config('GUPSHUP_SENDER_ID', default='SABPSA')