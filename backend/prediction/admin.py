from django.contrib import admin
from .models import Horizon, MLModel, MLModelFitResults
from .tasks import fit_prediction_model


@admin.action(description='Fit prediction models')
def fit_prediction_model_action(modeladmin, request, queryset):
    for t in queryset:
        fit_prediction_model.delay('gazp', 'd1', '2w', t.code)


class MLModelAdmin(admin.ModelAdmin):
    list_display = ['code', 'fullname', 'algorithm', 'last_fit']
    ordering = ['code']
    list_filter = ['algorithm']
    actions = [fit_prediction_model_action]


admin.site.register(Horizon)
admin.site.register(MLModelFitResults)
admin.site.register(MLModel, MLModelAdmin)