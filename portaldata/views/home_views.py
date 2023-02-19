
from notifications.views import NotificationViewList, AllNotificationsList
from django.conf import settings
from django.shortcuts import get_object_or_404
from notifications.signals import notify
from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


import datetime
from django import forms
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from django.shortcuts import render, redirect
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.forms import formset_factory, model_to_dict, inlineformset_factory, modelformset_factory

from core.decorators import group_required, org_required
from portaldata.views.admin_views import publish_data
from portaldata.views.indicator_data_views import update_currency_indicators_to_usd

from ..models import FocusArea, Indicator, IndicatorData, MemberState, AssignedIndicator


@login_required
def index(request):
    # email_notifications(request)
    # publish_data(request)
    # update_currency_indicators_to_usd(2021)
    return render(request, 'portaldata/index.html')


@login_required
def documentation(request):
    return render(request, 'portaldata/documentation.html')


def count_all_active_required_indicators():

    ind_count = Indicator.objects.filter(
        status='Active', required=True, ).count()
    return ind_count


def count_all_completed_required_indicators():

    ind_count = IndicatorData.objects.filter(indicator__required=True,

                                             ).exclude(value_NA=False, value__exact=''
                                                       ).exclude(value_NA=False, value__isnull=True).count()
    return ind_count


def calculate_overall_progress():

    if (count_all_active_required_indicators() == 0):
        return 0
    else:

        ind_progress = round(
            count_all_completed_required_indicators() / count_all_active_required_indicators() * 100)
        return ind_progress


# class NVL(NotificationViewList):
#     template_name = 'notifications/list.html'
#     context_object_name = 'notifications'


# def check_submitted():
#     ind_count = IndicatorData.objects.filter(submitted=False).count()
#     # print(ind_count)
#     return ind_count


# def open_notification(request, notification_id):
#     notifcation = get_object_or_404(
#         Notification, {"pk": notification_id, "recipient": request.user})
#     notifcation.mark_as_read()
#     return redirect(notifcation.target.get_absolute_url())
