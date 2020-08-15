from celery.schedules import crontab
from datetime import timedelta
from decimal import Decimal
import logging

DEBUG = True
TESTING = False
ASSETS_DEBUG = True
CSRF_SESSION_KEY = "blahblahblah"
SECRET_KEY = "blahblahblah"
GEOCITY_DAT_LOCATION = "./scout/libs/GeoLiteCity.dat"
LOGGING_LEVEL = logging.DEBUG
LOGGING_FILE = "./logs/app.log"
PORT = 8182

SENTRY_CONFIG = {
    'dsn': '',
    'environment': 'matts dev'
}

MONGODB_SETTINGS = {
    'DB': 'scout',
    'HOST': '192.168.1.224',
    'PORT': 27017,
    'USERNAME': '',
    'PASSWORD': ''
}

CELERYBEAT_SCHEDULE = {
}

MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 5MB

# MAILGUN
MAILGUN_DOMAIN = '.mailgun.org'
MAILGUN_API_KEY = 'key-'
MAILGUN_DEFAULT_FROM = 'Mailgun Sandbox <postmaster@.mailgun.org>'

# REDIS
REDIS_HOST = '192.168.1.140'
REDIS_PORT = 6379
REDIS_DB = 0

# CELERY
CELERY_TASK_SERIALIZER = 'custom_json'
CELERY_ACCEPT_CONTENT = ['custom_json']
CELERY_RESULT_BACKEND = "redis://192.168.1.140:6379/2"
CELERY_BROKER_URL = "redis://192.168.1.140:6379/2"

ASPIRE_BLOCK_URL = 'http://aspireblock-testnet:14100/api/'
ASPIRE_BLOCK_USER = 'rpc'
ASPIRE_BLOCK_PASS = 'rpc'

ASPIRE_GAS_HOST = 'gasp-testnet'
ASPIRE_GAS_PORT = 18332
ASPIRE_GAS_USER = 'rpc'
ASPIRE_GAS_PASS = 'rpc'
