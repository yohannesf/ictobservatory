from django.contrib import admin
from .models import (INDICATORDATA_STATUS, FocusArea, GeneralIndicator, GeneralIndicatorData, Chart, Indicator, ChartConfig, IndicatorData, IndicatorScoreCardConfig,
                     MemberState, Published, ReportingPeriod,
                     Organisation, Currency, AssignedIndicator, ExchangeRateData, IndicatorDataValidationHistory)

# Register your models here.


@admin.action(description='Mark selected data as valid')
def validate_data(modeladmin, request, queryset):
    queryset.update(validation_status=INDICATORDATA_STATUS.validated)


class IndicatorDataAdmin(admin.ModelAdmin):
    # 'focus_area',

    list_display = ('indicator', 'focus_area',  'reporting_year', 'member_state',  'ind_value',  'ind_value_adjusted',
                    'value_NA', 'comments', 'submitted', 'validation_status', 'created_by', 'updated_by')
    list_filter = ('indicator', 'member_state', 'reporting_year',)

    list_per_page = 25

    actions = [validate_data]


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('member_state', 'currency_label', 'currency_short_name')
    list_per_page = 10


class GeneralIndicatorDataAdmin(admin.ModelAdmin):
    # 'focus_area',

    list_display = ('general_indicator', 'indicator_value',
                    'reporting_year',  'updated_by')
    #search_fields = ('indicator', 'member_state', 'reporting_year',)

    list_per_page = 10


class ChartAdmin(admin.ModelAdmin):
    list_display = ('chart_name', 'chart_title', 'description',
                    'chart_type', 'y_axis_title',   'aggregation')

    list_filter = ('chart_title', 'chart_type')


class ChartConfigAdmin(admin.ModelAdmin):
    list_display = ('chart', 'indicator', 'series_name', 'extra_calculation')
    list_filter = ['chart']


class IndicatorScoreCardConfigAdmin(admin.ModelAdmin):
    list_display = ('scorecard_title', 'description',
                    'indicator',   'aggregation')


class ExchangeRateDataAdmin(admin.ModelAdmin):
    list_display = ('member_state', 'currency_label', 'exchange_rate',
                    'exchange_rate_date', 'reporting_year', 'submitted', 'validated')
    list_filter = ('currency__member_state', 'reporting_year')


class IndicatorAssignedAdmin(admin.ModelAdmin):
    list_display = ('indicator', 'assigned_to_organisation')


class IndicatorAdmin(admin.ModelAdmin):

    list_display = ['label', 'indicator_number', 'focus_area',  'data_type',
                    'indicator_type', 'status', 'required', 'indicator_assigned_to']
    list_filter = ['focus_area', 'label', 'indicator_type', ]

    list_per_page = 10


class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ['reporting_start_date', 'reporting_end_date', 'current']


class IndicatorDataValidationHistoryAdmin(admin.ModelAdmin):
    # 'focus_area',

    list_display = ('indicator_data', 'previous_data',  'current', 'comments',  'last_update',  'updated_by',
                    )
    # search_fields = ('indicator_data')

    list_per_page = 10


class MemberStateAdmin(admin.ModelAdmin):

    list_display = ('member_state', 'member_state_short_name',
                    'memberstate_status')


class GeneralIndicatorAdmin(admin.ModelAdmin):

    list_display = ('indicator_label', 'include_in_chart', 'series_name')


class PublishedAdmin(admin.ModelAdmin):
    list_display = ('reporting_year', 'published_status',
                    'last_update', 'updated_by')


admin.site.register(FocusArea)
admin.site.register(ReportingPeriod, ReportingPeriodAdmin)

admin.site.register(MemberState, MemberStateAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(IndicatorData, IndicatorDataAdmin)
admin.site.register(Organisation)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(AssignedIndicator, IndicatorAssignedAdmin)
admin.site.register(ExchangeRateData, ExchangeRateDataAdmin)
# admin.site.register(IndicatorDataValidationHistory,
#                     IndicatorDataValidationHistoryAdmin)
admin.site.register(GeneralIndicator, GeneralIndicatorAdmin)
admin.site.register(GeneralIndicatorData, GeneralIndicatorDataAdmin)
admin.site.register(Published, PublishedAdmin)
admin.site.register(Chart, ChartAdmin)
#admin.site.register(IndicatorScoreCardConfig, IndicatorScoreCardConfigAdmin)
admin.site.register(ChartConfig, ChartConfigAdmin)
