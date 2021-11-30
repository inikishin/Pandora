import pandas as pd
import time
from datetime import datetime
import configparser
import os

# инициируем файл настроек
config = configparser.ConfigParser()
config.read('settings.ini')

def load_files():
    for f in get_list_of_files():
        load_csv_file(f)

def get_list_of_files(folder):
    files_list = []
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith('.csv'):
                files_list.append(folder + '/' + f)

    return files_list

def load_csv_file(file_path):
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
    else:
        print(f'Ticker from file {file_name} not in ticker_list')