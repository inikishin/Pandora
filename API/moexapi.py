# Информацию о работе API можно найти по ссылке (https://www.moex.com/a2193).
# Там же можно скачать pdf с базовым описанием работы API.
# Описание всех функций можно найти по ссылке (http://iss.moex.com/iss/reference/).

import requests
import json
import pandas as pd
import time
from datetime import datetime
import configparser

# инициируем файл настроек
config = configparser.ConfigParser()
config.read('/home/ilya/PycharmProjects/Pandora/settings.ini')

url_prefix = 'http://iss.moex.com/'
engine = 'stock'
market = 'shares'
board = 'TQBR'

def load(ticker, load_difference=False, interval='24'):
    #http://iss.moex.com/iss/history/engines/stock/markets/index/boards/SNDX/securities/MICEXINDEXCF/dates.xml
    response = requests.get(url_prefix +
                            '/iss/history/engines/'+ engine +
                            '/markets/' + market +
                            '/boards/' + board +
                            '/securities/' + ticker +
                            '/dates.json')
    from_date = json.loads(response.text)['dates']['data'][0][0]
    till_date = json.loads(response.text)['dates']['data'][0][1]
    print('from {0} to {1} history available for {2}'.format(from_date, till_date, ticker))

    if load_difference:
        try:
            df = pd.read_csv(config['PANDORA']['DataPath'] + ticker + '_data.csv')
            df['date_time'] = pd.to_datetime(df.date_time)
            from_date = df['date_time'].max().strftime('%Y-%m-%d')
        except:
            print('Error')

    #/iss/engines/[engine]/markets/[market]/securities/[security]/candles
    history_data = pd.DataFrame()
    s = 0
    data = ['0']
    print('Load of {0} starts from {1}'.format(ticker, datetime.now()))
    while len(data) > 0:
        params = {'from': from_date,
                 'till': till_date,
                 'interval': interval,
                 'start': str(s)}
        response = requests.get(url_prefix +
                                '/iss/history/engines/'+ engine +
                                '/markets/' + market +
                                '/boards/' + board +
                                '/securities/' + ticker +
                                '/candles.json', params)
        data=json.loads(response.text)['history']['data']
        if len(data) > 0:
            history_data = history_data.append(pd.DataFrame(data=data))
        s = s + 100
        time.sleep(2)

    print('Load of {0} ends at {1}. Loaded: {2}'.format(ticker, datetime.now(), len(history_data)))
    data_cols = json.loads(response.text)['history']['columns']
    history_data.columns = data_cols
    history_data.drop(labels=['SHORTNAME', 'SECID', 'BOARDID', 'NUMTRADES', 'VALUE', 'LEGALCLOSEPRICE', 'WAPRICE',
                              'MARKETPRICE2', 'MARKETPRICE3', 'ADMITTEDQUOTE', 'MP2VALTRD', 'MARKETPRICE3TRADESVALUE',
                              'ADMITTEDVALUE', 'WAVAL'],
                      axis=1,
                      inplace=True)
    history_data['TRADEDATE'] = pd.to_datetime(history_data.TRADEDATE)
    history_data.columns = ['date_time', 'open', 'low', 'high', 'close', 'vol' ]

    if load_difference:
        history_data = pd.concat([df, history_data])
        history_data.drop_duplicates(subset=['date_time'], inplace=True, keep='last')

    history_data.dropna(inplace=True)
    history_data.to_csv(config['PANDORA']['DataPath'] + ticker + '_data.csv', index=False)
    return 'success'


