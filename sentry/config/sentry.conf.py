import os

DATABASES = {
    'default': {
        'ENGINE': 'postgresql',
        'NAME': 'sentry',
        'USER': 'sentry',
        'PASSWORD': 'sentry',
        'HOST': 'sentry-postgres',
        'PORT': '5432',
    }
}

SENTRY_CACHE = 'sentry.cache.redis.RedisCache'
SENTRY_RATE_LIMIT = 'sentry.ratelimits.redis.RedisRateLimiter'
SENTRY_QUOTAS = 'sentry.quotas.redis.RedisQuota'

BROKER_URL = 'redis://sentry-redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://sentry-redis:6379/0'


SENTRY_WEB_HOST = '0.0.0.0'
SENTRY_WEB_PORT = 9000
SENTRY_WEB_OPTIONS = {
    'workers': 3,
    'limit_request_line': 0,
    'secure_scheme_headers': {'X-FORWARDED-PROTO': 'https'},
}