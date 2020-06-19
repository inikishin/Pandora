import requests
import json
import configparser

config = configparser.ConfigParser()
config.read('/home/ilya/PycharmProjects/Pandora/settings.ini')

def gettickerid(ticker):
    responce = requests.get(config['PANDORATRADINGSOLUTION']['url'] + 'marketdictionary/api/tickers/?format=json')

    ticker_id = 0
    for t in json.loads(responce.text)['tickers']:
        if t['short_name'] == ticker:
            ticker_id = t['id']

    return ticker_id

def createpost(postdata):
    r = requests.post(url=config['PANDORATRADINGSOLUTION']['url']+'dailyanalysis/api/posts/', json=postdata)
    return r.text