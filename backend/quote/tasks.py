import os
import pandas as pd
from celery import shared_task
from django_pandas.io import read_frame
from django.db.models import Max
from .models import Quote, Market, Timeframe, Ticker, BondAdditionalInfo, Currency, StockExchange, FeaturedQuotes
from trading_strategy.models import TradingStrategy, Signal
from core.preprocessing import features, signals
import api.moex as api_moex


@shared_task
def load_quotes_from_moex_api(ticker_code: str) -> None:
    ticker = Ticker.objects.get(code=ticker_code)
    stock_exchange = StockExchange.objects.get(code='moex')
    timeframe_d1 = Timeframe.objects.get(code='D1')
    max_date = Quote.objects.filter(ticker=ticker, timeframe=timeframe_d1).aggregate(Max('datetime'))

    if ticker.market.stock_exchange == stock_exchange:
        history_df = api_moex.load_quotes(ticker=ticker.code, market=ticker.market.type.code, from_date=max_date['datetime__max'], interval='24')
        if len(history_df) > 0:
            for index, row in history_df.iterrows():
                Quote.objects.update_or_create(
                    ticker=ticker, timeframe=timeframe_d1, datetime=row['datetime'],
                    defaults={'ticker': ticker, 'timeframe': timeframe_d1, 'datetime': row['datetime'],
                              'open': row['open'], 'high': row['high'], 'low': row['low'], 'close': row['close'],
                              'volume': row['volume']}
                )
            print(f'Loading quotes for {ticker} ended')


@shared_task
def load_quotes_from_csv_file(ticker_code: str) -> None:
    ticker = Ticker.objects.get(code=ticker_code)
    timeframe_d1 = Timeframe.objects.get(code='D1')
    catalogs = os.getenv('QUOTES_IMPORT_CATALOGS').split(';')
    filename = f'{ticker_code.upper()}_D1.csv'
    files = []
    print(catalogs)
    if len(catalogs) > 0:
        for c in catalogs:
            print(c + '/' + filename)
            if os.path.isfile(c + '/' + filename):
                files.append(c + '/' + filename)
    else:
        print(f'No catalogues in env variable QUOTES_IMPORT_CATALOGS')

    if len(files) == 0:
        print(f'For ticker {ticker_code} no quotes in csv data files')
    elif len(files) > 1:
        print(f'For ticker {ticker_code} more than one csv file in catalogues. File list: {files}')
    else:
        history_df = pd.read_csv(files[0])
        history_df['date_time'] = pd.to_datetime(history_df.date_time)
        history_df.dropna(inplace=True)

        if len(history_df) > 0:
            for index, row in history_df.iterrows():
                Quote.objects.update_or_create(
                    ticker=ticker, timeframe=timeframe_d1, datetime=row['date_time'],
                    defaults={'ticker': ticker, 'timeframe': timeframe_d1, 'datetime': row['date_time'],
                              'open': row['open'], 'high': row['high'], 'low': row['low'], 'close': row['close'],
                              'volume': row['vol']}
                )
            print(f'Loading quotes for {ticker} ended')


@shared_task
def load_bonds_list_from_moex() -> None:
    bonds_list = api_moex.get_ticker_list(market='bonds')
    usd_currency = Currency.objects.get(code='USD')
    eur_currency = Currency.objects.get(code='EUR')
    rub_currency = Currency.objects.get(code='RUB')

    for index, bond in bonds_list.iterrows():
        try:
            ticker = Ticker.objects.get(code=bond['code'])
        except Ticker.DoesNotExist:
            moex_market = Market.objects.get(code='moex-bonds')
            ticker = Ticker(code=bond['code'], fullname=bond['fullname'], market=moex_market)
            ticker.save()

        currency = rub_currency
        if bond['currency'] == 'USD':
            currency = usd_currency
        elif bond['currency'] == 'EUR':
            currency = eur_currency
        elif bond['currency'] != 'SUR':
            raise Exception(f'Unknown currency in bond ticker: {bond["currency"]}')

        BondAdditionalInfo.objects.update_or_create(ticker=ticker,
                                                    defaults=
                                                    {'ticker': ticker,
                                                     'short_name': bond['short_name'],
                                                     'code_isin': bond['code_isin'],
                                                     'gov_reg_number': bond['gov_reg_number'],
                                                     'issue_size': bond['issue_size'],
                                                     'currency': currency,
                                                     'lot_size': bond['lot_size'],
                                                     'lot_value': bond['lot_value'],
                                                     'min_step': bond['min_step'],
                                                     'list_level': bond['list_level'],
                                                     'status': bond['status'],
                                                     'coupon_percent': bond['coupon_percent'],
                                                     'coupon_period': bond['coupon_period'],
                                                     'coupon_value': bond['coupon_value'],
                                                     'maturity_date': bond['maturity_date'] if bond[
                                                                                                   'maturity_date'] != '0000-00-00' else None,
                                                     'next_coupon_date': bond['next_coupon_date'] if bond[
                                                                                                         'next_coupon_date'] != '0000-00-00' else None,
                                                     'accumulated_coupon_yield': bond['accumulated_coupon_yield']}
                                                    );

    print(f'Loading bonds ended')


@shared_task
def preprocessing_quotes(ticker_code: str):
    ticker = Ticker.objects.get(code=ticker_code)
    timeframe_d1 = Timeframe.objects.get(code='D1')
    quotes = Quote.objects.filter(ticker=ticker, timeframe=timeframe_d1)
    df = read_frame(quotes)
    df['datetime'] = pd.to_datetime(df.datetime)
    df = df.set_index('datetime')

    df = features.extend_dataframe_with_features(df)
    df = signals.extend_dataframe_with_signals(df)

    db_object_sig_channel = TradingStrategy.objects.get(code='sig_channel')
    db_object_sig_divbar = TradingStrategy.objects.get(code='sig_divbar')
    db_object_sig_nr4id = TradingStrategy.objects.get(code='sig_nr4id')
    db_object_sig_break_volatility = TradingStrategy.objects.get(code='sig_break_volatility')
    db_object_sig_elder = TradingStrategy.objects.get(code='sig_elder')

    for index, item in df.iterrows():
        FeaturedQuotes.objects.update_or_create(ticker=ticker, timeframe=timeframe_d1, datetime=index,
                                                defaults={
                                                    'ticker': ticker,
                                                    'timeframe': timeframe_d1,
                                                    'datetime': index,
                                                    'regression_angle_short': item['regression_angle_short'],
                                                    'regression_angle_short_interpreter': item[
                                                        'regression_angle_short_interpreter'],
                                                    'regression_angle_long': item['regression_angle_long'],
                                                    'regression_angle_long_interpreter': item[
                                                        'regression_angle_long_interpreter'],
                                                    'ma_fast': item['ma_fast'],
                                                    'ma_slow': item['ma_slow'],
                                                    'ma_fast_position_at_price': item['ma_fast_position_at_price'],
                                                    'ma_fast_position_at_ma_slow': item[
                                                        'ma_fast_position_at_ma_slow'],
                                                    'macd': item['macd'],
                                                    'macd_change': item['macd_change'],
                                                    'macd_divergence_short': item['macd_divergence_short'],
                                                    'macd_divergence_long': item['macd_divergence_long'],
                                                    'williams': item['williams'],
                                                    'williams_over_zones': item['williams_over_zones'],
                                                    'williams_divergence_short': item['williams_divergence_short'],
                                                    'williams_divergence_long': item['williams_divergence_long'],
                                                    'cci': item['cci'],
                                                    'cci_over_zones': item['cci_over_zones'],
                                                    'cci_divergence_short': item['cci_divergence_short'],
                                                    'cci_divergence_long': item['cci_divergence_long'],
                                                    'up_bb': item['up_bb'],
                                                    'mid_bb': item['mid_bb'],
                                                    'low_bb': item['low_bb'],
                                                    'bb_touch': item['bb_touch'],
                                                    'hummer': item['hummer'],
                                                    'shooting_star': item['shooting_star'],
                                                    'divbar': item['divbar'],
                                                })

        Signals.objects.update_or_create(ticker=ticker, timeframe=timeframe_d1, datetime=index,
                                         trading_strategy=db_object_sig_channel,
                                         defaults={
                                             'ticker': ticker,
                                             'timeframe': timeframe_d1,
                                             'datetime': index,
                                             'trading_strategy': db_object_sig_channel,
                                             'value': item['sig_channel']
                                         })

        Signals.objects.update_or_create(ticker=ticker, timeframe=timeframe_d1, datetime=index,
                                         trading_strategy=db_object_sig_divbar,
                                         defaults={
                                             'ticker': ticker,
                                             'timeframe': timeframe_d1,
                                             'datetime': index,
                                             'trading_strategy': db_object_sig_divbar,
                                             'value': item['sig_divbar']
                                         })

        Signals.objects.update_or_create(ticker=ticker, timeframe=timeframe_d1, datetime=index,
                                         trading_strategy=db_object_sig_nr4id,
                                         defaults={
                                             'ticker': ticker,
                                             'timeframe': timeframe_d1,
                                             'datetime': index,
                                             'trading_strategy': db_object_sig_nr4id,
                                             'value': item['sig_nr4id']
                                         })

        Signals.objects.update_or_create(ticker=ticker, timeframe=timeframe_d1, datetime=index,
                                         trading_strategy=db_object_sig_break_volatility,
                                         defaults={
                                             'ticker': ticker,
                                             'timeframe': timeframe_d1,
                                             'datetime': index,
                                             'trading_strategy': db_object_sig_break_volatility,
                                             'value': item['sig_break_volatility']
                                         })

        Signals.objects.update_or_create(ticker=ticker, timeframe=timeframe_d1, datetime=index,
                                         trading_strategy=db_object_sig_elder,
                                         defaults={
                                             'ticker': ticker,
                                             'timeframe': timeframe_d1,
                                             'datetime': index,
                                             'trading_strategy': db_object_sig_elder,
                                             'value': item['sig_elder']
                                         })
