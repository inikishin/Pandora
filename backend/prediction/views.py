import json
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_pandas.io import read_frame
from django.contrib.auth.models import User

from .models import MLModel, MLModelFitResults
from quote.models import Quote
from .serializers import MLModelSerializer, MLModelFitResultsSerializer
from core.preprocessing.features import get_available_features_list, extend_dataframe_with_features
from core.ml_models.common import get_available_algorithms_list, split_data, fit, predict


class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer

    @action(detail=False)
    def available_features_list(self, request):
        return Response(get_available_features_list())

    @action(detail=False)
    def available_algorithms_list(self, request):
        return Response(get_available_algorithms_list())

    @action(detail=True, methods=['POST'])
    def fit(self, request, pk=None):
        model = MLModel.objects.get(id=pk)
        user = User.objects.get(username='admin') # TODO Hardcode
        quotes = Quote.objects\
            .filter(ticker=model.ticker, timeframe=model.timeframe)\
            .values('datetime', 'open', 'high', 'low', 'close', 'volume')\
            .order_by('datetime')
        model_parameters = json.loads(model.parameters)
        df_with_features = extend_dataframe_with_features(read_frame(quotes), model_parameters['features'])
        splitted_data: object = split_data(df_with_features,
                                   model_parameters['predict']['target'],
                                   model_parameters['predict']['shift'],
                                   model_parameters['fit']['split_train_percentage'])
        fit_results, filename = fit('1', model.id, splitted_data, model.algorithm, model_parameters['algorithm'])
        model_fit_results = MLModelFitResults(user=user,
                                              ml_model=model,
                                              algorithm=model.algorithm,
                                              parameters=model.parameters,
                                              fit_results=json.dumps(fit_results),
                                              filename=filename)
        model_fit_results.save()
        return Response({'result id': model_fit_results.id})


class MLModelFitResultsViewSet(viewsets.ModelViewSet):
    queryset = MLModelFitResults.objects.all()
    serializer_class = MLModelFitResultsSerializer

    @action(detail=True)
    def predict(self, request, pk=None):
        model_fit = MLModelFitResults.objects.get(id=pk)
        model_parameters = json.loads(model_fit.parameters)
        user = User.objects.get(username='admin')  # TODO Hardcode

        quotes = Quote.objects.filter(ticker=model_fit.ml_model.ticker, timeframe=model_fit.ml_model.timeframe).values(
            'datetime', 'open', 'high', 'low', 'close', 'volume').order_by('datetime')
        df_with_features = extend_dataframe_with_features(read_frame(quotes), model_parameters['features'])
        prediction = predict(df_with_features, user.id, model_fit.ml_model.id, model_fit.filename, model_fit.algorithm, 5) # TODO Remove hardcode for shift

        return Response(prediction)