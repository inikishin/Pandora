import pandas as pd
import configparser
from datetime import datetime
from API import moexapi
from preprocessing import dailyAnalysis, preprocessing

# сунуть текст в DAG. Сделать два ДАГа: первый для полной загрузки (запускать руками),
# второй для инкрементальной, для ежедневного запуска по расписанию.
# Вторым шагом в ДАГе сделать предобработку этих данных в другую таблицу, чтобы сократить время анализа.
config = configparser.ConfigParser()
config.read('/home/ilya/PycharmProjects/Pandora/settings.ini')

ticker_list = pd.read_csv(config['PANDORA']['DataPath'] + 'ticker_list.csv')

is_load = False
is_preprocessing = False
is_createdaily = True

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
dates = ['2020-06-15', '2020-06-16', '2020-06-17', '2020-06-18']
if is_createdaily:
    for t in ticker_list.ticker:
        for d in dates:
            r = dailyAnalysis.createdailyanalysis(t, datetime.strptime(d, '%Y-%m-%d'))
            print(r)
    print('Create daily analysis done!')