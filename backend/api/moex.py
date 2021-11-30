# Информацию о работе api можно найти по ссылке (https://www.moex.com/a2193).
# Там же можно скачать pdf с базовым описанием работы api.
# Описание всех функций можно найти по ссылке (http://iss.moex.com/iss/reference/).

import requests
import json
import pandas as pd
import time
from datetime import datetime

url_prefix = 'http://iss.moex.com/'
engine = 'stock'
#market = 'shares'
#board = 'TQBR'
board = 'TQCB'


def load_quotes(ticker: str, market: str, from_date: str = '', interval: str = '24') -> pd.DataFrame:
    """
    Loading quotes from MOEX

    :param from_date: start date for load quotes
    :param ticker: ticker short name in string
    :param interval: 24 - daily
    :return: pandas DataFrame with quotes
    """
    # http://iss.moex.com/iss/history/engines/stock/markets/index/boards/SNDX/securities/MICEXINDEXCF/dates.xml

    url_text = url_prefix + 'iss/history/engines/' + engine + '/markets/' + market + '/boards/' + board + '/securities/' + ticker + '/dates.json'
    response = requests.get(url_text)
    available_from_date = json.loads(response.text)['dates']['data'][0][0]
    available_to_date = json.loads(response.text)['dates']['data'][0][1]
    print(f'History for ticker {ticker} available from {available_from_date} to {available_to_date} ')

    # /iss/engines/[engine]/markets/[market]/securities/[security]/candles
    history_data = pd.DataFrame()
    s = 0
    data = ['0']
    print(f'Loading history for {ticker} starts at {datetime.now()}')

    while len(data) > 0:
        params = {'from': from_date if from_date != '' else available_from_date,
                  'till': available_to_date,
                  'interval': interval,
                  'start': str(s)}

        url_text = url_prefix + '/iss/history/engines/' + engine + '/markets/' + market + '/boards/' + board + '/securities/' + ticker + '/candles.json'
        print('get quotes url_text:', url_text)
        response = requests.get(url_text, params)
        data = json.loads(response.text)['history']['data']

        if len(data) > 0:
            history_data = history_data.append(pd.DataFrame(data=data))
        s = s + 100
        time.sleep(2)

    print(f'{ticker} quotes load ends at {datetime.now()}. Loaded {len(history_data)} quotes')

    data_cols = json.loads(response.text)['history']['columns']
    history_data.columns = data_cols

    export_data = pd.DataFrame()
    export_data['datetime'] = pd.to_datetime(history_data['TRADEDATE'])
    export_data['open'] = history_data['OPEN']
    export_data['high'] = history_data['HIGH']
    export_data['low'] = history_data['LOW']
    export_data['close'] = history_data['CLOSE']
    export_data['volume'] = history_data['VOLUME']
    export_data.dropna(inplace=True)

    return export_data


def get_news(max_count: int) -> list:
    start_record = 0
    news = []
    loops = int(max_count / 50)
    print(loops)
    for l in range(1, loops + 1):
        params = {'start': str(start_record)}
        response = requests.get(url_prefix + 'iss/sitenews.json', params)
        data = json.loads(response.text)
        news.append(data['sitenews']['data'])
        start_record = l * 50
        print(start_record)

    return news


# market = bonds, shares
def get_ticker_list(market: str, board: str = '') -> pd.DataFrame:
    url_text = url_prefix + f'iss/engines/stock/markets/{market}'
    if board != '':
        url_text = url_text + f'/boards/{board}'
    url_text = url_text + '/securities.json'

    response = requests.get(url_text)
    data = json.loads(response.text)

    ticker_list = pd.DataFrame(data=data['securities']['data'])
    ticker_list.columns = data['securities']['columns']

    ticker_list.drop(labels=["BOARDID", "PREVWAPRICE", "YIELDATPREVWAPRICE", "PREVPRICE", "FACEVALUE", "BOARDNAME",
                             "DECIMALS", "PREVLEGALCLOSEPRICE", "PREVADMITTEDQUOTE",
                             "PREVDATE", "REMARKS", "MARKETCODE", "INSTRID", "SECTORID", "FACEUNIT",
                             "BUYBACKPRICE", "BUYBACKDATE", "LATNAME", "ISSUESIZEPLACED",
                             "SECTYPE", "OFFERDATE", "SETTLEDATE"],
                     axis=1,
                     inplace=True)
    ticker_list.columns = ['code', 'short_name', 'coupon_value', 'next_coupon_date', 'accumulated_coupon_yield',
                           'lot_size', 'status', 'maturity_date', 'coupon_period', 'issue_size', 'fullname',
                           'min_step', 'code_isin', 'gov_reg_number', 'currency', 'list_level',
                           'coupon_percent', 'lot_value']

    return ticker_list
