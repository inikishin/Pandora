import datetime
import os
import pandas as pd
from celery import shared_task
from django_pandas.io import read_frame
from quote.models import Quote, Market, Timeframe, Ticker, BondAdditionalInfo, Currency, StockExchange, FeaturedQuotes
from .models import MLModel
from core.ml_models import common
from core.ml_models.algorithms import xgb_classifier


@shared_task
def fit_prediction_model(ticker_code: str, timeframe: str, horizon_code: str, ml_model_code: str) -> None:
    models_path = os.getenv('STORED_ML_MODELS_PATH')

    ml_model = MLModel.objects.get(code=ml_model_code)

    quotes = read_frame(Quote.objects.filter(ticker__code=ticker_code, timeframe__code=timeframe))
    quotes.drop(columns=['id'], axis=1, inplace=True)
    featured_quotes = read_frame(FeaturedQuotes.objects.filter(ticker__code=ticker_code, timeframe__code=timeframe))
    featured_quotes.drop(columns=['id'], axis=1, inplace=True)

    df = quotes.merge(featured_quotes, how='left', on=['ticker', 'timeframe', 'datetime'], validate='one_to_one')
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime')

    # df = common.resample_data(df, horizon_code)

    if len(df) < 60:
        return 'Not enough data for predict'

    x_train, x_test, y_train, y_test, y_train_values, y_test_values = common.prepare_data_sets(df, horizon_code)

    if ml_model.code == 'common classifier':
        # fitclassifier(ticker, horizon, x_train, x_test, y_train, y_test, models_path, detailedresults=detailedresults)
        xgb_classifier.fit(ticker_code, horizon_code, ml_model.code, x_train, x_test, y_train, y_test, models_path, detailedresults=True)
        ml_model.last_fit = datetime.datetime.now()
        ml_model.save()
    elif ml_model.code == 'common regressor':
        # fitregressor(ticker, horizon, x_train, x_test, y_train_values, y_test_values, models_path, detailedresults=detailedresults)
        ml_model.last_fit = datetime.datetime.now()
        ml_model.save()
    else:
        return f'Uncknown ml model code: {ml_model_code}'

    return 'Model successfully fitted!'


def fit_prediction_model():

    pass