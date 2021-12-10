import os
import pickle
import uuid
from datetime import timedelta
import pandas as pd
import numpy as np
from .algorithms import xgb_classifier, random_forest_regressor


def get_available_algorithms_list():
    algorithms_list = [{
        'code': 'xgb_classifier',
        'name': 'XGB Classifier',
        'description': 'XGB Classifier description',
        'params': xgb_classifier.get_parameters_layout()
    }, {
        'code': 'random_forest_regressor',
        'name': 'Random Forest Regressor',
        'description': 'Random Forest Regressor description',
        'params': random_forest_regressor.get_parameters_layout()
    }]

    return algorithms_list


def split_data(data: pd.DataFrame, target: str, target_shift: int, split_train_percentage: float) -> dict:
    df = data.copy()
    df['target'] = df[target].shift(target_shift)
    df.dropna(inplace=True)

    train_features, test_features = np.split(df, [int(split_train_percentage * len(df))])

    train_targets = train_features.target
    test_targets = test_features.target

    train_features.drop(['target'], axis=1, inplace=True)
    test_features.drop(['target'], axis=1, inplace=True)

    return {
        "train_features": train_features,
        "train_targets": train_targets,
        "test_features": test_features,
        "test_targets": test_targets
    }


def fit(user_id: int, ml_model_id: int, data: pd.DataFrame, algorithm: str, algorithm_parameters: dict) -> dict:
    if algorithm == 'xgb_classifier':
        model, fit_results = xgb_classifier.fit(data, algorithm_parameters)
    elif algorithm == 'random_forest_regressor':
        model, fit_results = random_forest_regressor.fit(data, algorithm_parameters)
    else:
        raise ValueError(f'Cannot fit unknown algorithm {algorithm}')

    data_example_columns = ['datetime'] + list(data['train_features'].columns)
    data_example = []
    for index, row in data['train_features'].tail(10).iterrows():
        new_row = [index]
        for column in data['train_features'].columns:
            new_row.append(row[column])
        data_example.append(new_row)

    fit_results['data_example'] = {
        'columns': data_example_columns,
        'values': data_example
    }

    filename = save_model(f'{user_id}/{ml_model_id}/', model)

    return fit_results, filename


def save_model(path: str, model: any) -> str:
    if not os.path.isdir(os.getenv('STORED_ML_MODELS_PATH') + path):
        os.makedirs(os.getenv('STORED_ML_MODELS_PATH') + path, exist_ok=True)

    filename = str(uuid.uuid4()) + '.model'
    with open(os.getenv('STORED_ML_MODELS_PATH') + path + filename, 'wb') as f:
        pickle.dump(model, f)

    return filename


def predict(data: pd.DataFrame, user_id: int, ml_model_id: int, model_filename: str, algorithm: str, shift: int) -> dict:
    model_path = f"{os.getenv('STORED_ML_MODELS_PATH')}{user_id}/{ml_model_id}/{model_filename}"
    if not os.path.exists(model_path):
        raise Exception(f'Saved model does not exist at path {model_path}')
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    prediction_results = {}

    predict_data = data.dropna()
    predict_data = predict_data[-shift:]
    if algorithm == 'xgb_classifier':
        prediction = xgb_classifier.predict(predict_data, model)
    elif algorithm == 'random_forest_regressor':
        prediction = random_forest_regressor.predict(predict_data, model)
    else:
        raise ValueError(f'Cannot fit unknown algorithm {algorithm}')

    prediction_results['predictions'] = []
    data_example_columns = ['datetime'] + list(data.columns)
    data_example = []
    for index, row in data[-100:].iterrows():
        new_row = [pd.to_datetime(index)]
        for column in predict_data.columns:
            new_row.append(row[column])
        data_example.append(new_row)
    prediction_results['data_example'] = {
        'columns': data_example_columns,
        'values': data_example
    }

    i = 0
    for index, row in predict_data.iterrows():
        prediction_results['predictions'].append([
            pd.to_datetime(index) + timedelta(days=shift),
            prediction[i]
        ])
        i += 1

    return prediction_results


# df in D1 timeframe
def resample_data(df: pd.DataFrame, horizon: str) -> pd.DataFrame:
    if horizon in ['1w', '2w', '1m']:  # resample to w1
        conversion = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'vol': 'sum'
        }
        interval = 'W'
    elif horizon in ['3m', '6m', '1y']:  # resample to m1
        conversion = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'vol': 'sum'
        }
        interval = 'M'
    else:
        raise ValueError('Wrong horizon pointed!')

    downsampled_df = df.resample(interval).apply(conversion)
    downsampled_df.fillna(method='bfill', inplace=True)

    return downsampled_df


# split_coef = 0.8 : 80 - тренировочный сет, 20 - тестовый сет
def prepare_data_sets(df: pd.DataFrame, horizon: str, split_coef: float = 0.8):
    if horizon == '1w':
        s = -1
    elif horizon == '2w':
        s = -2
    elif horizon == '1m':
        s = -1
    elif horizon == '3m':
        s = -3
    elif horizon == '6m':
        s = -6
    elif horizon == '1y':
        s = -12
    else:
        raise ValueError('Wrong horizon pointed!')

    df['targetPrice'] = df.close.shift(s)
    df['deltaPrice'] = df.close.shift(s) - df.close
    df['deltaPrice'] = np.where(df['deltaPrice'] > 0, 1, 0)  ## 1 = цена возрастёт, 0 = цена упадёт

    df['ts'] = df.index.values
    df.reset_index(drop=True, inplace=True)
    df.drop(['ticker', 'timeframe'], axis=1, inplace=True)
    df.dropna(inplace=True)

    ## считаем, сколько цен выше, и сколько ниже текущей (насколько сбалансирован дейтасет)
    countPos = len(df[df.deltaPrice == 1])
    countNeg = len(df[df.deltaPrice == 0])
    print(f'Pos: {countPos}   Neg: {countNeg}\n')

    df_train, df_test = np.split(df, [int(split_coef * len(df))])
    print(f'train start: {df_train.ts.iloc[0]}')
    print(f'train end:   {df_train.ts.iloc[-1]}')
    print(f'test start:  {df_test.ts.iloc[0]}')
    print(f'test end:    {df_test.ts.iloc[-1]}')
    df_train.drop(['ts'], axis=1, inplace=True)
    df_test.drop(['ts'], axis=1, inplace=True)

    # подготавливаем сеты
    y_train = df_train.deltaPrice
    y_test = df_test.deltaPrice
    y_train_values = df_train.targetPrice
    y_test_values = df_test.targetPrice

    df_train.drop(['deltaPrice', 'targetPrice'], axis=1, inplace=True)
    df_test.drop(['deltaPrice', 'targetPrice'], axis=1, inplace=True)
    x_train = df_train
    x_test = df_test

    return x_train, x_test, y_train, y_test, y_train_values, y_test_values
