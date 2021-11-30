from django.db import models


class Measure(models.Model):
    code = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=1000)

    def __repr__(self):
        return f'{self.code} (id: {self.pk})'

    def __str__(self):
        return f'{self.code}'


class Country(models.Model):
    code = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=1000)

    def __repr__(self):
        return f'{self.code} (id: {self.pk})'

    def __str__(self):
        return f'{self.code}'


class Indicator(models.Model):
    code = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000, null=True, blank=True)
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE)

    def __repr__(self):
        return f'{self.code} (id: {self.pk})'

    def __str__(self):
        return f'{self.code}'


class IndicatorValue(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE)
    value = models.FloatField(default=0)

    def __repr__(self):
        return f'{self.value} (indicator: {self.indicator})'

    def __str__(self):
        return f'{self.value} (indicator: {self.indicator})'
