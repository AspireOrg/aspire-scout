from celery import signals
from flask import current_app
import os

from scout.core import db
from scout.factory import make_celery, create_app

app = current_app
if not app:
    app = create_app('scout.tasks', os.path.dirname(__file__), celery=True)
celery = make_celery(app)


def reset_mongo_connection(**kwargs):
    with app.app_context():
        try:
            db.init_app(app)
        except:
            pass


signals.task_prerun.connect(reset_mongo_connection)
