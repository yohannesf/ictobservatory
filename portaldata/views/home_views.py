from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.views import Get_Reporting_Year

from portaldata.views.indicator_data_views import (
    SendNotification_to_self,
    SendNotification_to_self_orgs,
    update_currency_indicators_to_usd,
)
from ..models import Indicator, IndicatorData


@login_required
def index(request):
    """Backend Home Page (a landing page when user is logged in)"""

    # TO DO -> to be replaced by a button on the backend for admins with year selection dropdown
    update_currency_indicators_to_usd("2022")

    return render(request, "portaldata/index.html")


@login_required
def documentation(request):
    return render(request, "portaldata/documentation.html")


def count_all_active_required_indicators():
    ind_count = Indicator.objects.filter(
        status="Active",
        required=True,
    ).count()
    return ind_count


def count_all_completed_required_indicators():
    ind_count = (
        IndicatorData.objects.filter(
            indicator__required=True,
        )
        .exclude(value_NA=False, value__exact="")
        .exclude(value_NA=False, value__isnull=True)
        .count()
    )
    return ind_count


def calculate_overall_progress():
    if count_all_active_required_indicators() == 0:
        return 0
    else:
        ind_progress = round(
            count_all_completed_required_indicators()
            / count_all_active_required_indicators()
            * 100
        )
        return ind_progress
