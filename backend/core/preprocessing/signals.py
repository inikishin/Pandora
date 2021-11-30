import pandas as pd
import numpy as np

# TODO Вернуть позже
def sig_elder(w1_UpperTimeFrameCondition, WILLRoverZones):
    d = pd.DataFrame()
    # d['w1_UpperTimeFrameCondition'] = w1_UpperTimeFrameCondition
    # d['WILLRoverZones'] = WILLRoverZones
    d['sig_elder'] = 0

    # i = 0
    # for index, row in d.iterrows():
    #     if d.iloc[i, 0] < 0 and d.iloc[i, 1] < 0:
    #         d.iloc[i, 2] = -1
    #     if d.iloc[i, 0] > 0 and d.iloc[i, 1] > 0:
    #         d.iloc[i, 2] = 1
    #     i += 1

    return d.sig_elder


def sig_channel(bb_touch: pd.Series, cci_divergence_short: pd.Series, cci_divergence_long: pd.Series) -> pd.Series:
    d = pd.DataFrame()
    d['BBTouch'] = bb_touch
    d['CCIDiv_short'] = cci_divergence_short
    d['CCIDiv_long'] = cci_divergence_long
    d['sig_channel'] = 0

    i = 0
    for index, row in d.iterrows():
        if d.iloc[i, 0] < 0 and (d.iloc[i, 1] < 0 or d.iloc[i, 2] < 0):
            d.iloc[i, 3] = -1
        if d.iloc[i, 0] > 0 and (d.iloc[i, 1] > 0 or d.iloc[i, 2] > 0):
            d.iloc[i, 3] = 1
        i += 1

    return d.sig_channel


def sig_divbar(close: pd.Series, ma_slow: pd.Series, divbar: pd.Series) -> pd.Series:
    d = pd.DataFrame()
    d['close'] = close
    d['MA_slow'] = ma_slow
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


def sig_nr4id(high: pd.Series, low: pd.Series) -> pd.Series:
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


def sig_break_volatility(df_short_ugol_35: pd.Series, close: pd.Series, perc_var: float = 0.1) -> pd.Series:
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


def extend_dataframe_with_signals(initial_dataframe: pd.DataFrame) -> pd.DataFrame:
    df = initial_dataframe

    df['sig_channel'] = sig_channel(df.bb_touch, df.cci_divergence_short, df.cci_divergence_long)
    df['sig_divbar'] = sig_divbar(df.close, df.ma_slow, df.divbar)
    df['sig_nr4id'] = sig_nr4id(df.high, df.low)
    df['sig_break_volatility'] = sig_break_volatility(df.bb_touch, df.cci_divergence_short, df.cci_divergence_long)
    df['sig_elder'] = sig_elder(df.regression_angle_long, df.close)

    return df