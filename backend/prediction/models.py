import uuid
from django.db import models
from django.contrib.auth.models import User
from quote.models import Ticker, Timeframe

ML_MODELS_ALGORITHMS = [
    ('xgb_classifier', 'xgb_classifier'),
    ('random_forest_regressor', 'random_forest_regressor'),
]


class Horizon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    duration = models.IntegerField(help_text='Duration in seconds')

    def __repr__(self):
        return f'{self.code} (id: {self.pk})'

    def __str__(self):
        return f'{self.code}'


class MLModel(models.Model):
    code = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000, null=True, blank=True)
    timeframe = models.ForeignKey(Timeframe, on_delete=models.CASCADE)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    algorithm = models.CharField(max_length=100, choices=ML_MODELS_ALGORITHMS)
    parameters = models.TextField()
    last_fit = models.DateTimeField(null=True, blank=True)
    fit_results = models.TextField()
    guid = models.CharField(max_length=32, unique=True)

    def get_inital_parameters(self):
        return {
            'features': [],
            'fit': {
                'split_train_percentage': 0.8
            },
            'predict': {
                'target': 'close',
                'shift': 5
            },
            'algorithm': {
                'type': '',
                'parameters': {}
            }
        }

    def __repr__(self):
        return f'{self.code} (id: {self.pk})'

    def __str__(self):
        return f'{self.code}'


class MLModelFitResults(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ml_model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    algorithm = models.CharField(max_length=100, choices=ML_MODELS_ALGORITHMS)
    parameters = models.TextField()
    fit_results = models.TextField()
    score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f'{self.algorithm} (id: {self.id})'

    def __str__(self):
        return f'{self.algorithm}'