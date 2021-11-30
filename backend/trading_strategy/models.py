from django.db import models
from quote.models import Ticker, Timeframe

class TradingStrategy(models.Model):
    code = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000, null=True, blank=True)

    def __repr__(self):
        return f'{self.code} (id: {self.pk})'

    def __str__(self):
        return f'{self.code}'


class Signal(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    timeframe = models.ForeignKey(Timeframe, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    trading_strategy = models.ForeignKey(TradingStrategy, on_delete=models.CASCADE)
    value = models.FloatField(default=0)