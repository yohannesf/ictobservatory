from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from core.sharedfunctions import get_current_reporting_year

from ..forms.indicator_data_entry_edit_by_ms import ExchangeRateDataForm
from ..models import ExchangeRateData


def exchange_rate_data(request):

    existing = ExchangeRateData.objects.filter(currency__member_state=request.user.getUserMemberState(),
                                               reporting_year=get_current_reporting_year()).first()

    if existing:
        form = ExchangeRateDataForm(instance=existing,
                                    ms=request.user.getUserMemberState())
        if request.method == 'POST':

            form = ExchangeRateDataForm(request.POST, instance=existing,
                                        ms=request.user.getUserMemberState())

            if form.is_valid():
                instance = form.save(commit=False)

                instance.updated_by = request.user
                instance.reporting_year = get_current_reporting_year()
                form.save()
                return HttpResponseRedirect(
                    reverse_lazy(
                        'portaldata:dataentrybyms',))
    else:
        if request.method == 'POST':
            form = ExchangeRateDataForm(
                request.POST, ms=request.user.getUserMemberState())

            if form.is_valid():
                instance = form.save(commit=False)
                instance.reporting_year = get_current_reporting_year()
                instance.updated_by = request.user

                form.save()
                return HttpResponseRedirect(
                    reverse_lazy(
                        'portaldata:dataentrybyms',))
        else:
            form = ExchangeRateDataForm(ms=request.user.getUserMemberState())

    return render(request, 'portaldata/exchange_rate.html', {'form': form})
