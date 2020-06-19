import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import uuid
from datetime import datetime
from preprocessing import preprocessing
from API import ptsapi
import configparser
import ftplib
from PIL import Image, ImageDraw, ImageFont

# Init config file
config = configparser.ConfigParser()
config.read('/home/ilya/PycharmProjects/Pandora/settings.ini')

def saveimg(img_name, image_folder, fig, ftp):
    fig.write_image(image_folder + img_name)
    image = Image.open(image_folder + img_name)
    image = image.resize((750, 600), Image.ANTIALIAS)
    drawing = ImageDraw.Draw(image)
    drawing.text((70, 80),
                 'www.pandoratradingsolutions.ru',
                 fill=(160, 160, 160),
                 font=ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 10))
    image.save(image_folder + img_name, 'png')
    with open(image_folder + img_name, 'rb') as fobj:
        ftp.storbinary('STOR ' + img_name, fobj, 8192)

def weeklyanalysisblock(df, ticker, doc_uuid, image_folder, is_show_figs, ftp):

    # downsample to weeks
    conversion = {
        'w1_open': 'last',
        'w1_high': 'last',
        'w1_low': 'last',
        'w1_close': 'last',
        'w1_vol': 'last',
        'w1_MA_fast': 'last',
        'w1_MA_slow': 'last',
        'w1_MACD': 'last',
        'w1_WILLR': 'last',
        'w1_regAngle_8': 'last',
        'w1_regAngleInterpreter_8': 'last',
        'w1_prcntChng_5': 'last',
        'w1_prcntChng_15': 'last',
        'w1_MA_fast_price_pos': 'last',
        'w1_MA_fast_slow_pos': 'last',
        'w1_MACDchg': 'last',
        'w1_MACDdiv': 'last',
        'w1_WILLRoverZones': 'last',
        'w1_WILLRdiv_short': 'last',
        'w1_WILLRdiv_long': 'last',
        'w1_Hummer': 'last',
        'w1_ShootingStar': 'last',
        'w1_DivBar': 'last',
        'w1_UpperTimeFrameCondition': 'last'
    }
    downsampled_df = df.resample('W').apply(conversion)
    downsampled_df.dropna(inplace=True)
    research_window = 100  # Число баров для анализа
    downsampled_df = downsampled_df[-research_window:]

    # Расчет линии регрессии за последние 8 баров
    downsampled_reg, downsampled_ugol_reg = preprocessing.RegAngleLine(downsampled_df.w1_close, 8)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.2, 0.2])

    fig.add_trace(go.Candlestick(x=downsampled_df.index,
                                 open=downsampled_df['w1_open'],
                                 high=downsampled_df['w1_high'],
                                 low=downsampled_df['w1_low'],
                                 close=downsampled_df['w1_close'],
                                 name=ticker),
                  row=1, col=1)
    # **********************************************************************************************************
    fig.add_trace(go.Scatter(
        x=downsampled_df.index,
        y=downsampled_df['w1_MA_fast'],
        name="Быстрое MA",
        line_color='red',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=downsampled_df.index,
        y=downsampled_df['w1_MA_slow'],
        name="Медленное MA",
        line_color='blue',
        opacity=1),
        row=1, col=1)
    # **********************************************************************************************************
    if downsampled_reg[-1] < downsampled_reg[-2]:
        reg_col = 'red'
    else:
        reg_col = 'green'
    fig.add_trace(go.Scatter(
        x=downsampled_df.index[-8:],  # reg_n
        y=downsampled_reg,
        name="Линия регрессии: " + str(round(downsampled_ugol_reg, 0)) + ' град.',
        line_color=reg_col,
        opacity=1),
        row=1, col=1)
    # **********************************************************************************************************
    fig.add_trace(go.Bar(x=downsampled_df.index,
                         y=downsampled_df.w1_MACD,
                         name="MACD"),
                  row=2, col=1)
    # **********************************************************************************************************
    fig.add_trace(go.Scatter(x=downsampled_df.index,
                             y=downsampled_df.w1_WILLR,
                             name="%Willams"),
                  row=3, col=1)
    # **********************************************************************************************************
    fig.update_yaxes(title_text="График цены", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="%Willams", row=3, col=1)
    fig.update_layout(height=800, width=1000, xaxis_rangeslider_visible=False)

    if is_show_figs:
        fig.show()

    img_name = ticker + "_weekly_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Анализ недельного графика  \n'

    # Цена. Процент изменения цены и линия регрессии
    annot_str = 'За последние 5 недель изменение цены составило ' + str(
        round(downsampled_df.w1_prcntChng_5[-1] * 100, 2)) + '%, что свидетельствует о ' + (
                    'краткосрочном росте цен. ' if downsampled_df.w1_prcntChng_5[
                                                       -1] > 0 else 'краткосрочном падении цен. ')
    annot_str = annot_str + 'Долгосрочное изменение цены (за последние полгода) составлет ' + str(
        round(downsampled_df.w1_prcntChng_15[-1] * 100, 2)) + '%. '
    content = content + annot_str

    annot_str = 'Линия регрессии, построенная за последние 8 недель, направлена ' + (
        'вниз' if downsampled_reg[-1] < downsampled_reg[-2] else 'вверх') + '. '
    annot_str = annot_str + 'Угол наклона составляет ' + str(round(downsampled_ugol_reg, 1)) + ' градусов. '
    content = content + annot_str

    # MA
    annot_str = 'Цена находится ' + (
        'выше' if downsampled_df.w1_MA_fast_price_pos[-1] == 1 else 'ниже') + ' быстрой скользящей средней. '
    annot_str = annot_str + 'Быстрая скользящая средняя, в свою очередь, находится ' + (
        'выше' if downsampled_df.w1_MA_fast_slow_pos[-1] == 1 else 'ниже') + ' медленной скользящей средней. '
    annot_str = annot_str + 'Все это говорит о том, что сейчас на рынке наблюдается '
    if downsampled_df.w1_MA_fast_price_pos[-1] == 1 and downsampled_df.w1_MA_fast_slow_pos[-1] == 1:
        annot_str = annot_str + 'сильный восходящий тренд. '
    elif downsampled_df.w1_MA_fast_price_pos[-1] == 0 and downsampled_df.w1_MA_fast_slow_pos[-1] == 0:
        annot_str = annot_str + 'сильный нисходящий тренд. '
    else:
        annot_str = annot_str + 'разнонаправленное горизонтальное движение рынка или наблюдается смена тренда.'
    content = content + annot_str + '  \n'

    # MACD
    annot_str = 'Индикатор MACD находится ' + (
        'выше' if downsampled_df.w1_MACD[-1] > 0 else 'ниже') + ' нулевой линии, '
    annot_str = annot_str + 'его значения ' + (
        'снижаются. ' if downsampled_df.w1_MACDchg[-1] == 0 else 'повышаются. ')
    if downsampled_df.w1_MACDdiv[-1] > 0:
        annot_str = annot_str + 'Также присутствует бычье расхождение между ценой и индикатором MACD. '
    if downsampled_df.w1_MACDdiv[-1] < 0:
        annot_str = annot_str + 'Также присутствует медвежье расхождение между ценой и индикатором MACD. '
    content = content + annot_str

    # Осцилляторы
    annot_str = 'Значение индикатора %Williams равно ' + str(round(downsampled_df.w1_WILLR[-1], 0)) + '. '

    if downsampled_df.w1_WILLRoverZones[-1] > 0:
        annot_str = annot_str + 'Он находится в зоне перепроданности. '
    elif downsampled_df.w1_WILLRoverZones[-1] < 0:
        annot_str = annot_str + 'Он находится в зоне перекупленности. '
    else:
        annot_str = annot_str + 'Он не находится на текущий момент в экстремальных зонах. '

    if downsampled_df.w1_WILLRdiv_short[-1] > 0:
        annot_str = annot_str + 'Также присутствует краткосрочное бычье расхождение между ценой и индикатором %Williams. Что может говорить о скором появлении восходящего движения цены. '
    if downsampled_df.w1_WILLRdiv_short[-1] < 0:
        annot_str = annot_str + 'Также присутствует краткосрочное медвежье расхождение между ценой и индикатором %Williams. Что может говорить о скором появлении нисходящего движения цены. '

    if downsampled_df.w1_WILLRdiv_long[-1] > 0:
        annot_str = annot_str + 'Также присутствует среднесрочное бычье расхождение между ценой и индикатором %Williams. Что может говорить о скором появлении восходящего движения цены. '
    if downsampled_df.w1_WILLRdiv_long[-1] < 0:
        annot_str = annot_str + 'Также присутствует среднесрочное медвежье расхождение между ценой и индикатором %Williams. Что может говорить о скором появлении нисходящего движения цены. '
    content = content + annot_str

    # Свечные паттерны
    annot_str = ''
    if downsampled_df.w1_Hummer[-3:-1].max() > 0:
        annot_str = annot_str + 'Один из трех последних баров представляет собой свечной паттерн Молот, что может являтся сигналом разворота.'
    if downsampled_df.w1_ShootingStar[-3:-1].min() < 0:
        annot_str = annot_str + 'Один из трех последних баров представляет собой свечной паттерн Падающая звезда, что может являтся сигналом разворота.'
    if downsampled_df.w1_DivBar[-3:-1].max() > 0:
        annot_str = annot_str + 'Один из трех последних баров представляет собой дивергентный бар на покупку, что может являтся сигналом разворота.'
    if downsampled_df.w1_DivBar[-3:-1].min() < 0:
        annot_str = annot_str + 'Один из трех последних баров представляет собой дивергентный бар на продажу, что может являтся сигналом разворота.'
    content = content + annot_str + '  \n'

    annot_str = ''
    if downsampled_df.w1_UpperTimeFrameCondition[-1] == 2:
        annot_str = annot_str + '**Краткосрочный сильный тренд вверх. Общие рекомендации, покупать или оставаться вне рынка. Предпочтительные стратегии: три экрана.**'
    elif downsampled_df.w1_UpperTimeFrameCondition[-1] == -2:
        annot_str = annot_str + '**Краткосрочный сильный тренд вниз. Общие рекомендации, продавать или оставаться вне рынка. Предпочитаемые стратегии: три экрана.**'
    elif downsampled_df.w1_UpperTimeFrameCondition[-1] == 1:
        annot_str = annot_str + '**Краткосрочный тренд вверх. Общие рекомендации, покупать, торговать на разворот при сильных сигналах или оставаться вне рынка. Предпочтительные стратегии: три экрана, система канала (с осторожностью), дивергентный бар (с осторожностью), прорыв волатильности.**'
    elif downsampled_df.w1_UpperTimeFrameCondition[-1] == -1:
        annot_str = annot_str + '**Краткосрочный тренд вниз. Общие рекомендации, продавать, торговать на разворот при сильных сигналах или оставаться вне рынка. Предпочтительные стратегии: три экрана, система канала (с осторожностью), дивергентный бар (с осторожностью), прорыв волатильности.**'
    else:
        annot_str = annot_str + '**Горизонтальное или разнонаправленное направление движдения рынка. Общие рекомендации, торговать внутрь канала и ждать прорыва волатильности. Предпочтительные стратегии: система канала, дивергентный бар, прорыв волатильности.**'

    content = content + annot_str + '  \n'
    content = content + '![Alt text](media_url/dailyAnalysis/' + img_name + ')' + '  \n'

    return content


def dailyanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    research_window = 75  # Число баров для анализа
    df_short = df[-research_window:]

    df_short_reg_8, df_short_ugol_8 = preprocessing.RegAngleLine(df_short.close, 8)
    df_short_reg_35, df_short_ugol_35 = preprocessing.RegAngleLine(df_short.close, 35)

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.2, 0.2, 0.1])

    fig.add_trace(go.Candlestick(x=df_short.index,
                                 open=df_short['open'],
                                 high=df_short['high'],
                                 low=df_short['low'],
                                 close=df_short['close'],
                                 name=ticker),
                  row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_short.index,
        y=df_short['MA_fast'],
        name="Быстрое MA",
        line_color='red',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_short.index,
        y=df_short['MA_slow'],
        name="Медленное MA",
        line_color='blue',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_short.index,
        y=df_short['upBB'],
        name="Линии Боллинджера (верх)",
        line_color='blue',
        opacity=0.5),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_short.index,
        y=df_short['lowBB'],
        name="Линии Боллинджера (низ)",
        line_color='blue',
        opacity=0.5),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_short.index,
        y=df_short['CCI'],
        name="CCI",
        line_color='blue',
        opacity=1),
        row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df_short.index,
        y=df_short['WILLR'],
        name="%Willams",
        line_color='black',
        opacity=1),
        row=3, col=1)

    fig.add_trace(go.Bar(x=df_short.index,
                         y=df_short.MACD,
                         name="MACD"),
                  row=4, col=1)

    # ******************************
    if df_short_reg_8[-1] < df_short_reg_8[-2]:
        reg_col = 'red'
    else:
        reg_col = 'green'
    fig.add_trace(go.Scatter(
        x=df_short.index[-8:],
        y=df_short_reg_8,
        name="Линия регрессии (8): " + str(round(df_short_ugol_8, 0)) + ' град.',
        line_color=reg_col,
        opacity=1),
        row=1, col=1)

    if df_short_reg_35[-1] < df_short_reg_35[-2]:
        reg_col = 'red'
    else:
        reg_col = 'green'
    fig.add_trace(go.Scatter(
        x=df_short.index[-35:],
        y=df_short_reg_35,
        name="Линия регрессии (35): " + str(round(df_short_ugol_35, 0)) + ' град.',
        line_color=reg_col,
        opacity=1),
        row=1, col=1)

    # ********************************
    # отмечаем интересные зоны на графике
    annotations = []
    df_ann = df_short[-20:]
    for index, row in df_ann[df_ann['ShootingStar'] < 0].iterrows():
        annotations.append(
            dict(x=index, y=row['low'], xref='x', yref='y', showarrow=True, xanchor='left', text='ShootingStar'))
    for index, row in df_ann[df_ann['Hummer'] > 0].iterrows():
        annotations.append(
            dict(x=index, y=row['high'], xref='x', yref='y', showarrow=True, xanchor='right', text='Hummer'))
    for index, row in df_ann[df_ann['DivBar'] > 0].iterrows():
        annotations.append(
            dict(x=index, y=row['high'], xref='x', yref='y', showarrow=True, xanchor='right', text='DivBar'))
    fig.update_layout(annotations=annotations)

    # ********************************
    # финальная настройка layout
    fig.update_yaxes(title_text="График цены", row=1, col=1)
    fig.update_yaxes(title_text="CCI", row=2, col=1)
    fig.update_yaxes(title_text="%Williams", row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), holydays])
    fig.update_layout(height=800, width=1000, xaxis_rangeslider_visible=False)

    if is_show_figs:
        fig.show()

    img_name = ticker + "_daily_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Анализ дневного графика  \n'

    # Цена. Линия регрессии
    annot_str = 'Линия регрессии, построенная за последние 8 дней, направлена ' + (
        'вниз' if df_short_reg_8[-1] < df_short_reg_8[-2] else 'вверх') + '. '
    annot_str = annot_str + 'Угол ее наклона составляет ' + str(round(df_short_ugol_8, 1)) + ' градусов. '
    annot_str = annot_str + 'Линия регрессии, построенная за последние 35 дней, направлена ' + (
        'вниз' if df_short_reg_35[-1] < df_short_reg_35[-2] else 'вверх') + '. '
    annot_str = annot_str + 'Угол ее наклона составляет ' + str(round(df_short_ugol_35, 1)) + ' градусов. '
    content = content + annot_str

    # MA
    annot_str = 'Цена находится ' + (
        'выше' if df_short.MA_fast_price_pos[-1] == 1 else 'ниже') + ' быстрой скользящей средней. '
    annot_str = annot_str + 'Быстрое скользящее среднее, в свою очередь, находится ' + (
        'выше' if df_short.MA_fast_slow_pos[-1] == 1 else 'ниже') + ' медленной скользящей средней. '
    annot_str = annot_str + 'Все это говорит о том, что сейчас на рынке наблюдается '
    if df_short.MA_fast_price_pos[-1] == 1 and df_short.MA_fast_slow_pos[-1] == 1:
        annot_str = annot_str + 'сильный восходящий тренд. '
    elif df_short.MA_fast_price_pos[-1] == 0 and df_short.MA_fast_slow_pos[-1] == 0:
        annot_str = annot_str + 'сильный нисходящий тренд. '
    else:
        annot_str = annot_str + 'разнонаправленное горизонтальное движение рынка или наблюдается смена тренда. '
    content = content + annot_str

    # MACD
    annot_str = 'Индикатор MACD находится ' + ('выше' if df_short.MACD[-1] > 0 else 'ниже') + ' нулевой линии. '
    annot_str = annot_str + ', его значения ' + (
        'снижаются. ' if df_short.MACDchg[-1] == 0 else 'повышаются. ')
    if df_short.MACDdiv_short[-1] > 0:
        annot_str = annot_str + 'Также присутствует краткосрочное бычье расхождение между ценой и индикатором MACD. '
    if df_short.MACDdiv_short[-1] < 0:
        annot_str = annot_str + 'Также присутствует краткосрочное медвежье расхождение между ценой и индикатором MACD. '
    if df_short.MACDdiv_long[-1] > 0:
        annot_str = annot_str + 'Также присутствует долгосрочное бычье расхождение между ценой и индикатором MACD. '
    if df_short.MACDdiv_long[-1] < 0:
        annot_str = annot_str + 'Также присутствует долгосрочное медвежье расхождение между ценой и индикатором MACD. '
    content = content + annot_str

    # Осцилляторы
    annot_str = 'Значение индикатора %Williams равно ' + str(round(df_short.WILLR[-1], 0)) + '. '
    if df_short.WILLRoverZones[-1] > 0:
        annot_str = annot_str + 'Он находится в зоне перепроданности. '
    elif df_short.WILLRoverZones[-1] < 0:
        annot_str = annot_str + 'Он находится в зоне перекупленности. '
    else:
        annot_str = annot_str + 'Он не находится на текущий момент в экстремальных зонах. '

    if df_short.WILLRdiv_short[-1] > 0:
        annot_str = annot_str + 'Также присутствует краткосрочное бычье расхождение между ценой и индикатором %Williams. Что может говорить о скором появлении восходящего движения цены. '
    if df_short.WILLRdiv_short[-1] < 0:
        annot_str = annot_str + 'Также присутствует краткосрочное медвежье расхождение между ценой и индикатором %Williams. Что может говорить о скором появлении нисходящего движения цены. '

    if df_short.WILLRdiv_long[-1] > 0:
        annot_str = annot_str + 'Также присутствует среднесрочное бычье расхождение между ценой и индикатором %Williams. Что может говорить о скором появлении восходящего движения цены. '
    if df_short.WILLRdiv_long[-1] < 0:
        annot_str = annot_str + 'Также присутствует среднесрочное медвежье расхождение между ценой и индикатором %Williams. Что может говорить о скором появлении нисходящего движения цены. '
    content = content + annot_str

    annot_str = 'Значение индикатора CCI равно ' + str(round(df_short.CCI[-1], 0)) + '. '
    if df_short.CCIoverZones[-1] > 0:
        annot_str = annot_str + 'Он находится в зоне перепроданности. '
    elif df_short.CCIoverZones[-1] < 0:
        annot_str = annot_str + 'Он находится в зоне перекупленности. '
    else:
        annot_str = annot_str + 'Он не находится на текущий момент в экстремальных зонах. '

    if df_short.CCIdiv_short[-1] > 0:
        annot_str = annot_str + 'Также присутствует краткосрочное бычье расхождение между ценой и индикатором CCI. Что может говорить о скором появлении восходящего движения цены. '
    if df_short.CCIdiv_short[-1] < 0:
        annot_str = annot_str + 'Также присутствует краткосрочное медвежье расхождение между ценой и индикатором CCI. Что может говорить о скором появлении нисходящего движения цены. '

    if df_short.CCIdiv_long[-1] > 0:
        annot_str = annot_str + 'Также присутствует среднесрочное бычье расхождение между ценой и индикатором CCI. Что может говорить о скором появлении восходящего движения цены. '
    if df_short.CCIdiv_long[-1] < 0:
        annot_str = annot_str + 'Также присутствует среднесрочное медвежье расхождение между ценой и индикатором CCI. Что может говорить о скором появлении нисходящего движения цены. '
    content = content + annot_str

    # Свечные паттерны
    annot_str = ''
    if df_short.Hummer[-3:-1].max() > 0:
        annot_str = annot_str + 'Один из трех последних баров представляет собой свечной паттерн Молот, что может являтся сигналом разворота. '
    if df_short.ShootingStar[-3:-1].min() < 0:
        annot_str = annot_str + 'Один из трех последних баров представляет собой свечной паттерн Падающая звезда, что может являтся сигналом разворота. '
    if df_short.DivBar[-3:-1].max() > 0:
        annot_str = annot_str + 'Один из трех последних баров представляет собой дивергентный бар на покупку, что может являтся сигналом разворота. '
    if df_short.DivBar[-3:-1].min() < 0:
        annot_str = annot_str + 'Один из трех последних баров представляет собой дивергентный бар на продажу, что может являтся сигналом разворота. '
    content = content + annot_str + '  \n'

    content = content + '![Alt text](media_url/dailyAnalysis/' + img_name + ')' + '  \n'

    return content


def elderanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    df_fig = df[-35:]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.4])

    fig.add_trace(go.Candlestick(x=df_fig.index,
                                 open=df_fig['open'],
                                 high=df_fig['high'],
                                 low=df_fig['low'],
                                 close=df_fig['close'],
                                 name=ticker),
                  row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['WILLR'],
        name="%Willams",
        line_color='black',
        opacity=1),
        row=2, col=1)

    # ********************************
    # финальная настройка layout
    fig.update_yaxes(title_text="График цены", row=1, col=1)
    fig.update_yaxes(title_text="%Williams", row=2, col=1)
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), holydays])
    fig.update_layout(height=800, width=1000, xaxis_rangeslider_visible=False)

    if is_show_figs:
        fig.show()

    img_name = ticker + "_elder_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Стратегия: Три экрана Элдера  \n'

    annot_str = ''
    if df.sig_elder[-1] < 0:
        annot_str = annot_str + 'Значения инидикатора MACD снижаются. Рассматриваем только сделки на продажу, либо вне рынка. '
        annot_str = annot_str + '**Значения инидикатора %Williams в зоне перекупленности. Выставляем стоп приказ на продажу по цене: ' + str(
            df['low'][-2]) + ' со стопом ' + str(df['high'][-2:].max()) + '**'
    elif df.sig_elder[-1] > 0:
        annot_str = annot_str + 'Значения инидикатора MACD повышаются. Рассматриваем только сделки на покупку, либо вне рынка. '
        annot_str = annot_str + '**Значения инидикатора %Williams в зоне перепроданности. Выставляем стоп приказ на покупку по цене: ' + str(
            df['high'][-2]) + ' со стопом ' + str(df['low'][-2:].min()) + '**'
    else:
        annot_str = annot_str + 'В рамках данной стратегии остаемся вне рынка, так как на большем таймфрейме наблюдается флет.'

    content = content + annot_str + '  \n'
    content = content + '![Alt text](media_url/dailyAnalysis/' + img_name + ')' + '  \n'
    current_sig_elder = df.sig_elder[-1]

    return content, current_sig_elder


def channelanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    df_fig = df[-35:]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.4])

    fig.add_trace(go.Candlestick(x=df_fig.index,
                                 open=df_fig['open'],
                                 high=df_fig['high'],
                                 low=df_fig['low'],
                                 close=df_fig['close'],
                                 name=ticker),
                  row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['upBB'],
        name="Линии Боллинджера (верх)",
        line_color='blue',
        opacity=0.5),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['lowBB'],
        name="Линии Боллинджера (низ)",
        line_color='blue',
        opacity=0.5),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['CCI'],
        name="CCI",
        line_color='blue',
        opacity=1),
        row=2, col=1)

    # ********************************
    # отмечаем интересные зоны на графике
    annotations = []
    df_ann = df[-20:]
    for index, row in df_fig[df_fig['DivBar'] != 0].iterrows():
        annotations.append(
            dict(x=index, y=row['high'], xref='x', yref='y', showarrow=True, xanchor='left', text='DivBar'))
    fig.update_layout(annotations=annotations[-5:])

    # ********************************
    # финальная настройка layout
    fig.update_yaxes(title_text="График цены", row=1, col=1)
    fig.update_yaxes(title_text="CCI", row=2, col=1)
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), holydays])
    fig.update_layout(height=800, width=1000, xaxis_rangeslider_visible=False)

    if is_show_figs:
        fig.show()

    img_name = ticker + "_channel_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Стратегия: Система канала  \n'

    annot_str = ''
    if df['sig_channel'][-1] < 0:
        annot_str = annot_str + '**Имеет место дивергенция CCI и касание бара верхней границы канала. Выставляем стоп приказ на продажу по цене: ' + str(
            df['low'][-2]) + ' со стопом ' + str(df['high'][-2:].max()) + '.**'
    elif df['sig_channel'][-1] > 0:
        annot_str = annot_str + '**Имеет место дивергенция CCI и касание бара нижней границы канала. Выставляем стоп приказ на покупку по цене: ' + str(
            df['high'][-2]) + ' со стопом ' + str(df['low'][-2:].min()) + '.**'
    else:
        annot_str = annot_str + 'Сигналов в рамках данной стратегии на текущий момент нет.'

    content = content + annot_str + '  \n'
    content = content + '![Alt text](media_url/dailyAnalysis/' + img_name + ')' + '  \n'
    current_sig_channel = df.sig_channel[-1]

    return content, current_sig_channel


def divbaranalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    df_fig = df[-35:]
    df_short_reg_8, df_short_ugol_8 = preprocessing.RegAngleLine(df_fig.close, 8)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.4])

    fig.add_trace(go.Candlestick(x=df_fig.index,
                                 open=df_fig['open'],
                                 high=df_fig['high'],
                                 low=df_fig['low'],
                                 close=df_fig['close'],
                                 name=ticker),
                  row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['MA_fast'],
        name="Быстрое MA",
        line_color='red',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['WILLR'],
        name="%Willams",
        line_color='black',
        opacity=1),
        row=2, col=1)

    # ******************************
    if df_short_reg_8[-1] < df_short_reg_8[-2]:
        reg_col = 'red'
    else:
        reg_col = 'green'
    fig.add_trace(go.Scatter(
        x=df_fig.index[-8:],
        y=df_fig,
        name="Линия регрессии: " + str(round(df_short_ugol_8, 0)) + ' град.',
        line_color=reg_col,
        opacity=1),
        row=1, col=1)

    # ********************************
    # отмечаем интересные зоны на графике
    annotations = []
    for index, row in df_fig[df_fig['DivBar'] != 0].iterrows():
        annotations.append(
            dict(x=index, y=row['high'], xref='x', yref='y', showarrow=True, xanchor='left', text='DivBar'))
    fig.update_layout(annotations=annotations[-5:])

    # ********************************
    # финальная настройка layout
    fig.update_yaxes(title_text="График цены", row=1, col=1)
    fig.update_yaxes(title_text="%Williams", row=2, col=1)
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), holydays])
    fig.update_layout(height=800, width=1000, xaxis_rangeslider_visible=False)

    if is_show_figs:
        fig.show()

    img_name = ticker + "_divbar_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    # Расчет линии регрессии за последние 8 баров
    df_short_reg_8, df_short_ugol_8 = preprocessing.RegAngleLine(df_fig.close, 8)

    # Расчет линии регрессии за последние 8 баров
    df_shortma_reg_8, df_shortma_ugol_8 = preprocessing.RegAngleLine(df_fig.MA_slow, 8)

    content = '###Стратегия: Дивергентный бар  \n'

    annot_str = ''
    annot_str = annot_str + 'Угол наклона линии регрессии цены составляет ' + str(round(df_short_ugol_8)) + 'градусов, '
    annot_str = annot_str + 'угол наклона линии регрессии скользящей средней составляет ' + str(
        round(df_shortma_ugol_8)) + 'градусов. '
    if df.sig_DivBar[-1] < 0:
        annot_str = annot_str + 'Есть дивергенция между скользящей средней и ценой. '
        annot_str = annot_str + '**Присутствует дивергентный бар на продажу, выставляем стоп ордер на продажу по цене ' + str(
            df.low[-1]) + ' и стоп лоссом на ' + str(df.high[-1]) + '**'

    if df.sig_DivBar[-1] > 0:
        annot_str = annot_str + 'Есть дивергенция между скользящей средней и ценой. '
        annot_str = annot_str + '**Присутствует дивергентный бар на покупку, выставляем стоп ордер на покупку по цене ' + str(
            df.high[-1]) + ' и стоп лоссом на ' + str(df.low[-1]) + '**'

    content = content + annot_str + '  \n'
    content = content + '![Alt text](media_url/dailyAnalysis/' + img_name + ')' + '  \n'
    current_sig_DivBar = df.sig_DivBar[-1]

    return content, current_sig_DivBar


def volatilityanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    df_fig = df[-35:]
    df_short_reg_35, df_short_ugol_35 = preprocessing.RegAngleLine(df.close, 35)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.4])

    fig.add_trace(go.Candlestick(x=df_fig.index,
                                 open=df_fig['open'],
                                 high=df_fig['high'],
                                 low=df_fig['low'],
                                 close=df_fig['close'],
                                 name=ticker),
                  row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['MA_fast'],
        name="Быстрое MA",
        line_color='red',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['MA_slow'],
        name="Медленное MA",
        line_color='green',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['upBB'],
        name="Линии Боллинджера (верх)",
        line_color='blue',
        opacity=0.5),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['lowBB'],
        line_color='blue',
        name="Линии Боллинджера (низ)",
        opacity=0.5),
        row=1, col=1)

    fig.add_trace(go.Bar(x=df_fig.index,
                         y=df_fig.MACD,
                         name="MACD"),
                  row=2, col=1)

    if df_short_reg_35[-1] < df_short_reg_35[-2]:
        reg_col = 'red'
    else:
        reg_col = 'green'
    fig.add_trace(go.Scatter(
        x=df_fig.index[-35:],
        y=df_short_reg_35,
        name="Линия регрессии (35): " + str(round(df_short_ugol_35, 0)) + ' град.',
        line_color=reg_col,
        opacity=1),
        row=1, col=1)

    # финальная настройка layout
    fig.update_yaxes(title_text="График цены", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), holydays])
    fig.update_layout(height=800, width=1000, xaxis_rangeslider_visible=False)

    if is_show_figs:
        fig.show()

    img_name = ticker + "_volatility_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Стратегия: Прорыв волатильности  \n'

    annot_str = ''
    annot_str = annot_str + 'Угол наклона линии регрессии цены составляет ' + str(
        round(df_short_ugol_35)) + ' градусов. '
    if df_short_ugol_35 > -12 and df_short_ugol_35 < 12:
        annot_str = annot_str + 'Направление линии регрессии почти горизонтальное.'

    annot_str = annot_str + '(!Потом убрать раздел)Дисперсия составляет: ' + str(
        round(np.var(df.close[-15:]))) + '. '
    if np.var(df.close[-15:]) < (df.close[-1] * 0.1):
        annot_str = annot_str + 'А это меньше 10% текущей стоимости акции за последние 15 баров' + '. '

    if df.sig_breakVolatility[-1]:
        annot_str = annot_str + '**Ожидаем прорыв волатильности. Выставляем ордера на покупку и продажу по ценам ' + str(
            df.high[-15:-1].max()) + ' и ' + str(
            df.low[-15:-1].min()) + ' соответственно. Стопы на противополжных границах канала **'

    if df.sig_NR4ID[-1]:
        annot_str = annot_str + '**Текущий бар является баром NR4/ID. Выставляем ордера на масимуме и минимуме текущего бара, ' + str(
            df.high[-1]) + ' и ' + str(
            df.low[-1]) + ' соответсвенно, со стопами на противоположных экстремумах бара. **'

    content = content + annot_str + '  \n'
    content = content + '![Alt text](media_url/dailyAnalysis/' + img_name + ')' + '  \n'
    current_sig_breakVolatility = df.sig_breakVolatility[-1]
    current_sig_NR4ID = df.sig_NR4ID[-1]

    return content, current_sig_breakVolatility, current_sig_NR4ID


def supportanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    content = '###Сопровождение открытых позиций  \n'
    annot_str = 'В случае если **открыты длинные позиции**, в качестве стоп-лосса могут выступать:'
    content = content + annot_str + '  \n\n'
    annot_str = '* Предыдущий экстремум: ' + str(df.low[-1])
    content = content + annot_str + '  \n\n'
    annot_str = '* Быстрая MA: ' + str(round(df.MA_fast[-1], 2))
    content = content + annot_str + '  \n\n\n'
    annot_str = 'Целевыми значениями могут являтся:'
    content = content + annot_str + '  \n\n'
    annot_str = '* Верхняя граница BB: ' + str(round(df.upBB[-1], 2))
    content = content + annot_str + '  \n\n\n'

    annot_str = 'В случае если **открыты короткие позиции**, в качестве стоп-лосса могут выступать:'
    content = content + annot_str + '  \n\n'
    annot_str = '* Предыдущий экстремум: ' + str(df.high[-1])
    content = content + annot_str + '  \n\n'
    annot_str = '* Быстрая MA: ' + str(round(df.MA_fast[-1], 2))
    content = content + annot_str + '  \n\n\n'
    annot_str = 'Целевыми значениями могут являтся:'
    content = content + annot_str + '  \n\n'
    annot_str = '* Нижняя граница BB: ' + str(round(df.lowBB[-1], 2))
    content = content + annot_str + '  \n\n'

    return content


def createdailyanalysis(ticker, on_date='', is_show_figs=False):

    ftp = ftplib.FTP(config['PANDORATRADINGSOLUTION']['ftpip'], config['PANDORATRADINGSOLUTION']['ftpuserdam'], config['PANDORATRADINGSOLUTION']['ftppassdam'])

    image_folder = config['PANDORATRADINGSOLUTION']['ImagePath']
    doc_uuid = str(uuid.uuid4())
    content = '  \n'
    holydays = dict(values=["2020-02-24", "2020-03-09", "2020-05-01", "2020-05-11", "2020-06-12"])

    df = pd.read_csv(config['PANDORA']['DataPath'] + ticker + '_processeddata.csv')
    df['date_time'] = pd.to_datetime(df.date_time)
    if on_date != '':
        df = df[df.date_time <= on_date]

    df = df.set_index('date_time')

    content = content + weeklyanalysisblock(df, ticker, doc_uuid, image_folder, is_show_figs, ftp)
    content = content + dailyanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp)
    annotation_elder, current_sig_elder = elderanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp)
    content = content + annotation_elder
    annotation_channel, current_sig_channel = channelanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp)
    content = content + annotation_channel
    annotation_divbar, current_sig_DivBar = divbaranalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp)
    content = content + annotation_divbar
    annotation_volatility, current_sig_breakVolatility, current_sig_NR4ID = volatilityanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp)
    content = content + annotation_volatility
    annotation_support = supportanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp)
    content = content + annotation_support

    title = 'Ежедневный анализ: ' + ticker + ' от ' + df.index[-1].strftime("%Y-%m-%d")
    # API post
    postdata = {'post': {'analysis_type_id': 1,
                         'ticker_id': ptsapi.gettickerid(ticker),
                         'date_analysis': df.index[-1].strftime("%Y-%m-%d"),  # s[1],
                         'header': title,
                         'content': content,
                         'slug': doc_uuid,
                         'created': datetime.now().strftime("%Y-%m-%dT%H:%M"), # YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]
                         'sig_elder': int(current_sig_elder),
                         'sig_channel': int(current_sig_channel),
                         'sig_DivBar': int(current_sig_DivBar),
                         'sig_NR4ID': int(current_sig_NR4ID),
                         'sig_breakVolatility': int(current_sig_breakVolatility)
                         }
                }

    result = ptsapi.createpost(postdata)

    return result
