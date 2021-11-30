# uvicorn backend_api:pandora --reload
import typing

from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict
import configparser
import pandas as pd
from tasks import inspector, load_quotes_from_moex_api, load_quotes_from_csv_files, preprocessing, daily_analysis_post, \
    fit_daily_analysis_model, fit_prediction_model, post_prediction
from celery.result import AsyncResult

from orm.sessions import timeframe_create
from orm.models import update_metadata

config = configparser.ConfigParser()
config.read('settings.ini')


pandora = FastAPI()


@pandora.get('/')
async def root():
    return 'Pandora server is running...'


@pandora.get('/tasks')
async def get_task_state():
    return inspector()


@pandora.get('/tasks/{task_id}')
async def get_task_state(task_id: str):
    task = AsyncResult(task_id)
    return {'task_state': task.state}

# /tasks/create/{action}
class ActionTypes(str, Enum):
    load_quotes_moex = 'load-quotes-moex'
    load_quotes_from_csv_files = 'load-quotes-from-csv-files'
    preprocessing = 'preprocessing'
    daily_analysis = 'daily-analysis'
    fit_prediction_model = 'fit-prediction-model'
    fit_daily_analysis_model = 'fit-daily-analysis-model'
    post_prediction = 'post-prediction'


class Params(BaseModel):  # TODO describe types
    # tickers_list: Optional[Dict[str, str]] = None
    tickers_list: typing.Any
    folders_list: typing.Any
    da_posts_dates: typing.Any
    horizons: typing.Any
    predict_on_date: typing.Any

@pandora.post('/tasks/create/{action}')
async def create_action(action: ActionTypes, params: Params):
    tasks = []
    if action == ActionTypes.load_quotes_moex:
        for ticker in params.tickers_list:
            tasks.append(load_quotes_from_moex_api.delay(ticker).id)
    elif action == ActionTypes.load_quotes_from_csv_files:
        for folder in params.folders_list:
            tasks.append(load_quotes_from_csv_files.delay(folder).id)
    elif action == ActionTypes.preprocessing:
        for ticker in params.tickers_list:
            tasks.append(preprocessing.delay(ticker).id)
    elif action == ActionTypes.daily_analysis:
        for ticker in params.tickers_list:
            for post_date in params.da_posts_dates:
                tasks.append(daily_analysis_post.delay(ticker=ticker, post_date=post_date).id)
    elif action == ActionTypes.fit_daily_analysis_model:
        signals = ['sig_elder', 'sig_channel', 'sig_DivBar', 'sig_NR4ID',
                   'sig_breakVolatility']  # TODO remove list from here to database
        for ticker in params.tickers_list:
            for signal in signals:
                # TODO Fix bugs in fit method
                tasks.append(fit_daily_analysis_model.delay(ticker, params.tickers_list, signal, 5).id)
    elif action == ActionTypes.fit_prediction_model:
        for ticker in params.tickers_list:
            for horizon in params.horizons:
                tasks.append(fit_prediction_model.delay(ticker, horizon).id)
    elif action == ActionTypes.post_prediction:
        for ticker in params.tickers_list:
            for horizon in params.horizons:
                tasks.append(post_prediction.delay(ticker, horizon, params.predict_on_date).id)
    else:
        raise ValueError('Unknown action type:', action)

    return {'tasks': tasks}


@pandora.get('/data/markets')
async def get_markets():
    df = pd.read_csv(config['PANDORA']['DataPath'] + 'ticker_list.csv')
    market_list = set(df['market'].tolist())
    return_data = []
    for market in market_list:
        return_data.append({'code': market})

    return {'markets': return_data}


@pandora.get('/data/tickers')
async def get_tickers(market: str = None):
    tickers = pd.read_csv(config['PANDORA']['DataPath'] + 'ticker_list.csv')

    if market is not None:
        tickers = tickers[tickers['market'] == market]

    return_data = []
    for index, ticker_row in tickers.iterrows():
        return_data.append({'market': ticker_row['market'], 'code': ticker_row['ticker']})

    return {'tickers': return_data}

@pandora.post('/data/timeframes')
async def post_timeframe(code: str):
    update_metadata()
    timeframe_create(code)
