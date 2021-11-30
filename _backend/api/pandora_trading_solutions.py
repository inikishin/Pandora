import requests
import json
import configparser

# New api
api_url = 'http://127.0.0.1:8000/data/'


def __create_query_string(filters):
    query = ''

    for key, value in filters.items():
        query = query + f'{key}={value}&'

    return query[:-1]


def __get_url(entity):
    if entity == 'markets':
        return 'tickers/markets/'
    elif entity == 'tickers':
        return 'tickers/tickers/'
    elif entity == 'quotes':
        return 'quotes/quotes/'
    elif entity == 'indicators':
        return 'quotes/indicators/'
    elif entity == 'signals':
        return 'quotes/signals/'
    else:
        raise ValueError(f'Unknown entity {entity}')


def get_data(entity, filters=None):
    request_url = api_url + __get_url(entity) + '?format=json'
    if filters is not None:
        request_url = request_url + '&' + __create_query_string(filters)

    print(request_url)
    response = requests.get(request_url)
    return json.loads(response.text)['results']


def post_data(entity, data):
    request_url = api_url + __get_url(entity)
    response = requests.post(request_url, data=data)
    return response


def load_tickers(tickers):
    '''
    This function loads DataFrame of tickers to webapp

    :param tickers: (DateFrame) - with columns 'market' and 'ticker'
    :return: None
    '''

    for index, row in tickers.iterrows():
        print(row['market'], row['ticker'])
        markets = get_data('markets', filters={'code': row['market']})
        if len(markets) == 1:
            post_data('tickers', {
                'code': row['ticker'].lower(),
                'fullname': row['ticker'].lower(),
                'market': markets[0]['id']
            })
        else:
            raise ValueError(f"Incorrect value for market - {row['market']}")


def load_quotes(ticker_code, data, timeframe='D1', from_date='', to_date=''):
    ticker = get_data('tickers', filters={'code': ticker_code.lower()})
    if len(ticker) == 1:
        data_to_load = data
        if from_date != '':
            data_to_load = data_to_load[data_to_load.date_time >= from_date]
        if to_date != '':
            data_to_load = data_to_load[data_to_load.date_time <= to_date]

        for index, row in data_to_load.iterrows():
            response = post_data('quotes', {'ticker': ticker[0]['id'],
                                            'timeframe': timeframe,
                                            'datetime': str(row['date_time']),
                                            'open': float(row['open']),
                                            'high': float(row['high']),
                                            'low': float(row['low']),
                                            'close': float(row['close']),
                                            'volume': float(row['vol'])})
            print(response)
            response = post_data('indicators', {'ticker': ticker[0]['id'],
                                                'timeframe': timeframe,
                                                'datetime': str(row['date_time']),
                                                'ma_fast': float(row['MA_fast']),
                                                'ma_slow': float(row['MA_slow']),
                                                'macd': float(row['MACD']),
                                                'willr': float(row['WILLR']),
                                                'cci': float(row['CCI']),
                                                'bbup': float(row['upBB']),
                                                'bbmid': float(row['midBB']),
                                                'bblow': float(row['lowBB'])
                                                })
            print(response)
            response = post_data('signals', {'ticker': ticker[0]['id'],
                                             'timeframe': timeframe,
                                             'datetime': str(row['date_time']),
                                             'ma_fast_price_pos': float(row['MA_fast_price_pos']),
                                             'ma_fast_slow_pos': float(row['MA_fast_slow_pos']),
                                             'macd_chg': float(row['MACDchg']),
                                             'macd_div_short': float(row['MACDdiv_short']),
                                             'macd_div_long': float(row['MACDdiv_long']),
                                             'willr_rover_zones': float(row['WILLRoverZones']),
                                             'willr_div_short': float(row['WILLRdiv_short']),
                                             'willr_div_long': float(row['WILLRdiv_long']),
                                             'cci_over_zones': float(row['CCIoverZones']),
                                             'cci_div_short': float(row['CCIdiv_short']),
                                             'cci_div_long': float(row['CCIdiv_long']),
                                             'bb_touch': float(row['BBTouch']),
                                             'hummer': float(row['Hummer']),
                                             'shooting_star': float(row['ShootingStar']),
                                             'divbar': float(row['DivBar']),
                                             'sig_elder': float(row['sig_elder']),
                                             'sig_channel': float(row['sig_channel']),
                                             'sig_divbar': float(row['sig_DivBar']),
                                             'sig_nr4id': float(row['sig_NR4ID']),
                                             'sig_break_volatility': float(row['sig_breakVolatility'])
                                             })

            print(response)
    else:
        raise ValueError(f"Incorrect value for ticker - {ticker_code}")

## ends new api


config = configparser.ConfigParser()
config.read('settings.ini')


def get_ticker_id(ticker):
    '''
    Get ticker id from site

    :param ticker: short ticker name string, like 'GAZP'
    :return: id int
    '''
    if config['PANDORATRADINGSOLUTION']['test_env'] == 'False':
        url = config['PANDORATRADINGSOLUTION']['url']
    else:
        url = config['PANDORATRADINGSOLUTION']['url_test']

    responce = requests.get(url + 'marketdictionary/api/tickers/?format=json')

    ticker_id = 0
    for t in json.loads(responce.text)['tickers']:
        if t['short_name'] == ticker:
            ticker_id = t['id']

    return ticker_id


def get_ticker_name(ticker):
    '''
    Get ticker full name from site

    :param ticker: short ticker name string, like 'GAZP'
    :return: full name str
    '''
    if config['PANDORATRADINGSOLUTION']['test_env'] == 'False':
        url = config['PANDORATRADINGSOLUTION']['url']
    else:
        url = config['PANDORATRADINGSOLUTION']['url_test']

    responce = requests.get(url + 'marketdictionary/api/tickers/?format=json')

    ticker_name = ''
    for t in json.loads(responce.text)['tickers']:
        if t['short_name'] == ticker:
            ticker_name = t['ticker_name']

    return ticker_name


def gethorizonid(horizon):
    if config['PANDORATRADINGSOLUTION']['test_env'] == 'False':
        url = config['PANDORATRADINGSOLUTION']['url']
    else:
        url = config['PANDORATRADINGSOLUTION']['url_test']

    responce = requests.get(url + 'predictions/api/predictionhorizons/?format=json')

    horizon_id = 0
    for t in json.loads(responce.text)['horizons']:
        if t['horizon_name'] == horizon:
            horizon_id = t['id']

    return horizon_id


def createpost(postdata):
    if config['PANDORATRADINGSOLUTION']['test_env'] == 'False':
        url = config['PANDORATRADINGSOLUTION']['url']
    else:
        url = config['PANDORATRADINGSOLUTION']['url_test']

    r = requests.post(url=url + 'dailyanalysis/api/posts/', json=postdata)
    print('Post data: {0} \n'.format(postdata))
    print('Responce text: {0}'.format(r.text))
    return r.text


def createpredict(predictdata):
    if config['PANDORATRADINGSOLUTION']['test_env'] == 'False':
        url = config['PANDORATRADINGSOLUTION']['url']
    else:
        url = config['PANDORATRADINGSOLUTION']['url_test']

    r = requests.post(url=url + 'predictions/api/predictions/', json=predictdata)
    return r.text
