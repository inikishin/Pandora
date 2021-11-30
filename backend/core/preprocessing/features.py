import pandas as pd
import time
import numpy as np
import talib as ta
from sklearn.preprocessing import MinMaxScaler


def divergence(high: pd.Series, low: pd.Series, index: pd.Series, short_range: int, long_range: int) -> pd.Series:
    d = pd.DataFrame()
    d['high'] = high
    d['low'] = low
    d['ind'] = index
    d['high_' + str(short_range) + '_max'] = 0.0
    d['high_' + str(long_range) + '_max'] = 0.0
    d['low_' + str(short_range) + '_min'] = 0.0
    d['low_' + str(long_range) + '_min'] = 0.0
    d['ind_' + str(short_range) + '_max'] = 0.0
    d['ind_' + str(short_range) + '_min'] = 0.0
    d['ind_' + str(long_range) + '_max'] = 0.0
    d['ind_' + str(long_range) + '_min'] = 0.0
    d['ind_div'] = 0

    i = 0
    for index, row in d.iterrows():
        d.iloc[i, 3] = d['high'][i - short_range + 1:i + 1].max()
        d.iloc[i, 4] = d['high'][i - long_range + 1:i + 1].max()
        d.iloc[i, 5] = d['low'][i - short_range + 1:i + 1].min()
        d.iloc[i, 6] = d['low'][i - long_range + 1:i + 1].min()
        d.iloc[i, 7] = d['ind'][i - short_range + 1:i + 1].max()
        d.iloc[i, 8] = d['ind'][i - short_range + 1:i + 1].min()
        d.iloc[i, 9] = d['ind'][i - long_range + 1:i + 1].max()
        d.iloc[i, 10] = d['ind'][i - long_range + 1:i + 1].min()

        if d.iloc[i, 3] == d.iloc[i, 4] and d.iloc[i, 7] < d.iloc[i, 9]:
            d.iloc[i, 11] = -100
        elif d.iloc[i, 5] == d.iloc[i, 6] and d.iloc[i, 8] > d.iloc[i, 10]:
            d.iloc[i, 11] = 100
        else:
            d.iloc[i, 11] = 0
        i += 1

    return d.ind_div


def divbar(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    d = pd.DataFrame()
    d['high'] = high
    d['low'] = low
    d['close'] = close
    d['high_3_max'] = 0.0
    d['low_3_min'] = 0.0
    d['divbar'] = 0

    i = 0
    for index, row in d.iterrows():
        d.iloc[i, 3] = d['high'][i - 3 + 1:i + 1].max()
        d.iloc[i, 4] = d['low'][i - 3 + 1:i + 1].min()
        if d.iloc[i, 3] == d.iloc[i, 0] and (d.iloc[i, 2] < ((d.iloc[i, 0] - d.iloc[i, 1]) / 3 + d.iloc[i, 1])):
            d.iloc[i, 5] = -100
        if d.iloc[i, 4] == d.iloc[i, 1] and (d.iloc[i, 2] > (d.iloc[i, 0] - (d.iloc[i, 0] - d.iloc[i, 1]) / 3)):
            d.iloc[i, 5] = 100
        i += 1
    return d.divbar


def bb_touch(bbUp: pd.Series, bbDown: pd.Series, high: pd.Series, low: pd.Series, perc: float) -> pd.Series:
    d = pd.DataFrame()
    d['bbUp'] = bbUp
    d['bbDown'] = bbDown
    d['high'] = high
    d['low'] = low

    d['upBorder'] = d.bbUp - (d.bbUp - d.bbDown) * perc
    d['downBorder'] = (d.bbUp - d.bbDown) * perc + d.bbDown

    d['upTouch'] = np.where(d['high'] > d['upBorder'], -1, 0)
    d['downTouch'] = np.where(d['low'] < d['downBorder'], 1, 0)

    return d['upTouch'] + d['downTouch']


def percent_change(close: pd.Series, n: int) -> pd.Series:
    d = pd.DataFrame()
    d['close'] = close
    d['prcntChng'] = 0

    i = 0
    for index, row in d.iterrows():
        d.iloc[i, 1] = d['close'][i] / d['close'][i - n] - 1
        i += 1

    return d.prcntChng


def over_zones_indicator(indicator_value: float, overbought: float, oversold: float) -> int:
    if indicator_value > overbought:
        return -1
    elif indicator_value < oversold:
        return 1
    else:
        return 0


def regression_line_angle(data, reg_n):
    d = pd.DataFrame()
    d['data'] = data
    d['angle'] = 0

    i = 0
    for index, row in d.iterrows():
        if i < reg_n + 1:
            d.iloc[i, 1] = 0
        else:
            try:
                scaler = MinMaxScaler(feature_range=(0, 20))
                scaled_data = scaler.fit_transform(d['data'][i - reg_n + 1:i + 1].values.reshape(-1, 1)).reshape(-1)
                z = np.polyfit(range(reg_n), scaled_data, 1)

                p = np.poly1d(z)
                data_reg = p(range(reg_n))
                reg_Angle = np.rad2deg(np.arctan2(data_reg[-1] - data_reg[1], len(data_reg) - 1))
            except:
                print('Error in RegAngle: i {0}, array: {1}'.format(i, d['data'][i - reg_n + 1:i + 1]))
                reg_Angle = 0
            d.iloc[i, 1] = reg_Angle
        i += 1

    return d.angle


def regression_line_interpreter(angle):
    if angle > 45:
        return 2
    elif angle > 5:
        return 1
    elif angle < -45:
        return -2
    elif angle < -5:
        return -1
    else:
        return 0


def get_available_features_list():
    return [
        {
            'name': 'MA',
            'description': 'Simple moving average',
            'params': {
                'period': {'type': 'integer', 'default': 8, 'description': 'Simple moving average period'}
            }
        },
        {
            'name': 'AO',
            'description': 'Awesome oscillator',
            'params': {}
        },
    ]


def extend_dataframe_with_features(initial_dataframe: pd.DataFrame, features=[]) -> pd.DataFrame:
    df = initial_dataframe.copy()

    if len(features) > 0:
        for feature in features:

            if feature['name'] == 'MA':
                df[feature['code']] = ta.EMA(df.close, feature['params']['period'])



    # TODO Засунуть параметры в какой-нибудь файл конфигурации
    # df['regression_angle_short'] = regression_line_angle(df.close, 8)
    # df['regression_angle_short_interpreter'] = df['regression_angle_short'].apply(regression_line_interpreter)
    # df['regression_angle_long'] = regression_line_angle(df.close, 35)
    # df['regression_angle_long_interpreter'] = df['regression_angle_long'].apply(regression_line_interpreter)
    # df['ma_fast'] = ta.EMA(df.close, 8)
    # df['ma_slow'] = ta.EMA(df.close, 13)
    # df['ma_fast_position_at_price'] = df.close - df.ma_fast
    # df['ma_fast_position_at_price'] = df.ma_fast_position_at_price.apply(lambda x: 1 if x > 0 else 0)
    # df['ma_fast_position_at_ma_slow'] = df.ma_fast - df.ma_slow
    # df['ma_fast_position_at_ma_slow'] = df.ma_fast_position_at_ma_slow.apply(lambda x: 1 if x > 0 else 0)
    # df['macd'], _, _ = ta.MACD(df.close, fastperiod=5, slowperiod=35, signalperiod=3)
    # df['macd_change'] = df['macd'].shift(1)
    # df['macd_change'] = df['macd'] - df['macd_change']
    # df['macd_change'] = df['macd_change'].apply(lambda x: 1 if x > 0 else 0)
    # df['macd_divergence_short'] = divergence(df.high, df.low, df.macd, 3, 8)
    # df['macd_divergence_long'] = divergence(df.high, df.low, df.macd, 5, 35)
    # df['williams'] = ta.WILLR(df.high, df.low, df.close, timeperiod=8)
    # df['williams_over_zones'] = df.williams.apply(over_zones_indicator, args=[-20, -80])
    # df['williams_divergence_short'] = divergence(df.high, df.low, df.williams, 3, 8)
    # df['williams_divergence_long'] = divergence(df.high, df.low, df.williams, 5, 35)
    # df['cci'] = ta.CCI(df.high, df.low, df.close, timeperiod=12)
    # df['cci_over_zones'] = df.cci.apply(over_zones_indicator, args=[100, -100])
    # df['cci_divergence_short'] = divergence(df.high, df.low, df.cci, 3, 8)
    # df['cci_divergence_long'] = divergence(df.high, df.low, df.cci, 5, 35)
    # df['up_bb'], df['mid_bb'], df['low_bb'] = ta.BBANDS(df.close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
    # df['bb_touch'] = bb_touch(df.up_bb, df.low_bb, df.high, df.low, 0.1)
    # df['hummer'] = ta.CDLHAMMER(df.open, df.high, df.low, df.close)
    # df['shooting_star'] = ta.CDLSHOOTINGSTAR(df.open, df.high, df.low, df.close)
    # df['divbar'] = divbar(df.high, df.low, df.close)

    df['datetime'] = df['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
    df.set_index('datetime', inplace=True)

    return df