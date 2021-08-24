from datetime import datetime
import configparser

import pandas as pd

from API import moexapi
from preprocessing import dailyAnalysis, preprocessing, dailyanalysisprediction, prediction, loadfile

# сунуть текст в DAG. Сделать два ДАГа: первый для полной загрузки (запускать руками),
# второй для инкрементальной, для ежедневного запуска по расписанию.
# Вторым шагом в ДАГе сделать предобработку этих данных в другую таблицу, чтобы сократить время анализа.

config = configparser.ConfigParser()
config.read('settings.ini')

ticker_list = pd.read_csv(config['PANDORA']['DataPath'] + 'ticker_list.csv')

# data analysis
is_load = False
is_preprocessing = True
is_createdaily = False
# Creating daily analysises
dates = ['2021-02-08', '2021-02-09']

# machine learning
fit_da_models = False
fit_prediction_models = False

post_predict_daily = False
post_predict_weekly = False
predict_on_date = '2021-02-09'

# Loading data from MOEX and folders
if is_load:
    for t in ticker_list[ticker_list.market=='moex'].ticker:
        moexapi.load(ticker=t, load_difference=True, interval='24')
    loadfile.load_files()
    print('All data loaded!')

# Preprocessing loaded data
if is_preprocessing:
    for t in ticker_list.to_numpy():
        preprocessing.preprocessing_daily(t[0], t[1])
        print(t[1] + ' ready')
    print('Preprocessing done!')

if is_createdaily:
    for t in ticker_list.to_numpy():
        for d in dates:
            r = dailyAnalysis.createdailyanalysis(t[0], t[1], datetime.strptime(d, '%Y-%m-%d'))
            print(r)

    print('**************************************************************************')
    print('Create daily analysis done!')


# machine learning
if fit_da_models:
    for t in ticker_list.to_numpy():
        dailyanalysisprediction.fitpredictionmodel(t[0], t[1], ticker_list, 'sig_elder', 5)
        dailyanalysisprediction.fitpredictionmodel(t[0], t[1], ticker_list, 'sig_channel', 5)
        dailyanalysisprediction.fitpredictionmodel(t[0], t[1], ticker_list, 'sig_DivBar', 5)
        dailyanalysisprediction.fitpredictionmodel(t[0], t[1], ticker_list, 'sig_NR4ID', 5)
        dailyanalysisprediction.fitpredictionmodel(t[0], t[1], ticker_list, 'sig_breakVolatility', 5)

if fit_prediction_models:
    for t in ticker_list.to_numpy():
        horizon = ['1w', '2w', '1m', '3m', '6m', '1y']
        for h in horizon:
            prediction.fitpredictionmodel(t[0], t[1], h)

if post_predict_daily:
    for t in ticker_list.to_numpy():
        horizon = ['1w', '2w']
        for h in horizon:
            prediction.postPredict(t[0], t[1], h, predict_on_date)

if post_predict_weekly:
    for t in ticker_list.to_numpy():
        horizon = ['1m', '3m', '6m', '1y']
        for h in horizon:
            prediction.postPredict(t[0], t[1], h, predict_on_date)