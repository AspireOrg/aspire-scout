from scout.tasks.core import celery
from scout.models import Block


@celery.task(ignore_result=True, queue="general")
def catchup_blocks(channel, event, data):
    print('yep')
