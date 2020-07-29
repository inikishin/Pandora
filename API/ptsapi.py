import requests
import json
import configparser

config = configparser.ConfigParser()
config.read('/home/ilya/PycharmProjects/Pandora/settings.ini')

def gettickerid(ticker):
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

    r = requests.post(url=url+'dailyanalysis/api/posts/', json=postdata)
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