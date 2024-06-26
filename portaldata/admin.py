from notifications.signals import notify
from django.contrib import admin

from core.models import User
from portaldata.views.indicator_data_validation import send_notification
from .models import (
    INDICATORDATA_STATUS,
    FocusArea,
    GeneralIndicator,
    GeneralIndicatorData,
    Chart,
    Indicator,
    ChartConfig,
    IndicatorData,
    MemberState,
    Published,
    ReportingPeriod,
    ScoreCard,
    ScoreCardConfig,
    Organisation,
    Currency,
    AssignedIndicator,
    ExchangeRateData,
    IndicatorDataValidationHistory,
)

# Register your models here.


@admin.action(description="Mark selected data as valid")
def validate_data(modeladmin, request, queryset):
    queryset.update(validation_status=INDICATORDATA_STATUS.validated)


@admin.action(description="Mark selected data as Unsubmitted")
def unsubmit_data(modeladmin, request, queryset):
    unsubmitted_list = list(queryset)

    member_state_id = []
    if unsubmitted_list:
        for i in unsubmitted_list:
            member_state_id.append(i.member_state.id)

    users = User.objects.filter(
        systemuser__user_member_state_id__in=member_state_id)

    verb = f"Data Unsubmitted"

    message = f"Data is unsubmitted per your request."

    send_notification(sender=request.user, recipients=users,
                      subject=verb, message=message)

    # if users:

    #     notify.send(request.user, recipient=users,
    #                 verb=verb, description=message)

    queryset.update(submitted=False,
                    validation_status=INDICATORDATA_STATUS.draft)


class IndicatorDataAdmin(admin.ModelAdmin):
    # 'focus_area',
    model = IndicatorData

    list_display = (
        "indicator",
        "get_focusarea",
        "reporting_year",
        "member_state",
        "ind_value",
        "ind_value_adjusted",
        "value_NA",
        "comments",
        "submitted",
        "validation_status",
        "created_by",
        "updated_by",
    )
    list_filter = (
        "indicator__focus_area",
        "indicator",
        "member_state",
        "reporting_year",
    )

    list_per_page = 25

    actions = [validate_data, unsubmit_data]

    def get_focusarea(self, obj):
        return obj.indicator.focus_area

    get_focusarea.admin_order_field = "indicator__focus_area"
    get_focusarea.short_description = "Focus Area"


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("member_state", "currency_label", "currency_short_name")
    list_per_page = 10


class GeneralIndicatorDataAdmin(admin.ModelAdmin):
    # 'focus_area',

    list_display = (
        "general_indicator",
        "indicator_value",
        "reporting_year",
        "updated_by",
    )
    # search_fields = ('indicator', 'member_state', 'reporting_year',)

    list_per_page = 10


class ScorecardAdmin(admin.ModelAdmin):
    list_display = ("scorecard_name", "scorecard_title",
                    "description", "aggregation")

    list_filter = ["scorecard_title"]


class ScorecardConfigAdmin(admin.ModelAdmin):
    list_display = ("scorecard", "indicator", "num_denom", "aggregation")
    list_filter = ["scorecard"]


class ChartAdmin(admin.ModelAdmin):
    list_display = (
        "chart_name",
        "chart_title",
        "description",
        "chart_type",
        "y_axis_title",
        "aggregation",
    )

    list_filter = ("chart_title", "chart_type")


class ChartConfigAdmin(admin.ModelAdmin):
    list_display = ("chart", "indicator", "series_name", "extra_calculation")
    list_filter = ["chart"]


class ExchangeRateDataAdmin(admin.ModelAdmin):
    list_display = (
        "member_state",
        "currency_label",
        "exchange_rate",
        "exchange_rate_date",
        "reporting_year",
        "submitted",
        "validated",
    )
    list_filter = ("currency__member_state", "reporting_year")


class IndicatorAssignedAdmin(admin.ModelAdmin):
    list_display = ("indicator", "assigned_to_organisation")


class FocusAreaAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "abbreviation",
        "focusarea_status",
    ]
    list_filter = [
        "title",
        "abbreviation",
        "focusarea_status",
    ]

    list_per_page = 10


class IndicatorAdmin(admin.ModelAdmin):
    list_display = [
        "label",
        "indicator_number",
        "focus_area",
        "data_type",
        "indicator_type",
        "status",
        "required",
        "indicator_assigned_to",
    ]
    list_filter = ["focus_area", "label", "indicator_type", "status"]

    list_per_page = 10


class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ["reporting_start_date", "reporting_end_date", "current"]


class IndicatorDataValidationHistoryAdmin(admin.ModelAdmin):
    # 'focus_area',

    list_display = (
        "indicator_data",
        "previous_data",
        "current",
        "comments",
        "last_update",
        "updated_by",
    )
    # search_fields = ('indicator_data')

    list_per_page = 10


class MemberStateAdmin(admin.ModelAdmin):
    list_display = (
        "member_state",
        "member_state_short_name",
        "member_state_iso3_code",
        "memberstate_status",
    )


class GeneralIndicatorAdmin(admin.ModelAdmin):
    list_display = ("indicator_label", "include_in_chart", "series_name")


class PublishedAdmin(admin.ModelAdmin):
    list_display = ("reporting_year", "published_status",
                    "last_update", "updated_by")


admin.site.register(FocusArea, FocusAreaAdmin)
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
admin.site.register(ChartConfig, ChartConfigAdmin)
admin.site.register(ScoreCard, ScorecardAdmin)
admin.site.register(ScoreCardConfig, ScorecardConfigAdmin)
