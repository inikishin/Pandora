# Start redis
# docker run -d -p 6379:6379 redis
# Start celery from common catalog
#  celery -A webapp.backend.tasks worker --loglevel=INFO

from celery import Celery, Task
from celery.result import AsyncResult

from API import moexapi

app = Celery('tasks', broker='redis://localhost', backend='redis://localhost')

@app.task(name='webapp.backend.tasks.processloadquotes')
def processloadquotes(ticker_list):
    for t in ticker_list:
        moexapi.load(ticker=t, load_difference=True, interval='24')
    return 'quotes loaded'

def check_status(id):
    r = app.AsyncResult(id)
    return {'is_ready': r.ready(), 'result': r.result}