# Sentry configuration
import os

# Database
DATABASES = {
    'default': {
        'ENGINE': 'postgresql',
        'NAME': os.environ.get('SENTRY_DB_NAME', 'sentry'),
        'USER': os.environ.get('SENTRY_DB_USER', 'sentry'),
        'PASSWORD': os.environ.get('SENTRY_DB_PASSWORD', ''),
        'HOST': os.environ.get('SENTRY_POSTGRES_HOST', 'sentry-postgres'),
        'PORT': '5432',
    }
}

# Redis
SENTRY_CACHE = 'sentry.cache.redis.RedisCache'
SENTRY_RATE_LIMIT = 'sentry.ratelimits.redis.RedisRateLimiter'
SENTRY_QUOTAS = 'sentry.quotas.redis.RedisQuota'

SENTRY_REDIS_HOST = os.environ.get('SENTRY_REDIS_HOST', 'sentry-redis')
SENTRY_REDIS_PORT = os.environ.get('SENTRY_REDIS_PORT', '6379')

BROKER_URL = f'redis://{SENTRY_REDIS_HOST}:{SENTRY_REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{SENTRY_REDIS_HOST}:{SENTRY_REDIS_PORT}/0'

# Web Server
SENTRY_WEB_HOST = '0.0.0.0'
SENTRY_WEB_PORT = 9000
SENTRY_WEB_OPTIONS = {
    'workers': 3,
    'limit_request_line': 0,
    'secure_scheme_headers': {'X-FORWARDED-PROTO': 'https'},
}