import pandas as pd
import pickle
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.metrics import roc_curve, auc, confusion_matrix


def get_parameters_layout():
    return {
        'n_estimators': {'help_text': 'Количество деревьев',
                         'type': 'integer',
                         'min_value': 10,
                         'max_value': 2000,
                         'step': 100,
                         'default': 500},
        'learning_rate': {'help_text': 'скорость обучения',
                          'type': 'float',
                          'min_value': 0.01,
                          'max_value': 1,
                          'step': 0.01,
                          'default': 0.1},
        'max_depth': {'help_text': 'максимальная глубина деревьев',
                      'type': 'integer',
                      'min_value': 1,
                      'max_value': 20,
                      'step': 1,
                      'default': 7},
        'subsample': {'help_text': 'Subsample ratio of the training instance',
                      'type': 'float',
                      'min_value': 0.1,
                      'max_value': 10,
                      'step': 0.1,
                      'default': 1.0},
        'reg_lambda': {'help_text': 'коэффициент L2-регуляризации',
                       'type': 'float',
                       'min_value': 0.1,
                       'max_value': 10,
                       'step': 0.1,
                       'default': 1},
        'objective': {'help_text': 'тип задачи',
                      'type': 'select',
                      'select_list': [{'value': 'reg:squarederror', 'description': 'regression with squared loss'},
                                      {'value': 'binary:logistic',
                                       'description': 'logistic regression for binary classification'}
                                      ],
                      'default': 'binary:logistic'},
        'random_state': {'help_text': 'зерно начального состояния',
                         'type': 'integer',
                         'min_value': 1,
                         'max_value': 1000,
                         'step': 1,
                         'default': 42},
        'silent': {'help_text': 'не выводить процесс обучения на экран',
                   'type': 'bool', 'default': False}
    }


def fit(data, algorithm_parameters):

    model = xgb.XGBClassifier(**algorithm_parameters).fit(data['train_features'], data['train_targets'])

    ## результаты
    model_estimate = pd.concat(data['test_features'], data['test_targets'], axis=1)
    model_estimate['predict_targets'] = model.predict(data['test_features'])
    model_estimate['predict_targets_probability'] = model.predict_proba(data['test_features'])[:, 1]  ## вероятности

    # ошибки первого/второго рода и площадь под ROC-кривой
    FPR, TPR, thresholds = roc_curve(model_estimate.target, model_estimate.predict_targets_probability)
    roc_auc = auc(FPR, TPR)

    ## точность
    acc = len(model_estimate[model_estimate.pred == model_estimate.deltaPrice]) / len(model_estimate)
    print(f"\nAUC = {roc_auc:.3f}\tAccuracy = {acc:.3f}\n")

    ## выводим вероятности (уверенность классификтора)
    plt.hist(model_estimate.pred_proba)
    plt.title('Распределение вероятностей')
    plt.show()

    ## выводим распределение значений
    plt.hist(model_estimate.predict_targets)
    plt.title('Распределение значений классификатора')
    plt.show()

    ## значительность различных фич (feature importance)
    ftmprt = pd.DataFrame()
    ftmprt['features'] = x_train.columns
    ftmprt['importances'] = clf.feature_importances_
    ftmprt = ftmprt.sort_values('importances', ascending=False).reset_index(drop=True)
    print(ftmprt.head(10))

    # ROC-кривая
    plt.title('Receiver Operating Characteristic')
    plt.plot(FPR, TPR, 'b', label=f'AUC = {roc_auc:.2f}')
    plt.legend(loc='lower right')
    plt.plot([0, 1], [0, 1], 'r--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    plt.show()

    ## матрица ошибок
    CM = confusion_matrix(res.deltaPrice, res.pred)
    CM_DF = pd.DataFrame(data=CM, columns=['Pos', 'Neg'])
    print('\n\nConfusion matrix:')
    print(CM_DF)

    filename = f'{ticker_code}_{horizon_code}_{ml_models_code}.model'
    with open(models_path + filename, 'wb') as f:
        pickle.dump(clf, f)


def predict(data, model):
    return model.predict(data)