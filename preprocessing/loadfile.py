import pandas as pd
import time
from datetime import datetime
import configparser
import os

# инициируем файл настроек
config = configparser.ConfigParser()
config.read('settings.ini')

def load_files():
    for f in __get_list_of_files():
        __load_csv_file(f)

def __get_list_of_files():
    file_list = []
    paths = config['PANDORA']['csvfilepath'].split(';')
    for p in paths:
        if os.path.exists(p):
            for f in os.listdir(p):
                if f.endswith('.csv'):
                    file_list.append(p + '\\' + f)

    return file_list

def __load_csv_file(file_path):
    print('Start loading file {0}'.format(file_path))
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    ticker, interval = file_name.split('_')

    if interval != 'D1':
        raise ValueError('Некорректный интервал "{0}"'.format(interval))

    ticker_list = pd.read_csv(config['PANDORA']['DataPath'] + 'ticker_list.csv')

    t_line = ticker_list[ticker_list.ticker==ticker]
    if len(t_line) == 1:
        folder_name = str(list(t_line.market)[0]) + '/'
        quotes = pd.read_csv(file_path)
        quotes.date_time = pd.to_datetime(quotes.date_time)
        quotes = quotes.set_index('date_time')
        quotes.to_csv(config['PANDORA']['DataPath'] + folder_name + ticker + '_data.csv')
        return 'File {0} successfully loaded'.format(file_path)