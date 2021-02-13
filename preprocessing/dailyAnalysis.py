import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import uuid
from datetime import datetime
from preprocessing import preprocessing, dailyanalysisprediction
from API import ptsapi
import configparser
import ftplib
from PIL import Image, ImageDraw, ImageFont

# Init config file
config = configparser.ConfigParser()
config.read('settings.ini')


def create_img_name(ticker, doc_uuid, img_type):
    if img_type == 'weekly':
        img_suffix = '_weekly_'
    elif img_type == 'daily':
        img_suffix = '_daily_'
    elif img_type == 'elder':
        img_suffix = '_elder_'
    elif img_type == 'channel':
        img_suffix = '_channel_'
    elif img_type == 'divbar':
        img_suffix = '_divbar_'
    elif img_type == 'volatility':
        img_suffix = '_volatility_'
    elif img_type == 'support':
        img_suffix = '_support_'
    else:
        raise ValueError(f'Unknown img_type: {img_type}')

    return ticker + img_suffix + doc_uuid + ".png"


def saveimg(img_name, image_folder, fig, ftp):
    fig.write_image(image_folder + img_name)
    image = Image.open(image_folder + img_name)
    #image = image.resize((750, 600), Image.ANTIALIAS)
    image = image.resize((638, 510), Image.ANTIALIAS)
    drawing = ImageDraw.Draw(image)
    drawing.text((60, 70),
                 'www.pandoratradingsolutions.ru',
                 fill=(160, 160, 160),
                 font=ImageFont.truetype("arial.ttf", 10))
    image.save(image_folder + img_name, 'png')
    if config['PANDORATRADINGSOLUTION']['test_env'] == 'False':
        with open(image_folder + img_name, 'rb') as fobj:
            ftp.storbinary('STOR ' + img_name, fobj, 8192)


def pts_layout(fig, holydays='', is_show_figs=False):
    updated_fig = fig

    if holydays != '':
        updated_fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), holydays])
    updated_fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    updated_fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)

    updated_fig.update_layout(height=800,
                              width=1000,
                              xaxis_rangeslider_visible=False,
                              template='plotly_white',
                              )
    if is_show_figs:
        updated_fig.show()

    return updated_fig


#Murray math
def murray_math_count(df):
    max_price = df.high.max()
    min_price = df.low.min()
    cur_price = df.close.values[-1]

    if max_price < 1:
        octave = 1
    elif max_price < 10:
        octave = 10
    elif max_price < 100:
        octave = 100
    elif max_price < 1000:
        octave = 1000
    elif max_price < 10000:
        octave = 10000
    else:
        octave = 100000

    main_step = octave / 8
    mm_main_lines = []
    for i in range(0, 9):
        mm_main_lines.append(main_step * i)

    i = 0
    while cur_price >= mm_main_lines[i]:
        i += 1

    q_min = mm_main_lines[i - 1]
    q_max = mm_main_lines[i]

    step = (q_max - q_min) / 8
    dict_mm_lines = dict()
    for j in range(0, 9):
        dict_mm_lines[str(j)] = q_min + step * j

    return dict_mm_lines


def line_properties(i):
    properties = {
        'color': '',
        'opacity': '',
    }

    if i == '0' or i == '8':
        properties['color'] = 'blue'
        properties['opacity'] = 1
    elif i == '4':
        properties['color'] = 'blue'
        properties['opacity'] = 1
    elif i == '1' or i == '7':
        properties['color'] = 'yellow'
        properties['opacity'] = 0.5
    elif i == '2' or i == '6':
        properties['color'] = 'red'
        properties['opacity'] = 0.8
    elif i == '3' or i == '5':
        properties['color'] = 'green'
        properties['opacity'] = 0.6
    else:
        raise Exception( f'error: unexpected value if MM line: {i}')

    return properties
#ends Murray math

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
    research_window = 35  # Число баров для анализа
    downsampled_df = downsampled_df[-research_window:]

    # Расчет линии регрессии за последние 8 баров
    downsampled_reg, downsampled_ugol_reg = preprocessing.RegAngleLine(downsampled_df.w1_close, 8)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.2, 0.2])

    fig.add_trace(go.Candlestick(x=downsampled_df.index,
                                 open=downsampled_df['w1_open'],
                                 high=downsampled_df['w1_high'],
                                 low=downsampled_df['w1_low'],
                                 close=downsampled_df['w1_close'],
                                 name=ticker,
                                 increasing={'line': {'width': 1, 'color': 'green'},
                                             'fillcolor': 'green'},
                                 decreasing={'line': {'width': 1, 'color': 'red'},
                                             'fillcolor': 'red'}
                                 ),
                  row=1, col=1)
    # **********************************************************************************************************
    fig.add_trace(go.Scatter(
        x=downsampled_df.index,
        y=downsampled_df['w1_MA_fast'],
        name="Fast MA",
        line_color='red',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=downsampled_df.index,
        y=downsampled_df['w1_MA_slow'],
        name="Slow MA",
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
        name="Regression: " + str(round(downsampled_ugol_reg, 0)) + 'dg',
        mode='lines',
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
    fig = pts_layout(fig, is_show_figs=is_show_figs)

    img_name = ticker + "_weekly_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Анализ недельного графика {: .color-primary}  \n'
    content = content + '<a name="weekly"></a>\n'

    # Цена. Процент изменения цены и линия регрессии
    annot_str = 'Изменение цены за последние полгода составляет ' + str(
        round(downsampled_df.w1_prcntChng_15[-1] * 100, 2)) + '%, '
    annot_str = annot_str + 'а за последний месяц ' + str(
        round(downsampled_df.w1_prcntChng_5[-1] * 100, 2)) + '%. '
    content = content + annot_str

    annot_str = 'Направление движения цены последний месяц соответствует ' + (
        'медвежьему тренду. ' if downsampled_reg[-1] < downsampled_reg[-2] else 'бычьему тренду. ')
    content = content + annot_str

    # MA
    annot_str = 'Цена находится ' + (
        'выше' if downsampled_df.w1_MA_fast_price_pos[-1] == 1 else 'ниже') + ' быстрой скользящей средней. \n'
    annot_str = annot_str + 'Быстрая скользящая средняя, в свою очередь, находится ' + (
        'выше' if downsampled_df.w1_MA_fast_slow_pos[-1] == 1 else 'ниже') + ' медленной скользящей средней. \n'

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
    annot_str = 'Значение индикатора %Williams равно ' + str(round(downsampled_df.w1_WILLR[-1], 0))

    if downsampled_df.w1_WILLRoverZones[-1] > 0:
        annot_str = annot_str + ', он находится в зоне перепроданности. '
    elif downsampled_df.w1_WILLRoverZones[-1] < 0:
        annot_str = annot_str + ', он находится в зоне перекупленности. '
    else:
        annot_str = annot_str + ', он не находится на текущий момент в экстремальных зонах. '

    if downsampled_df.w1_WILLRdiv_short[-1] > 0:
        annot_str = annot_str + 'Также присутствует краткосрочное бычье расхождение между ценой и индикатором %Williams. Что может свидетельствовать о скором появлении восходящего движения цены. '
    if downsampled_df.w1_WILLRdiv_short[-1] < 0:
        annot_str = annot_str + 'Также присутствует краткосрочное медвежье расхождение между ценой и индикатором %Williams. Что может свидетельствовать о скором появлении нисходящего движения цены. '

    if downsampled_df.w1_WILLRdiv_long[-1] > 0:
        annot_str = annot_str + 'Также присутствует среднесрочное бычье расхождение между ценой и индикатором %Williams. Что может свидетельствовать о скором появлении восходящего движения цены. '
    if downsampled_df.w1_WILLRdiv_long[-1] < 0:
        annot_str = annot_str + 'Также присутствует среднесрочное медвежье расхождение между ценой и индикатором %Williams. Что может свидетельствовать о скором появлении нисходящего движения цены. '
    content = content + annot_str + '  \n'

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
    content = content + annot_str + '  \n\n'

    annot_str = 'На текущий момент на недельном графике наблюдается '
    if downsampled_df.w1_UpperTimeFrameCondition[-1] == 2:
        annot_str = annot_str + 'краткосрочный **сильный** тренд вверх. Общие рекомендации, покупать или оставаться вне ' \
                                'рынка. Предпочтительные стратегии: экраны Элдера.'
    elif downsampled_df.w1_UpperTimeFrameCondition[-1] == -2:
        annot_str = annot_str + 'краткосрочный **сильный** тренд вниз. Общие рекомендации, продавать или оставаться вне ' \
                                'рынка. Предпочитаемые стратегии: экраны Элдера.'
    elif downsampled_df.w1_UpperTimeFrameCondition[-1] == 1:
        annot_str = annot_str + 'краткосрочный умеренный тренд вверх. Общие рекомендации, покупать, торговать на разворот в короткую сторону при ' \
                                'сильных сигналах или оставаться вне рынка. Предпочтительные стратегии: экраны Элдера, ' \
                                'канальная стратегия , дивергентный бар, прорыв волатильности, NR4/ID.'
    elif downsampled_df.w1_UpperTimeFrameCondition[-1] == -1:
        annot_str = annot_str + 'краткосрочный умеренный тренд вниз. Общие рекомендации, продавать, торговать на разворот в длинную сторону при ' \
                                'сильных сигналах или оставаться вне рынка. Предпочтительные стратегии: экраны Элдера, ' \
                                'канальная стратегия , дивергентный бар, прорыв волатильности, NR4/ID.'
    else:
        annot_str = annot_str + 'горизонтальное или разнонаправленное направление движения рынка. Общие рекомендации: ' \
                                'торговать внутрь канала и ждать прорыва волатильности. Предпочтительные стратегии: ' \
                                'канальная стратегия, дивергентный бар, прорыв волатильности, NR4/ID.'
    content = content + annot_str + '  \n'
    content = content + '![Недельный график](media_url/dailyAnalysis/' + img_name + '){: class="img-fluid" }' + '  \n'

    return content


def dailyanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    research_window = 50  # Число баров для анализа
    df_short = df[-research_window:]

    df_short_reg_8, df_short_ugol_8 = preprocessing.RegAngleLine(df_short.close, 8)
    df_short_reg_35, df_short_ugol_35 = preprocessing.RegAngleLine(df_short.close, 35)

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.2, 0.2, 0.1])

    fig.add_trace(go.Candlestick(x=df_short.index,
                                 open=df_short['open'],
                                 high=df_short['high'],
                                 low=df_short['low'],
                                 close=df_short['close'],
                                 name=ticker,
                                 increasing={'line': {'width': 1, 'color': 'green'},
                                             'fillcolor': 'green'},
                                 decreasing={'line': {'width': 1, 'color': 'red'},
                                             'fillcolor': 'red'}
                                 ),
                  row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_short.index,
        y=df_short['MA_fast'],
        name="Fast MA",
        line_color='red',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_short.index,
        y=df_short['MA_slow'],
        name="Slow MA",
        line_color='blue',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_short.index,
        y=df_short['upBB'],
        name="BB",
        line_color='blue',
        opacity=0.5),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_short.index,
        y=df_short['lowBB'],
        name="BB",
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
        name="Regression: " + str(round(df_short_ugol_8, 0)) + 'dg',
        mode='lines',
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
        name="Regression: " + str(round(df_short_ugol_35, 0)) + 'dg',
        mode='lines',
        line_color=reg_col,
        opacity=1),
        row=1, col=1)

    # ********************************
    # отмечаем интересные зоны на графике
    annotations = []
    df_ann = df_short[-10:]
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
    fig = pts_layout(fig, holydays=holydays, is_show_figs=is_show_figs)

    img_name = ticker + "_daily_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Анализ дневного графика {: .color-primary}  \n'
    content = content + '<a name="daily"></a>\n'

    # Цена. Линия регрессии
    annot_str = 'Линия тренда, построенная за последние 8 дней, направлена ' + (
        'вниз' if df_short_reg_8[-1] < df_short_reg_8[-2] else 'вверх') + '. '
    annot_str = annot_str + 'Угол ее наклона составляет ' + str(round(df_short_ugol_8, 1)) + ' градусов. '
    annot_str = annot_str + 'Линия тренда, построенная за последние 35 дней, направлена ' + (
        'вниз' if df_short_reg_35[-1] < df_short_reg_35[-2] else 'вверх') + '. '
    annot_str = annot_str + 'Угол ее наклона составляет ' + str(round(df_short_ugol_35, 1)) + ' градусов. '
    content = content + annot_str

    # MA
    annot_str = 'Цена находится ' + (
        'выше' if df_short.MA_fast_price_pos[-1] == 1 else 'ниже') + ' быстрой скользящей средней. '
    annot_str = annot_str + 'Быстрое скользящее среднее, в свою очередь, находится ' + (
        'выше' if df_short.MA_fast_slow_pos[-1] == 1 else 'ниже') + ' медленной скользящей средней. '
    annot_str = annot_str + 'Все это указывает на то, что сейчас на рынке наблюдается '
    if df_short.MA_fast_price_pos[-1] == 1 and df_short.MA_fast_slow_pos[-1] == 1:
        annot_str = annot_str + 'восходящий тренд. '
    elif df_short.MA_fast_price_pos[-1] == 0 and df_short.MA_fast_slow_pos[-1] == 0:
        annot_str = annot_str + 'нисходящий тренд. '
    else:
        annot_str = annot_str + 'разнонаправленное горизонтальное движение рынка или наблюдается смена тренда. '
    content = content + annot_str + '  \n'

    # MACD
    annot_str = 'Индикатор MACD находится ' + ('выше' if df_short.MACD[-1] > 0 else 'ниже') + ' нулевой линии'
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
    content = content + annot_str + '  \n'

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

    content = content + '![Дневной график](media_url/dailyAnalysis/' + img_name + '){: class="img-fluid" }' + '  \n'

    return content


def elderanalysisblock(df, market, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    df_fig = df[-35:]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.4])

    fig.add_trace(go.Candlestick(x=df_fig.index,
                                 open=df_fig['open'],
                                 high=df_fig['high'],
                                 low=df_fig['low'],
                                 close=df_fig['close'],
                                 name=ticker,
                                 increasing={'line': {'width': 1, 'color': 'green'},
                                             'fillcolor': 'green'},
                                 decreasing={'line': {'width': 1, 'color': 'red'},
                                             'fillcolor': 'red'}
                                 ),
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
    fig = pts_layout(fig, holydays=holydays, is_show_figs=is_show_figs)

    img_name = ticker + "_elder_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Стратегия: Три экрана Элдера {: .color-primary}  \n'
    content = content + '<a name="elder"></a>\n'

    annot_str = ''
    if df.sig_elder[-1] < 0:
        annot_str = annot_str + 'Значения инидикатора MACD снижаются. Рассматриваем только сделки на продажу, либо вне рынка. '
        annot_str = annot_str + 'Значения инидикатора %Williams в зоне перекупленности. Выставляем стоп приказ на продажу по цене: ' + str(
            df['low'][-2]) + ' со стопом ' + str(df['high'][-2:].max())
    elif df.sig_elder[-1] > 0:
        annot_str = annot_str + 'Значения инидикатора MACD повышаются. Рассматриваем только сделки на покупку, либо вне рынка. '
        annot_str = annot_str + 'Значения инидикатора %Williams в зоне перепроданности. Выставляем стоп приказ на покупку по цене: ' + str(
            df['high'][-2]) + ' со стопом ' + str(df['low'][-2:].min())
    else:
        annot_str = annot_str + 'В рамках данной стратегии остаемся вне рынка, так как отсутствуют сигналы.'

    content = content + annot_str + '  \n'
    content = content + '![График стратегии экраны Элдера](media_url/dailyAnalysis/' + img_name + '){: class="img-fluid" }' + '  \n'
    current_sig_elder = df.sig_elder[-1]
    _, _, current_sig_elder_proba = dailyanalysisprediction.predict(market, ticker, 'sig_elder', df.index[-1].strftime("%Y-%m-%d"))

    return content, current_sig_elder, current_sig_elder_proba


def channelanalysisblock(df, market, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    df_fig = df[-35:]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.4])

    fig.add_trace(go.Candlestick(x=df_fig.index,
                                 open=df_fig['open'],
                                 high=df_fig['high'],
                                 low=df_fig['low'],
                                 close=df_fig['close'],
                                 name=ticker,
                                 increasing={'line': {'width': 1, 'color': 'green'},
                                             'fillcolor': 'green'},
                                 decreasing={'line': {'width': 1, 'color': 'red'},
                                             'fillcolor': 'red'}
                                 ),
                  row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['upBB'],
        name="BB",
        line_color='blue',
        opacity=0.5),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['lowBB'],
        name="BB",
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
    df_ann = df[-10:]
    for index, row in df_ann[df_ann['DivBar'] != 0].iterrows():
        annotations.append(
            dict(x=index, y=row['high'], xref='x', yref='y', showarrow=True, xanchor='left', text='DivBar'))
    for index, row in df_ann[df_ann['ShootingStar'] < 0].iterrows():
        annotations.append(
            dict(x=index, y=row['low'], xref='x', yref='y', showarrow=True, xanchor='left', text='ShootingStar'))
    for index, row in df_ann[df_ann['Hummer'] > 0].iterrows():
        annotations.append(
            dict(x=index, y=row['high'], xref='x', yref='y', showarrow=True, xanchor='right', text='Hummer'))
    fig.update_layout(annotations=annotations[-5:])

    # ********************************
    # финальная настройка layout
    fig.update_yaxes(title_text="График цены", row=1, col=1)
    fig.update_yaxes(title_text="CCI", row=2, col=1)
    fig = pts_layout(fig, holydays=holydays, is_show_figs=is_show_figs)

    img_name = ticker + "_channel_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Стратегия: Система канала {: .color-primary}  \n'
    content = content + '<a name="channel"></a>\n'

    annot_str = ''
    if df['sig_channel'][-1] < 0:
        annot_str = annot_str + 'Сигналы индикаторов указывают на наличие паттерна на продажу. Имеет место дивергенция ' \
                                'между CCI и ценой и касание последнего бара верхней границы канала Боллинджера. ' \
                                'Выставляем стоп приказ на продажу по цене: ' + str(
                                df['low'][-2]) + ' со стопом ' + str(df['high'][-2:].max()) + '.'
    elif df['sig_channel'][-1] > 0:
        annot_str = annot_str + 'Сигналы индикаторов указывают на наличие паттерна на покупку. Имеет место дивергенция ' \
                                'между CCI и ценой и касание последнего бара нижней границы канала Боллинджера. ' \
                                'Выставляем стоп приказ на покупку по цене: ' + str(
                                df['high'][-2]) + ' со стопом ' + str(df['low'][-2:].min()) + '.'
    else:
        annot_str = annot_str + 'Сигналов в рамках данной стратегии на текущий момент нет.'

    content = content + annot_str + '  \n'
    content = content + '![График канальной стратегии](media_url/dailyAnalysis/' + img_name + '){: class="img-fluid" }' + '  \n'
    current_sig_channel = df.sig_channel[-1]
    _, _, current_sig_channel_proba = dailyanalysisprediction.predict(market, ticker, 'sig_channel', df.index[-1].strftime("%Y-%m-%d"))

    return content, current_sig_channel, current_sig_channel_proba


def divbaranalysisblock(df, market, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    df_fig = df[-35:]
    df_short_reg_8, df_short_ugol_8 = preprocessing.RegAngleLine(df_fig.close, 8)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.4])

    fig.add_trace(go.Candlestick(x=df_fig.index,
                                 open=df_fig['open'],
                                 high=df_fig['high'],
                                 low=df_fig['low'],
                                 close=df_fig['close'],
                                 name=ticker,
                                 increasing={'line': {'width': 1, 'color': 'green'},
                                             'fillcolor': 'green'},
                                 decreasing={'line': {'width': 1, 'color': 'red'},
                                             'fillcolor': 'red'}
                                 ),
                  row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['MA_fast'],
        name="Fast MA",
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
        name="Regression: " + str(round(df_short_ugol_8, 0)) + 'dg',
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
    fig = pts_layout(fig, holydays=holydays, is_show_figs=is_show_figs)

    img_name = ticker + "_divbar_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    # Расчет линии регрессии за последние 8 баров
    df_short_reg_8, df_short_ugol_8 = preprocessing.RegAngleLine(df_fig.close, 8)

    # Расчет линии регрессии за последние 8 баров
    df_shortma_reg_8, df_shortma_ugol_8 = preprocessing.RegAngleLine(df_fig.MA_slow, 8)

    content = '###Стратегия: Дивергентный бар {: .color-primary}  \n'
    content = content + '<a name="divbar"></a>\n'

    annot_str = ''
    annot_str = annot_str + 'Угол наклона линии регрессии цены за последние 8 баров составляет ' + str(round(df_short_ugol_8)) + ' градусов, '
    annot_str = annot_str + 'угол наклона линии регрессии скользящей средней за последние 8 баров составляет ' + str(
        round(df_shortma_ugol_8)) + ' градусов. '
    if df.sig_DivBar[-1] < 0:
        annot_str = annot_str + 'Есть дивергенция между скользящей средней и ценой. '
        annot_str = annot_str + 'Присутствует дивергентный бар на продажу, выставляем стоп ордер на продажу по цене ' + str(
            df.low[-1]) + ' и стоп лоссом на ' + str(df.high[-1]) + '.'

    if df.sig_DivBar[-1] > 0:
        annot_str = annot_str + 'Есть дивергенция между скользящей средней и ценой. '
        annot_str = annot_str + 'Присутствует дивергентный бар на покупку, выставляем стоп ордер на покупку по цене ' + str(
            df.high[-1]) + ' и стоп лоссом на ' + str(df.low[-1]) + '.'

    content = content + annot_str + '  \n'
    content = content + '![График стратегии дивергентный бар](media_url/dailyAnalysis/' + img_name + '){: class="img-fluid" }' + '  \n'
    current_sig_DivBar = df.sig_DivBar[-1]
    _, _, current_sig_DivBar_proba = dailyanalysisprediction.predict(market, ticker, 'sig_DivBar',
                                                                df.index[-1].strftime("%Y-%m-%d"))

    return content, current_sig_DivBar, current_sig_DivBar_proba


def volatilityanalysisblock(df, market, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    df_fig = df[-35:]
    df_short_reg_35, df_short_ugol_35 = preprocessing.RegAngleLine(df.close, 35)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.4])

    fig.add_trace(go.Candlestick(x=df_fig.index,
                                 open=df_fig['open'],
                                 high=df_fig['high'],
                                 low=df_fig['low'],
                                 close=df_fig['close'],
                                 name=ticker,
                                 increasing={'line': {'width': 1, 'color': 'green'},
                                             'fillcolor': 'green'},
                                 decreasing={'line': {'width': 1, 'color': 'red'},
                                             'fillcolor': 'red'}
                                 ),
                  row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['MA_fast'],
        name="Fast MA",
        line_color='red',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['MA_slow'],
        name="Slow MA",
        line_color='green',
        opacity=1),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['upBB'],
        name="BB",
        line_color='blue',
        opacity=0.5),
        row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_fig.index,
        y=df_fig['lowBB'],
        line_color='blue',
        name="BB",
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
        name="Regression: " + str(round(df_short_ugol_35, 0)) + 'dg',
        mode='lines',
        line_color=reg_col,
        opacity=1),
        row=1, col=1)

    # финальная настройка layout
    fig.update_yaxes(title_text="График цены", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig = pts_layout(fig, holydays=holydays, is_show_figs=is_show_figs)

    img_name = ticker + "_volatility_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Стратегия: Прорыв волатильности {: .color-primary}  \n'
    content = content + '<a name="volatility"></a>\n'

    annot_str = ''

    if df.sig_breakVolatility[-1]:
        annot_str = annot_str + 'Ожидаем прорыв волатильности. Выставляем ордера на покупку и продажу по ценам ' + str(
            df.high[-15:-1].max()) + ' и ' + str(
            df.low[-15:-1].min()) + ' соответственно. Стопы на противополжных границах канала. '

    if df.sig_NR4ID[-1]:
        annot_str = annot_str + 'Текущий бар является баром NR4/ID. Выставляем ордера на масимуме и минимуме текущего бара, ' + str(
            df.high[-1]) + ' и ' + str(
            df.low[-1]) + ' соответсвенно, со стопами на противоположных экстремумах бара. '

    annot_str = annot_str + 'Угол наклона линии регрессии цены за последние 35 баров составляет ' + str(
        round(df_short_ugol_35)) + ' градусов. '
    if df_short_ugol_35 > -12 and df_short_ugol_35 < 12:
        annot_str = annot_str + 'Направление линии регрессии почти горизонтальное.'

    annot_str = annot_str + ' Дисперсия цены составляет ' + str(
        round(np.var(df.close[-15:]), 2))
    if np.var(df.close[-15:]) < (df.close[-1] * 0.1):
        annot_str = annot_str + ', а это меньше 10% текущей стоимости инструмента за последние 15 баров'
    annot_str = annot_str + '. '

    content = content + annot_str + '  \n'
    content = content + '![График стратегии прорыв волатильности](media_url/dailyAnalysis/' + img_name + '){: class="img-fluid" }' + '  \n'
    current_sig_breakVolatility = df.sig_breakVolatility[-1]
    _, _, current_sig_breakVolatility_proba = dailyanalysisprediction.predict(market, ticker, 'sig_breakVolatility',
                                                              df.index[-1].strftime("%Y-%m-%d"))
    current_sig_NR4ID = df.sig_NR4ID[-1]
    _, _, current_sig_NR4ID_proba = dailyanalysisprediction.predict(market, ticker, 'sig_NR4ID',
                                                               df.index[-1].strftime("%Y-%m-%d"))

    return content, current_sig_breakVolatility, current_sig_breakVolatility_proba, current_sig_NR4ID, current_sig_NR4ID_proba


def supportanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp):
    df_fig = df[-100:]

    dict_mm_lines = murray_math_count(df_fig)

    max_price = df_fig.high.max()
    min_price = df_fig.low.min()
    max_line = 8
    for k in dict_mm_lines:
        if max_price < dict_mm_lines[k]:
            max_line = int(k)
            break
    min_line = 0
    for k in dict_mm_lines:
        if min_price < dict_mm_lines[k]:
            min_line = int(k) - 1
            break

    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02)
    fig.add_trace(go.Candlestick(x=df_fig.index,
                                 open=df_fig.open,
                                 high=df_fig.high,
                                 low=df_fig.low,
                                 close=df_fig.close,
                                 name=ticker,
                                 increasing={'line': {'width': 1, 'color': 'green'},
                                             'fillcolor': 'green'},
                                 decreasing={'line': {'width': 1, 'color': 'red'},
                                             'fillcolor': 'red'}
                                 ),
                  row=1,
                  col=1)

    # финальная настройка layout
    fig.update_yaxes(title_text="График цены", row=1, col=1)
    fig = pts_layout(fig, holydays=holydays, is_show_figs=is_show_figs)

    for a in dict_mm_lines:
        if int(a) >= min_line and int(a) <= max_line:
            fig.add_trace(go.Scatter(x=df_fig.index[-50:],
                                     y=np.full((50), dict_mm_lines[a]),
                                     mode='lines',
                                     name=f'MM {a}/8',
                                     line_color=line_properties(a)['color'],
                                     opacity=line_properties(a)['opacity']),
                          row=1,
                          col=1)

            fig.add_annotation(x=str(df_fig.index.values[-55]),
                               y=dict_mm_lines[a],
                               text=f'{a}/8 - ' + str(round(dict_mm_lines[a], 2)),
                               showarrow=False,
                               xshift=0)

    img_name = ticker + "_support_" + doc_uuid + ".png"
    saveimg(img_name, image_folder, fig, ftp)

    content = '###Сопровождение открытых позиций {: .color-primary}  \n'
    content = content + '<a name="opentrades"></a>\n'

    annot_str = 'Значения уровней Мюррея для текущего квадранта: '
    content = content + annot_str + '  \n\n'

    r_keys = list(dict_mm_lines.keys())
    r_keys.reverse()
    for l in r_keys:
        annot_str = f'* Линия {l}/8 - {dict_mm_lines[l]}'
        content = content + annot_str + '  \n\n'

    content = content + '![График текущих линий поддержки и сопротивления](media_url/dailyAnalysis/' + img_name + '){: class="img-fluid" }' + '  \n\n\n'

    annot_str = 'В случае если открыты длинные позиции, в качестве стоп-лосса могут выступать:'
    content = content + annot_str + '  \n\n'
    annot_str = '* Предыдущий экстремум: ' + str(df.low[-1])
    content = content + annot_str + '  \n\n'
    annot_str = '* Быстрая MA: ' + str(round(df.MA_fast[-1], 2))
    content = content + annot_str + '  \n\n\n'
    annot_str = 'Целевыми значениями могут являтся:'
    content = content + annot_str + '  \n\n'
    annot_str = '* Верхняя граница BB: ' + str(round(df.upBB[-1], 2))
    content = content + annot_str + '  \n\n\n'

    annot_str = 'В случае если открыты короткие позиции, в качестве стоп-лосса могут выступать:'
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


def createdailyanalysis(market, ticker, on_date='', is_show_figs=False):

    ftp = ftplib.FTP(config['PANDORATRADINGSOLUTION']['ftpip'], config['PANDORATRADINGSOLUTION']['ftpuserdam'], config['PANDORATRADINGSOLUTION']['ftppassdam'])

    image_folder = config['PANDORATRADINGSOLUTION']['ImagePath']
    doc_uuid = str(uuid.uuid4())
    content = '  \n'
    # TODO: Заменить хардкод на таблицу csv из папки data
    holydays = dict(values=["2020-02-24", "2020-03-09", "2020-05-01", "2020-05-11", "2020-06-12", "2020-06-24", "2020-07-01", '2020-11-04'])

    df = pd.read_csv(config['PANDORA']['DataPath'] + market + '/' + ticker + '_processeddata.csv')
    df['date_time'] = pd.to_datetime(df.date_time)
    if on_date != '':
        df = df[df.date_time <= on_date]

    df = df.set_index('date_time')

    weekly_content = weeklyanalysisblock(df, ticker, doc_uuid, image_folder, is_show_figs, ftp)
    daily_content = dailyanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp)
    annotation_elder, current_sig_elder, current_sig_elder_proba = elderanalysisblock(df, market, ticker, doc_uuid,
                                                                                      image_folder, holydays,
                                                                                      is_show_figs, ftp)
    annotation_channel, current_sig_channel, current_sig_channel_proba = channelanalysisblock(df, market, ticker, doc_uuid,
                                                                                              image_folder, holydays,
                                                                                              is_show_figs, ftp)
    annotation_divbar, current_sig_DivBar, current_sig_DivBar_proba = divbaranalysisblock(df, market, ticker, doc_uuid,
                                                                                          image_folder, holydays,
                                                                                          is_show_figs, ftp)
    annotation_volatility, current_sig_breakVolatility, current_sig_breakVolatility_proba, current_sig_NR4ID, current_sig_NR4ID_proba = volatilityanalysisblock(
        df, market, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp)
    annotation_support = supportanalysisblock(df, ticker, doc_uuid, image_folder, holydays, is_show_figs, ftp)

    def create_table_of_contents(content, **kwargs):
        content = content + '###Содержание: {: .color-primary} \n\n'
        content = content + '1. [Анализ недельного графика](#weekly) \n'
        content = content + '1. [Анализ дневного графика](#daily) \n'
        if kwargs['current_sig_elder'] != 0:
            content = content + '1. [Стратегия: Три экрана Элдера](#elder) \n'
        if kwargs['current_sig_channel'] != 0:
            content = content + '1. [Стратегия: Система канала](#channel) \n'
        if kwargs['current_sig_DivBar'] != 0:
            content = content + '1. [Стратегия: Дивергентный бар](#divbar) \n'
        if kwargs['current_sig_breakVolatility'] != 0 or current_sig_NR4ID != 0:
            content = content + '1. [Стратегия: Прорыв волатильности](#volatility) \n'
        content = content + '1. [Сопровождение открытых позиций](#opentrades) \n'
        content = content + '  \n'
        return content

    content = content + create_table_of_contents(content,
                                                 current_sig_elder=current_sig_elder,
                                                 current_sig_channel=current_sig_channel,
                                                 current_sig_DivBar=current_sig_DivBar,
                                                 current_sig_breakVolatility=current_sig_breakVolatility)

    content = content + weekly_content
    content = content + daily_content
    if current_sig_elder != 0:
        post_descr = '\n'.join(annotation_elder.split('\n')[2:-2])
        post_img = create_img_name(ticker, doc_uuid, 'elder')
        content = content + annotation_elder
    elif current_sig_channel != 0:
        post_descr = '\n'.join(annotation_channel.split('\n')[2:-2])
        post_img = create_img_name(ticker, doc_uuid, 'channel')
        content = content + annotation_channel
    elif current_sig_DivBar != 0:
        post_descr = '\n'.join(annotation_divbar.split('\n')[2:-2])
        post_img = create_img_name(ticker, doc_uuid, 'divbar')
        content = content + annotation_divbar
    elif current_sig_breakVolatility != 0 or current_sig_NR4ID != 0:
        post_descr = '\n'.join(annotation_volatility.split('\n')[2:-2])
        post_img = create_img_name(ticker, doc_uuid, 'volatility')
        content = content + annotation_volatility
    else:
        post_descr = '\n'.join(daily_content.split('\n')[2:-2])
        post_img = create_img_name(ticker, doc_uuid, 'daily')
    content = content + annotation_support

    title = 'Ежедневный анализ: ' + ticker + ' от ' + df.index[-1].strftime("%Y-%m-%d")

    # API post
    postdata = {'post': {'analysis_type_id': 1,
                         'ticker_id': ptsapi.get_ticker_id(ticker),
                         'date_analysis': df.index[-1].strftime("%Y-%m-%d"),
                         'post_img': post_img,
                         'post_description': post_descr,
                         'header': title,
                         'content': content,
                         'slug': doc_uuid,
                         'slug_url': 'ezhednevnyj-analiz-{0}-ot-{1}-{2}-{3}'.format(ticker.lower(),
                                                                                     df.index[-1].year,
                                                                                     df.index[-1].month,
                                                                                     df.index[-1].day),
                         'created': datetime.now().strftime("%Y-%m-%dT%H:%M"),
                         'sig_elder': int(current_sig_elder),
                         'sig_channel': int(current_sig_channel),
                         'sig_DivBar': int(current_sig_DivBar),
                         'sig_NR4ID': int(current_sig_NR4ID),
                         'sig_breakVolatility': int(current_sig_breakVolatility_proba),
                         'sig_elder_proba': float(current_sig_elder_proba),
                         'sig_channel_proba': float(current_sig_channel_proba),
                         'sig_DivBar_proba': float(current_sig_DivBar_proba),
                         'sig_NR4ID_proba': float(current_sig_NR4ID_proba),
                         'sig_breakVolatility_proba': float(current_sig_breakVolatility_proba)
                         }
                }

    result = ptsapi.createpost(postdata)

    return result