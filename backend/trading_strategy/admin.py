from django.contrib import admin
from .models import TradingStrategy, Signal


class TradingStrategyAdmin(admin.ModelAdmin):
    list_display = ['code', 'fullname']
    ordering = ['code']


admin.site.register(TradingStrategy, TradingStrategyAdmin)
admin.site.register(Signal)
