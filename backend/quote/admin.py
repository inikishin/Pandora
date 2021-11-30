from django.contrib import admin
from .models import Calendar, Holiday, MarketType, Market, Timeframe, Ticker, Quote, FeaturedQuotes, Currency, BondAdditionalInfo, StockExchange
from .tasks import load_quotes_from_moex_api, load_quotes_from_csv_file, load_bonds_list_from_moex, preprocessing_quotes


# TODO remove
@admin.action(description='Load quotes from MOEX')
def load_quotes_from_moex_action(modeladmin, request, queryset):
    for t in queryset:
        load_quotes_from_moex_api.delay(t.code)

# TODO remove
@admin.action(description='Load quotes from files')
def load_quotes_from_csv_action(modeladmin, request, queryset):
    for t in queryset:
        load_quotes_from_csv_file.delay(t.code)

# TODO remove
@admin.action(description='Load bonds from MOEX')
def load_bonds_list_action(modeladmin, request, queryset):
    load_bonds_list_from_moex.delay()

# TODO remove
@admin.action(description='Preprocessing quotes')
def preprocessing_quotes_action(modeladmin, request, queryset):
    for t in queryset:
        preprocessing_quotes.delay(t.code)

class TickerAdmin(admin.ModelAdmin):
    list_display = ['code', 'fullname', 'market']
    ordering = ['code']
    list_filter = ['market']
    actions = [load_quotes_from_moex_action, load_quotes_from_csv_action, load_bonds_list_action, preprocessing_quotes_action]


class QuoteAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'timeframe', 'datetime', 'open', 'high', 'low', 'close']
    ordering = ['ticker', 'datetime']
    list_filter = ['ticker']

admin.site.register(Calendar)
admin.site.register(Holiday)
admin.site.register(MarketType)
admin.site.register(StockExchange)
admin.site.register(Market)
admin.site.register(Timeframe)
admin.site.register(Ticker, TickerAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(FeaturedQuotes)
admin.site.register(Currency)
admin.site.register(BondAdditionalInfo)

