from celery.utils.log import get_task_logger
from celery import shared_task
logger = get_task_logger(__name__)

@shared_task(name="send_recipe")
def send_recipe(data, machine_id):
    return 0

@shared_task(name="favourites_edit_online")
def favourites_edit_online(data, operation, machine_id):
    return 0

@shared_task(name="favourites_edit_offline")
def favourites_edit_offline(data, machine_id):
    return 0

@shared_task(name="update_single_container")
def update_single_container(data, container_number, machine_id):
    return 0

@shared_task(name="update_all_containers")
def update_all_containers(data, machine_id):
    return 0