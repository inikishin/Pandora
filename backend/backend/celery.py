import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend', broker='redis://localhost')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# bash: celery -A backend worker -l INFO

def inspector():
    __inspector = app.control.inspect()
    return {'current_task': __inspector.active(), 'queue_tasks': __inspector.reserved()}


def check_status():
    print(app.control.ping())
    ping_result = app.control.ping()
    msg = 'Celery status: '
    if ping_result == []:
        msg += 'DOWN'
    else:
        msg += 'ok'
    return msg




