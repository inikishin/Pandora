from datetime import datetime
import configparser

import pandas as pd

from API import moexapi
from preprocessing import dailyAnalysis, preprocessing, dailyanalysisprediction, prediction

# сунуть текст в DAG. Сделать два ДАГа: первый для полной загрузки (запускать руками),
# второй для инкрементальной, для ежедневного запуска по расписанию.
# Вторым шагом в ДАГе сделать предобработку этих данных в другую таблицу, чтобы сократить время анализа.
config = configparser.ConfigParser()
config.read('/home/ilya/PycharmProjects/Pandora/settings.ini')

ticker_list = pd.read_csv(config['PANDORA']['DataPath'] + 'ticker_list.csv')

# data analysis
is_load = True
is_preprocessing = True
is_createdaily = True

# machine learning
fit_da_models = False
fit_prediction_models = False

post_predict_daily = False
post_predict_weekly = False

# Loading data from MOEX
if is_load:
    for t in ticker_list.ticker:
        moexapi.load(ticker=t, load_difference=True, interval='24')
    print('All data loaded!')


# Preprocessing loaded data
if is_preprocessing:
    for t in ticker_list.ticker:
        preprocessing.preprocessing_daily(t)
        print(t + ' ready')
    print('Preprocessing done!')

# Creating daily analysises
dates = ['2020-07-28']

if is_createdaily:
    for t in ticker_list.ticker:
        for d in dates:
            r = dailyAnalysis.createdailyanalysis(t, datetime.strptime(d, '%Y-%m-%d'))
            print(r)

    print('**************************************************************************')
    print('Create daily analysis done!')


# machine learning
if fit_da_models:
    for t in ticker_list.ticker:
        dailyanalysisprediction.fitpredictionmodel(t, ticker_list.ticker, 'sig_elder', 5)
        dailyanalysisprediction.fitpredictionmodel(t, ticker_list.ticker, 'sig_channel', 5)
        dailyanalysisprediction.fitpredictionmodel(t, ticker_list.ticker, 'sig_DivBar', 5)
        dailyanalysisprediction.fitpredictionmodel(t, ticker_list.ticker, 'sig_NR4ID', 5)
        dailyanalysisprediction.fitpredictionmodel(t, ticker_list.ticker, 'sig_breakVolatility', 5)

if fit_prediction_models:
    for t in ticker_list.ticker:
        horizon = ['1w', '2w', '1m', '3m', '6m', '1y']
        for h in horizon:
            prediction.fitpredictionmodel(t, h)

if post_predict_daily:
    for t in ticker_list.ticker:
        horizon = ['1w', '2w']
        for h in horizon:
            #prediction.postPredict(t, h, datetime.now().strftime("%Y-%m-%d"))
            prediction.postPredict(t, h, '2020-07-24')

if post_predict_weekly:
    for t in ticker_list.ticker:
        horizon = ['1m', '3m', '6m', '1y']
        for h in horizon:
            #prediction.postPredict(t, h, datetime.now().strftime("%Y-%m-%d"))
            prediction.postPredict(t, h, '2020-07-24')