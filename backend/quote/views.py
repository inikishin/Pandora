from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Market, Timeframe, Ticker, Quote
from .serializers import MarketSerializer, TimeframeSerializer, TickerSerializer, QuoteSerializer


class MarketViewSet(viewsets.ModelViewSet):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer


class TimeframeViewSet(viewsets.ModelViewSet):
    queryset = Timeframe.objects.all()
    serializer_class = TimeframeSerializer


class TickerViewSet(viewsets.ModelViewSet):
    queryset = Ticker.objects.all()
    serializer_class = TickerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['market']
    search_fields = ['code', 'fullname']


class QuoteViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ticker', 'timeframe', 'datetime']
