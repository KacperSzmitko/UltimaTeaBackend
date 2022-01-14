from .celery import app as celery_app
import os


if os.environ.get("DEV", True) is True:
    from dotenv import load_dotenv
    load_dotenv()

__all__ = ('celery_app',)
