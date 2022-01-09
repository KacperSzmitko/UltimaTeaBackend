from .celery import app as celery_app
import os

if os.environ.get("DEV", False):
    from dotenv import load_dotenv
    load_dotenv()

__all__ = ('celery_app',)
