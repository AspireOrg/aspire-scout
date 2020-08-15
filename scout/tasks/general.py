# from scout.core import slanger
from scout.tasks.core import celery


@celery.task(ignore_result=True, queue="general")
def socket_message(channel, event, data):
#    slanger.send(channel, event, data)
    pass
