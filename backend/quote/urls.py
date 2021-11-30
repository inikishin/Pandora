from rest_framework import routers
from .views import QuoteViewSet, MarketViewSet, TickerViewSet, TimeframeViewSet

router = routers.DefaultRouter()
router.register(r'quotes', QuoteViewSet)
router.register(r'markets', MarketViewSet)
router.register(r'tickers', TickerViewSet)
router.register(r'timeframes', TimeframeViewSet)