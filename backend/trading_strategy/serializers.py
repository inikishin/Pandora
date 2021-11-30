from .models import TradingStrategy, Signal
from rest_framework import serializers


class TradingStrategySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TradingStrategy
        fields = ['code', 'fullname', 'description']


class SignalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Signal
        fields = ['ticker', 'timeframe', 'datetime', 'trading_strategy', 'value']
