from rest_framework import routers
from .views import MLModelViewSet, MLModelFitResultsViewSet

router = routers.DefaultRouter()
router.register(r'ml-models', MLModelViewSet)
router.register(r'ml-models-fit-results', MLModelFitResultsViewSet)