from flask import session

from decimal import Decimal
from celery import Celery
from datetime import datetime
from datetime import timezone
from flask import Flask
from flask import current_app
from flask_cors import CORS
from kombu.serialization import register
from werkzeug.middleware.proxy_fix import ProxyFix
from logging.handlers import TimedRotatingFileHandler
from sentry_sdk.integrations.flask import FlaskIntegration
import logging
import os
import sentry_sdk

from scout.core import aspire
from scout.core import UTC
from scout.core import db
from scout.core import redis
from scout.core import formatter
from scout.core import logger
from scout.core import long_to_decimal
from scout.helpers import import_all_models


def create_app(package_name, package_path, celery=False, template_folder='site/templates', static_folder='sites/static'):

    app = Flask(
        package_name,
        template_folder = os.path.join(os.getcwd(), 'scout', template_folder),
        static_folder = os.path.join(os.getcwd(), 'scout', static_folder)
    )

    # Load Config
    app.config.from_object('config.development')
    try:
        app.config.from_envvar('SCOUT_CONFIG')
    except RuntimeError:
        logger.error('SCOUT_CONFIG is not set. PROPER CONFIG FILE IS NOT LOADED!! RUNNING WITH DEFAULT DEVELOPMENT CONFIG.')

    # Setup Logging
    logging_level = app.config.get("LOGGING_LEVEL", logging.DEBUG)
    logging_file = app.config.get("LOGGING_FILE", "logs/%s.log" % package_name)
    handler = TimedRotatingFileHandler(logging_file, when="midnight", interval=1)
    handler.setLevel(logging_level)
    handler.setFormatter(formatter)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging_level)
    log.addHandler(handler)
    app.logger.addHandler(handler)

    CORS(app)  # TODO: remove on prod, this is for dev only

    # This lets gunicorn work
    app.wsgi_app = ProxyFix(app.wsgi_app, 2)

    # Setup kombu with our custom serializer for celery security.
    from scout.tasks.helpers import loads, dumps
    register('custom_json', dumps, loads, content_type='application/x-custom_json', content_encoding='utf-8')

    # Setup db connection before anything
    if not celery:  # Celery init's db after per task.
        db.init_app(app)

    # Setup redis
    redis.init_app(app)
    from scout.libs.RedisSessions import RedisSessionInterface
    app.session_interface = RedisSessionInterface(redis=redis.redis_cli)

    # @slanger.auth
    # def slanger_auth(channel_name, socket_id):
    #     return False

    # Import all models so that its registered for the
    # mongoengine magic. (EX, db.ReferenceField("User"),
    #       The model User must've previously been imported)
    import_all_models()

    if not celery:
        from scout.models import PersistentConfig
        PersistentConfig.setup(app)

    # sentry_sdk.init(
    #     **app.config['SENTRY_CONFIG'],
    #     send_default_pii=True,
    #     integrations=[FlaskIntegration()]
    # )

    aspire.init_app(app)

    return app


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
