from .models import Ticker, Quote, Market, Timeframe
from rest_framework import serializers


class TimeframeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeframe
        fields = '__all__'


class MarketSerializer(serializers.ModelSerializer):
    type_code = serializers.ReadOnlyField(source='type.code')
    stock_exchange_code = serializers.ReadOnlyField(source='stock_exchange.code')
    class Meta:
        model = Market
        fields = '__all__'
        read_only_fields = ['type_code', 'stock_exchange_code']


class TickerSerializer(serializers.ModelSerializer):
    market_code = serializers.ReadOnlyField(source='market.code')
    class Meta:
        model = Ticker
        fields = '__all__'
        read_only_fields = ['market_code']


class QuoteSerializer(serializers.ModelSerializer):
    ticker_code = serializers.ReadOnlyField(source='ticker.code')
    timeframe_code = serializers.ReadOnlyField(source='timeframe.code')
    class Meta:
        model = Quote
        fields = '__all__'
        read_only_fields = ['ticker_code', 'timeframe_code']



