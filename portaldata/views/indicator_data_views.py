from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from notifications.signals import notify
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.forms import formset_factory, modelformset_factory

from core.decorators import group_required
from core.models import SystemUser, User
from core.views import Get_Reporting_Year
from ..models import (DATA_TYPE, IND_ASSIGNED_TO, INDICATORDATA_STATUS, ExchangeRateData, FocusArea,
                      GeneralIndicator, GeneralIndicatorData, Indicator, IndicatorData, MemberState)
from ..forms.indicator_data_entry_edit_by_ms import IndicatorDataEntryForm, IndicatorDataEditForm
from ..forms.indicator_data_entry_edit_by_orgs import GeneralIndicatorDataForm, IndicatorDataEntryFormOrg, IndicatorDataEditFormOrg


@login_required
# @group_required('Member State')
def dataentryprogress(request):
    '''Data Entry Progress page for Member States'''

    focusareas = FocusArea.objects.filter(
        focusarea_status=True)  # type: ignore

    context = {'focusareas': focusareas}
    return render(request, 'portaldata/data-entry-progress.html', context=context)


@login_required
# @group_required('Organisation')
def dataentryprogressorg(request):
    '''Data Entry Progress page for Organisations'''

    indicators = Indicator.objects.filter(status='Active', indicator_assigned_to=IND_ASSIGNED_TO.ORGANIZATIONS, focus_area__focusarea_status=True,
                                          assignedindicator__assigned_to_organisation=request.user.getUserOrganisation())

    context = {'indicators': indicators,
               }
    return render(request, 'portaldata/data-entry-progress-org.html', context=context)


@login_required
def manage_general_indicatordata(request):
    '''General Indicator Data View'''

    qs_gen_ind_data = GeneralIndicatorData.objects.filter(
        reporting_year=Get_Reporting_Year())

    num_gen_ind_data = qs_gen_ind_data.count()

    num_extra = 0
    num_general_indicators = GeneralIndicator.objects.all().count()

    if qs_gen_ind_data:

        if num_gen_ind_data == num_general_indicators:
            num_extra = 0
        elif num_general_indicators > num_gen_ind_data:
            num_extra = num_general_indicators - num_gen_ind_data
        else:
            num_extra = num_general_indicators
    else:
        num_extra = num_general_indicators

    GeneralIndicatorDataFormSet = modelformset_factory(
        GeneralIndicatorData, fields=('general_indicator', 'indicator_value'), extra=num_extra)
    GeneralIndicatorDataFormSet = modelformset_factory(
        GeneralIndicatorData, form=GeneralIndicatorDataForm, extra=num_extra)

    if request.method == 'POST':
        formset = GeneralIndicatorDataFormSet(request.POST)

        if formset.is_valid():

            instances = formset.save(commit=False)
            for instance in instances:
                instance.reporting_year = Get_Reporting_Year()
                instance.updated_by = request.user
                instance.save()

            messages.success(request, 'Saved')
            # return HttpResponseRedirect(
            #     reverse_lazy('portaldata:index',))
    else:
        formset = GeneralIndicatorDataFormSet(
            queryset=GeneralIndicatorData.objects.filter(reporting_year=Get_Reporting_Year()))

    context = {'formset': formset}
    return render(request, 'portaldata/data-entry-sadc.html', context=context)


@ login_required
# @group_required('Member State')
def manage_indicatordata(request, id):
    '''
    Data Entry / Edit by Member States
    '''

    focusarea_title = FocusArea.objects.get(
        pk=id).title

    exisiting_indicator_data = IndicatorData.objects.prefetch_related('indicator').filter(
        indicator__focus_area=id, indicator__status='Active',
        indicator__indicator_assigned_to=IND_ASSIGNED_TO.MEMBER_STATES,
        reporting_year=Get_Reporting_Year(),
        member_state=request.user.getUserMemberState())

    initial_indicator_data = [{'indicator': q}
                              for q in Indicator.objects.filter(focus_area=id, focus_area__focusarea_status=True)
                              .filter(status='Active', indicator_assigned_to=IND_ASSIGNED_TO.MEMBER_STATES)]

    IndicatorDataEditFormSet = modelformset_factory(
        IndicatorData, form=IndicatorDataEditForm, can_delete=False, extra=0)

    '''if there is an existing data, fetch for edit'''
    if (exisiting_indicator_data):

        formset = IndicatorDataEditFormSet(
            request.POST or None, queryset=exisiting_indicator_data)

        if request.method == 'POST':
            formset = IndicatorDataEditFormSet(
                request.POST or None, queryset=exisiting_indicator_data)

            if formset.is_valid():

                for form in formset:
                    if form.is_valid():

                        instance = form.save(commit=False)

                        instance.updated_by = request.user

                        instance.save()
                messages.success(request, 'Saved')
                return HttpResponseRedirect(
                    reverse_lazy('portaldata:manage_indicatordata', kwargs={'id': id}))

    else:
        '''if there are no exisitng data, fetch all indicators for creating data:'''

        IndicatorDataEntryFormSet = formset_factory(
            IndicatorDataEntryForm, extra=0)

        formset = IndicatorDataEntryFormSet(
            request.POST or None)

        if request.method == 'POST':

            formset = IndicatorDataEntryFormSet(request.POST, request.FILES)

            if formset.is_valid():
                for form in formset.forms:

                    if form.is_valid():
                        instance = form.save(commit=False)

                        instance.reporting_year = Get_Reporting_Year()
                        instance.member_state = request.user.getUserMemberState()
                        instance.created_by = request.user
                        instance.updated_by = request.user

                        instance.save()
                messages.success(request, 'Saved')
                return HttpResponseRedirect(
                    reverse_lazy(
                        'portaldata:manage_indicatordata', kwargs={'id': id}))

        else:
            formset = IndicatorDataEntryFormSet(
                initial=initial_indicator_data)

    context = {'formset': formset, 'initial_indicator_data': initial_indicator_data,
               'exisiting_indicator_data': exisiting_indicator_data, 'focusarea_title': focusarea_title}
    return render(request, 'portaldata/data-entry.html', context=context)


@ login_required
# @group_required('Organisation')
def manage_indicatordata_organisation(request, id):
    '''
    Data Entry / Edit by Organizations
    '''

    initial_indicator_data = Indicator.objects.get(
        pk=id)

    exisiting_indicator_data = IndicatorData.objects.prefetch_related('indicator').filter(
        indicator=id, indicator__status='Active',
        member_state__memberstate_status=True,
        reporting_year=Get_Reporting_Year())

    member_state_initial_data = [{'member_state': q}
                                 for q in MemberState.objects.filter(memberstate_status=True)]

    IndicatorDataEditFormSet = modelformset_factory(
        IndicatorData, form=IndicatorDataEditFormOrg, can_delete=False, extra=0)

    IndicatorDataEntryFormSet = formset_factory(
        IndicatorDataEntryFormOrg, extra=0)

    if (exisiting_indicator_data):

        formset = IndicatorDataEditFormSet(
            request.POST or None, queryset=exisiting_indicator_data)

        if request.method == 'POST':
            formset = IndicatorDataEditFormSet(
                request.POST or None, queryset=exisiting_indicator_data)

            if formset.is_valid():

                for form in formset:
                    if form.is_valid():

                        instance = form.save(commit=False)

                        instance.updated_by = request.user

                        instance.save()
                messages.success(request, 'Saved')
                return HttpResponseRedirect(
                    reverse_lazy('portaldata:manage_indicatordata_organisation', kwargs={'id': id}))

    else:

        if request.method == 'POST':

            formset = IndicatorDataEntryFormSet(request.POST, request.FILES, form_kwargs={
                'indicator': initial_indicator_data})

            if formset.is_valid():

                for form in formset.forms:

                    if form.is_valid():
                        instance = form.save(commit=False)

                        instance.reporting_year = Get_Reporting_Year()

                        instance.created_by = request.user
                        instance.updated_by = request.user

                        instance.save()
                messages.success(request, 'Saved')
                return HttpResponseRedirect(
                    reverse_lazy(
                        'portaldata:manage_indicatordata_organisation', kwargs={'id': id}))

        else:

            formset = IndicatorDataEntryFormSet(
                initial=member_state_initial_data, form_kwargs={'indicator': initial_indicator_data})

    context = {

        'formset': formset,
        'initial_indicator_data': initial_indicator_data,
        'exisiting_indicator_data': exisiting_indicator_data,

    }
    return render(request, 'portaldata/data-entry-organisation.html', context=context)


@ login_required
@ group_required('Member State', 'Organisation', 'SADC')
def showdefinition(request, id):
    indicator = Indicator.objects.get(pk=id)
    return render(request, 'portaldata/_definition.html', {'indicator': indicator})


def SendNotification(name, submittedby, reporting_year):
    '''Send Notification to Admin/SADC when data is submitted'''

    sadc = list(SystemUser.objects.filter(
        user_organisation__organisation_name__iexact='SADC').values_list('user__id', flat=True))

    if sadc:

        users = User.objects.filter(Q(id__in=sadc) |
                                    Q(is_superuser=True)).distinct().order_by()

    else:
        users = User.objects.filter(
            Q(is_superuser=True)).distinct().order_by()

    description = f'{name} has submitted data for the {reporting_year} reporting Year. Please visit the indicator validation page to review the data.'

    notify.send(submittedby, recipient=users,
                verb='Data Submission',
                description=description)

    email_from = settings.EMAIL_HOST_USER

    recipient_list = []
    for u in users:
        recipient_list.append(u.email)

    send_mail('Data Submission', description, email_from, recipient_list)


def update_currency_indicators_to_usd(reporting_year, member_state=''):
    '''
    Once data is submitted, all the currency indicators (except GDP and GNI)
    will be converted from local currency to USD using the exchange rate data
    '''

    if not member_state:

        exchange_rate = dict(list(ExchangeRateData.objects.filter(
            reporting_year=reporting_year).values_list('currency__member_state__member_state', 'exchange_rate')))
    else:
        exchange_rate = dict(list(ExchangeRateData.objects.filter(
            reporting_year=reporting_year, currency__member_state__member_state=member_state).values_list('currency__member_state__member_state', 'exchange_rate')))

    ind_data = IndicatorData.objects.filter(
        reporting_year=reporting_year)

    with transaction.atomic():
        for data in ind_data:
            if data.ind_value:
                if data.indicator.data_type == DATA_TYPE.currency and data.indicator.type_of_currency != 'usd':
                    if exchange_rate.get(data.member_state.member_state):

                        IndicatorData.objects.filter(pk=data.pk).update(ind_value_adjusted=round(float(
                            data.ind_value) / float(exchange_rate.get(data.member_state.member_state)), 4))  # type: ignore
                else:
                    IndicatorData.objects.filter(pk=data.pk).update(
                        ind_value_adjusted=data.ind_value)


@ login_required
@ group_required('Member State', 'Organisation', 'SADC')
def submitIndicatorData(request):
    '''Submit Indicator data (by Member States) and send notification to Admin/SADC'''

    ExchangeRateData.objects.filter(currency__member_state=request.user.getUserMemberState(),
                                    reporting_year=Get_Reporting_Year()).update(submitted=True)

    IndicatorData.objects.filter(submitted=False, reporting_year=Get_Reporting_Year(),
                                 indicator__indicator_assigned_to=IND_ASSIGNED_TO.MEMBER_STATES,
                                 indicator__focus_area__focusarea_status=True,
                                 member_state=request.user.getUserMemberState()). \
        update(submitted=True, validation_status=INDICATORDATA_STATUS.ready)

    messages.success(request, 'Data Submitted Successfully.')

    ms = request.user.getUserMemberState().member_state

    '''Here, the function call below ensures local currencies are converted to USD values'''
    update_currency_indicators_to_usd(Get_Reporting_Year(), ms)

    SendNotification(ms, request.user, Get_Reporting_Year())

    return HttpResponseRedirect(
        reverse_lazy(
            'portaldata:dataentrybyms',))


@ login_required
@ group_required('Member State', 'Organisation', 'SADC')
def submitIndicatorDatabyOrg(request):
    '''Submit Indicator data (by Organisations) and send notification to Admin/SADC'''

    IndicatorData.objects.filter(submitted=False, reporting_year=Get_Reporting_Year(),
                                 indicator__indicator_assigned_to=IND_ASSIGNED_TO.ORGANIZATIONS,
                                 indicator__assignedindicator__assigned_to_organisation=request.user.getUserOrganisation(),
                                 indicator__focus_area__focusarea_status=True,). \
        update(submitted=True, validation_status=INDICATORDATA_STATUS.ready)

    messages.success(request, 'Data Submitted Successfully')

    org = request.user.getUserOrganisation().organisation_name

    '''Here, the function call below ensures local currencies are converted to USD values'''
    update_currency_indicators_to_usd(Get_Reporting_Year())

    SendNotification(org, request.user, Get_Reporting_Year())

    return HttpResponseRedirect(
        reverse_lazy(
            'portaldata:dataentrybyorg',))
