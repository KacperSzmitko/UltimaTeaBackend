from celery.utils.log import get_task_logger
from celery import shared_task
logger = get_task_logger(__name__)

@shared_task(name="send_recipe")
def send_recipe(data):
    return 0