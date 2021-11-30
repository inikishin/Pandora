# docker run -d -p 5672:5672 rabbitmq
# docker run -d -p 6379:6379 redis
# celery -A tasks worker --loglevel=INFO

from celery import Celery
from api import moex
from preprocessing.loadfile import load_csv_file, get_list_of_files
from preprocessing.preprocessing import preprocessing_daily
from preprocessing.dailyAnalysis import createdailyanalysis
from preprocessing import dailyanalysisprediction
from preprocessing import prediction

pandora = Celery('backend/tasks', backend='redis://localhost', broker='amqp://localhost')


def inspector():
    __inspector = pandora.control.inspect()
    return {'current_task': __inspector.active(), 'queue_tasks': __inspector.reserved()}


@pandora.task
def load_quotes_from_moex_api(ticker):
    if ticker['market'] == 'moex':
        moex.load(ticker=ticker['code'], load_difference=True, interval='24')


@pandora.task
def load_quotes_from_csv_files(folder):
    for file in get_list_of_files(folder):
        load_csv_file(file)


@pandora.task
def preprocessing(ticker):
    preprocessing_daily(market=ticker['market'], ticker=ticker['code'])


@pandora.task
def daily_analysis_post(ticker, post_date):
    createdailyanalysis(market=ticker['market'], ticker=ticker['code'], on_date=post_date)


@pandora.task
def fit_prediction_model(ticker, horizon):
    prediction.fitpredictionmodel(market=ticker['market'], ticker=ticker['code'], horizon=horizon)


@pandora.task
def fit_daily_analysis_model(ticker, ticker_list, signal, shift):
    dailyanalysisprediction.fitpredictionmodel(market=ticker['market'], ticker=ticker['code'], tickers=ticker_list,
                                               signal=signal, shift=shift)


@pandora.task
def post_prediction(ticker, horizon, predict_on_date):
    prediction.postPredict(market=ticker['market'], ticker=ticker['code'], horizon=horizon,
                           predict_date=predict_on_date)
