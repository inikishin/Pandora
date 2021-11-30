import pandas as pd
import numpy as np
import talib as ta
import configparser
from sklearn.preprocessing import MinMaxScaler

config = configparser.ConfigParser()
config.read('settings.ini')

# Additional features block

def DIVERGENCE(high, low, ind, short_range, long_range):
    d = pd.DataFrame()
    d['high'] = high
    d['low'] = low
    d['ind'] = ind
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


def DIVBAR(high, low, close):
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


def BBTouch(bbUp, bbDown, high, low, perc):
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


def PrcntChng(close, n):
    d = pd.DataFrame()
    d['close'] = close
    d['prcntChng'] = 0

    i = 0
    for index, row in d.iterrows():
        d.iloc[i, 1] = d['close'][i] / d['close'][i - n] - 1
        i += 1

    return d.prcntChng


def OverZonesInd(ind, overB, overS):
    if ind > overB:
        return -1
    elif ind < overS:
        return 1
    else:
        return 0

# Return Series of regression line angles
def RegAngle(data, reg_n):
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

# Return angle and array of regression line points
def RegAngleLine(data, reg_n):
    z = np.polyfit(range(reg_n), data[-reg_n:], 1)
    p = np.poly1d(z)
    downsampled_reg = p(range(reg_n))
    downsampled_ugol_reg = RegAngle(data, reg_n)[-1]
    return downsampled_reg, downsampled_ugol_reg


def LinRegInterpreter(ugol):
    if ugol > 45:
        return 2
    elif ugol > 5:
        return 1
    elif ugol < -45:
        return -2
    elif ugol < -5:
        return -1
    else:
        return 0


def UpperTimeFrameCondition(downsampled_ugol_reg, MACD, MACDchg, MA_fast_price_pos, MA_fast_slow_pos):
    d = pd.DataFrame()
    d['downsampled_ugol_reg'] = downsampled_ugol_reg
    d['MACD'] = MACD
    d['MACDchg'] = MACDchg
    d['MA_fast_price_pos'] = MA_fast_price_pos
    d['MA_fast_slow_pos'] = MA_fast_slow_pos
    d['UpperTimeFrameCondition'] = 0

    i = 0
    for index, row in d.iterrows():
        if LinRegInterpreter(d.iloc[i, 0]) == 2 and d.iloc[i, 1] > 0 and d.iloc[i, 2] == 1 and d.iloc[i, 3] == 1 and \
                d.iloc[i, 4] == 1:
            d.iloc[i, 5] = 2
        elif LinRegInterpreter(d.iloc[i, 0]) == -2 and d.iloc[i, 1] < 0 and d.iloc[i, 2] == 0 and d.iloc[i, 3] == 0 and \
                d.iloc[i, 4] == 0:
            d.iloc[i, 5] = -2
        elif LinRegInterpreter(d.iloc[i, 0]) > 0 and d.iloc[i, 4] == 1:
            d.iloc[i, 5] = 1
        elif LinRegInterpreter(d.iloc[i, 0]) < 0 and d.iloc[i, 4] == 0:
            d.iloc[i, 5] = -1
        else:
            d.iloc[i, 5] = 0
        i += 1

    return d.UpperTimeFrameCondition
# Additional features endblock

#Signal features block

def sig_elder(w1_UpperTimeFrameCondition, WILLRoverZones):
    d = pd.DataFrame()
    d['w1_UpperTimeFrameCondition'] = w1_UpperTimeFrameCondition
    d['WILLRoverZones'] = WILLRoverZones
    d['sig_elder'] = 0

    i = 0
    for index, row in d.iterrows():
        if d.iloc[i, 0] < 0 and d.iloc[i, 1] < 0:
            d.iloc[i, 2] = -1
        if d.iloc[i, 0] > 0 and d.iloc[i, 1] > 0:
            d.iloc[i, 2] = 1
        i += 1

    return d.sig_elder


def sig_channel(BBTouch, CCIDiv_short, CCIDiv_long):
    d = pd.DataFrame()
    d['BBTouch'] = BBTouch
    d['CCIDiv_short'] = CCIDiv_short
    d['CCIDiv_long'] = CCIDiv_long
    d['sig_channel'] = 0

    i = 0
    for index, row in d.iterrows():
        if d.iloc[i, 0] < 0 and (d.iloc[i, 1] < 0 or d.iloc[i, 2] < 0):
            d.iloc[i, 3] = -1
        if d.iloc[i, 0] > 0 and (d.iloc[i, 1] > 0 or d.iloc[i, 2] > 0):
            d.iloc[i, 3] = 1
        i += 1

    return d.sig_channel


def sig_DivBar(close, MA_slow, divbar):
    d = pd.DataFrame()
    d['close'] = close
    d['MA_slow'] = MA_slow
    d['divbar'] = divbar
    d['sig_DivBar'] = 0

    i = 0
    for index, row in d.iterrows():
        if i < 26:
            d.iloc[i, 3] = np.nan
            i += 1
            continue
        # Расчет линии регрессии за последние 8 баров
        z = np.polyfit(range(8), d.iloc[i - 8:i, 0].values, 1)
        p = np.poly1d(z)
        df_short_reg_8 = p(range(8))

        # Расчет линии регрессии за последние 8 баров
        z = np.polyfit(range(8), d.iloc[i - 8:i, 1], 1)
        p = np.poly1d(z)
        df_shortma_reg_8 = p(range(8))

        df_short_ugol_8 = np.rad2deg(np.arctan2(df_short_reg_8[-1] - df_short_reg_8[1], len(df_short_reg_8) - 1))
        df_shortma_ugol_8 = np.rad2deg(
            np.arctan2(df_shortma_reg_8[-1] - df_shortma_reg_8[1], len(df_shortma_reg_8) - 1))

        if df_short_ugol_8 > 0 and df_short_ugol_8 > (df_shortma_ugol_8 + 15) and d.iloc[i, 2] < 0:
            d.iloc[i, 3] = -1

        if df_short_ugol_8 < 0 and df_short_ugol_8 < (df_shortma_ugol_8 - 15) and d.iloc[i, 2] > 0:
            d.iloc[i, 3] = 1
        i += 1

    return d.sig_DivBar


def sig_NR4ID(high, low):
    d = pd.DataFrame()
    d['high'] = high
    d['low'] = low
    d['sig_NR4ID'] = 0

    i = 0
    for index, row in d.iterrows():
        if (d.iloc[i, 0] < d.iloc[i - 1, 0] and d.iloc[i, 1] > d.iloc[i - 1, 1]) and (
                (d.iloc[i, 0] - d.iloc[i, 1]) <= (d.iloc[i - 4:i, 0] - d.iloc[i - 4:i, 1]).min()):
            d.iloc[i, 2] = 1
        i += 1

    return d.sig_NR4ID


def sig_breakVolatility(df_short_ugol_35, close, perc_var=0.1):
    d = pd.DataFrame()
    d['df_short_ugol_35'] = df_short_ugol_35
    d['close'] = close
    d['sig_breakVolatility'] = 0

    i = 0
    for index, row in d.iterrows():
        if (d.iloc[i, 0] > -12 and d.iloc[i, 0] < 12) and (np.var(d.iloc[i - 15:i, 1]) < (d.iloc[i, 1] * perc_var)):
            d.iloc[i, 2] = 1
        i += 1

    return d.sig_breakVolatility


#Signal features endblock

# Main function for create preprocessed data
def preprocessing_daily(market, ticker):
    # loading data
    df = pd.read_csv(config['PANDORA']['DataPath'] + market + '/' + ticker + '_data.csv')
    df['date_time'] = pd.to_datetime(df.date_time)
    df = df.set_index('date_time')

    # weekly data frame processing
    conversion = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'vol': 'sum'
    }
    downsampled_df = df.resample('W').apply(conversion)
    downsampled_df.fillna(method='bfill', inplace=True)

    reg_n = 8
    downsampled_df['prcntChng_5'] = PrcntChng(downsampled_df.close, 5)
    downsampled_df['prcntChng_15'] = PrcntChng(downsampled_df.close, 25)
    downsampled_df['regAngle_8'] = RegAngle(downsampled_df.close, reg_n)
    downsampled_df['regAngleInterpreter_8'] = downsampled_df['regAngle_8'].apply(LinRegInterpreter)
    downsampled_df['MA_fast'] = ta.EMA(downsampled_df.close, 8)
    downsampled_df['MA_slow'] = ta.EMA(downsampled_df.close, 13)
    downsampled_df['MA_fast_price_pos'] = downsampled_df.close - downsampled_df.MA_fast
    downsampled_df['MA_fast_price_pos'] = downsampled_df.MA_fast_price_pos.apply(lambda x: 1 if x > 0 else 0)
    downsampled_df['MA_fast_slow_pos'] = downsampled_df.MA_fast - downsampled_df.MA_slow
    downsampled_df['MA_fast_slow_pos'] = downsampled_df.MA_fast_slow_pos.apply(lambda x: 1 if x > 0 else 0)
    downsampled_df['MACD'], _, _ = ta.MACD(downsampled_df.close, fastperiod=5, slowperiod=35, signalperiod=3)
    downsampled_df['MACDchg'] = downsampled_df['MACD'].shift(1)
    downsampled_df['MACDchg'] = downsampled_df['MACD'] - downsampled_df['MACDchg']
    downsampled_df['MACDchg'] = downsampled_df['MACDchg'].apply(lambda x: 1 if x > 0 else 0)
    downsampled_df['MACDdiv'] = DIVERGENCE(downsampled_df.high, downsampled_df.low, downsampled_df.MACD, 3, 8)
    downsampled_df['WILLR'] = ta.WILLR(downsampled_df.high, downsampled_df.low, downsampled_df.close, timeperiod=8)
    downsampled_df['WILLRoverZones'] = downsampled_df.WILLR.apply(OverZonesInd, args=[-20, -80])
    downsampled_df['WILLRdiv_short'] = DIVERGENCE(downsampled_df.high, downsampled_df.low, downsampled_df.WILLR, 3, 8)
    downsampled_df['WILLRdiv_long'] = DIVERGENCE(downsampled_df.high, downsampled_df.low, downsampled_df.WILLR, 5, 35)
    downsampled_df['Hummer'] = ta.CDLHAMMER(downsampled_df.open, downsampled_df.high, downsampled_df.low,
                                            downsampled_df.close)
    downsampled_df['ShootingStar'] = ta.CDLSHOOTINGSTAR(downsampled_df.open, downsampled_df.high, downsampled_df.low,
                                                        downsampled_df.close)
    downsampled_df['DivBar'] = DIVBAR(downsampled_df.high, downsampled_df.low, downsampled_df.close)
    downsampled_df['UpperTimeFrameCondition'] = UpperTimeFrameCondition(downsampled_df['regAngle_8'],
                                                                        downsampled_df['MACD'],
                                                                        downsampled_df['MACDchg'],
                                                                        downsampled_df['MA_fast_price_pos'],
                                                                        downsampled_df['MA_fast_slow_pos'])
    downsampled_df.dropna(inplace=True)

    # daily dataframe processing
    df['regAngle_8'] = RegAngle(df.close, 8)
    df['regAngleInterpreter_8'] = df['regAngle_8'].apply(LinRegInterpreter)
    df['regAngle_35'] = RegAngle(df.close, 35)
    df['regAngleInterpreter_35'] = df['regAngle_35'].apply(LinRegInterpreter)
    df['MA_fast'] = ta.EMA(df.close, 8)
    df['MA_slow'] = ta.EMA(df.close, 13)
    df['MA_fast_price_pos'] = df.close - df.MA_fast
    df['MA_fast_price_pos'] = df.MA_fast_price_pos.apply(lambda x: 1 if x > 0 else 0)
    df['MA_fast_slow_pos'] = df.MA_fast - df.MA_slow
    df['MA_fast_slow_pos'] = df.MA_fast_slow_pos.apply(lambda x: 1 if x > 0 else 0)
    df['MACD'], _, _ = ta.MACD(df.close, fastperiod=5, slowperiod=35, signalperiod=3)
    df['MACDchg'] = df['MACD'].shift(1)
    df['MACDchg'] = df['MACD'] - df['MACDchg']
    df['MACDchg'] = df['MACDchg'].apply(lambda x: 1 if x > 0 else 0)
    df['MACDdiv_short'] = DIVERGENCE(df.high, df.low, df.MACD, 3, 8)
    df['MACDdiv_long'] = DIVERGENCE(df.high, df.low, df.MACD, 5, 35)
    df['WILLR'] = ta.WILLR(df.high, df.low, df.close, timeperiod=8)
    df['WILLRoverZones'] = df.WILLR.apply(OverZonesInd, args=[-20, -80])
    df['WILLRdiv_short'] = DIVERGENCE(df.high, df.low, df.WILLR, 3, 8)
    df['WILLRdiv_long'] = DIVERGENCE(df.high, df.low, df.WILLR, 5, 35)
    df['CCI'] = ta.CCI(df.high, df.low, df.close, timeperiod=12)
    df['CCIoverZones'] = df.CCI.apply(OverZonesInd, args=[100, -100])
    df['CCIdiv_short'] = DIVERGENCE(df.high, df.low, df.CCI, 3, 8)
    df['CCIdiv_long'] = DIVERGENCE(df.high, df.low, df.CCI, 5, 35)
    df['upBB'], df['midBB'], df['lowBB'] = ta.BBANDS(df.close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
    df['BBTouch'] = BBTouch(df['upBB'], df['lowBB'], df.high, df.low, 0.1)
    df['Hummer'] = ta.CDLHAMMER(df.open, df.high, df.low, df.close)
    df['ShootingStar'] = ta.CDLSHOOTINGSTAR(df.open, df.high, df.low, df.close)
    df['DivBar'] = DIVBAR(df.high, df.low, df.close)

    # добавляем данные с недельного ТФ
    resample_bfill = downsampled_df.resample('D').bfill()
    new_list = []
    for c in resample_bfill.columns:
        new_list.append('w1_' + c)
    resample_bfill.columns = new_list
    df = df.merge(right=resample_bfill, how='left', on='date_time')

    df['sig_elder'] = sig_elder(df.w1_UpperTimeFrameCondition, df.WILLRoverZones)
    df['sig_channel'] = sig_channel(df.BBTouch, df.CCIdiv_short, df.CCIdiv_long)
    df['sig_DivBar'] = sig_DivBar(df.close, df.MA_slow, df.DivBar)
    df['sig_NR4ID'] = sig_NR4ID(df.high, df.low)
    df['sig_breakVolatility'] = sig_breakVolatility(df.regAngle_35, df.close)

    df.to_csv(config['PANDORA']['DataPath'] + market + '/' + ticker + '_processeddata.csv')

    return 'success!'