from sklearn.ensemble import RandomForestRegressor


def get_parameters_layout():
    return {
        'n_estimators': {'help_text': 'Количество деревьев',
                         'type': 'integer',
                         'min_value': 10,
                         'max_value': 2000,
                         'step': 100,
                         'default': 500},
        'max_depth': {'help_text': 'максимальная глубина деревьев',
                      'type': 'integer',
                      'min_value': 1,
                      'max_value': 20,
                      'step': 1,
                      'default': 7},
        'min_samples_split': {'help_text': 'The minimum number of samples required to split an internal node',
                         'type': 'integer',
                         'min_value': 1,
                         'max_value': 10,
                         'step': 1,
                         'default': 2},
        'max_features': {'help_text': 'The number of features to consider when looking for the best split',
                              'type': 'integer',
                              'min_value': 1,
                              'max_value': 10,
                              'step': 1,
                              'default': 1},
    }


def fit(data, algorithm_parameters):
    results = {}

    model = RandomForestRegressor(**algorithm_parameters).fit(data['train_features'], data['train_targets'])

    target_predicted_values = model.predict(data['test_features'])

    results['score'] = model.score(data['test_features'], data['test_targets'])
    results['target_predict_chart'] = {
        'type': 'chart',
        'title': 'Соотношение прогноза и исходных данных',
        'description': 'Соотношение прогноза модели машинного обучения и целевой функции',
        'x_title': 'Дата',
        'y_title': 'Цена',
        'y_label_1': 'Исходные данные',
        'y_label_2': 'Прогноз',
        'x_data': list(data['test_features'].index),
        'y_data_1': list(data['test_targets']),
        'y_data_2': list(target_predicted_values),
    }

    results['feature_importances'] = {
        'type': 'chart',
        'title': 'Ранжирование важности фичей',
        'description': 'Ранжирование важности фичей',
        'x_title': 'Фича',
        'y_title': 'Вес',
        'y_label_1': 'Вес',
        'x_data': list(data['train_features'].columns),
        'y_data_1': list(model.feature_importances_),
    }

    return model, results


def predict(data, model):
    return model.predict(data)

