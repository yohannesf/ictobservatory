
from django.db import transaction
import json
from django.contrib import messages
from notifications.models import Notification
from django.core.mail import send_mail
from django.conf import settings
from notifications.signals import notify
from django.utils.translation import gettext_lazy as _

from ajax_datatable.views import AjaxDatatableView
from django.views.decorators.csrf import csrf_exempt


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
from core.models import User
import portal
from ..models import DATA_TYPE, IND_ASSIGNED_TO, ExchangeRateData, FocusArea, GeneralIndicator, Indicator, IndicatorData, MemberState, AssignedIndicator, Published
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from ..forms.admin_forms import (
    IndicatorAssignEditForm, IndicatorAssignEntryForm, IndicatorForm, FocusAreaForm)


@method_decorator(login_required, name='dispatch')
class IndicatorCreateView(CreateView):

    model = Indicator
    # model_form.html -> indicator_form.html
    form_class = IndicatorForm
    success_url = reverse_lazy('portaldata:manageindicators')

    def form_valid(self, form):

        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user

        self.object = form.save()

        this_indicator = form.instance

        if this_indicator.indicator_assigned_to == IND_ASSIGNED_TO.ORGANIZATIONS:
            AssignedIndicator.objects.create(
                indicator=this_indicator, created_by=self.request.user, updated_by=self.request.user)

        # return super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class IndicatorUpdateView(UpdateView):

    model = Indicator

    form_class = IndicatorForm

    success_url = reverse_lazy('portaldata:manageindicators')

    def form_valid(self, form):

        form.instance.updated_by = self.request.user

        self.object = form.save()

        this_indicator = form.instance

        if this_indicator.indicator_assigned_to != IND_ASSIGNED_TO.ORGANIZATIONS:
            AssignedIndicator.objects.filter(
                indicator__id=this_indicator.id).delete()
        elif this_indicator.indicator_assigned_to == IND_ASSIGNED_TO.ORGANIZATIONS:
            AssignedIndicator.objects.update_or_create(
                indicator=this_indicator, created_by=this_indicator.created_by, updated_by=self.request.user)

        # return super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())
        # return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class GeneralIndicatorListView(ListView):
    model = GeneralIndicator
    # model_list.html -> indicator_list.html

    context_object_name = "GeneralIndicators"


@method_decorator(login_required, name='dispatch')
class GeneralIndicatorCreateView(CreateView):

    model = GeneralIndicator
    # model_form.html -> indicator_form.html
    # form_class = IndicatorForm
    fields = ['indicator_label', 'include_in_chart', 'definition']
    success_url = reverse_lazy('portaldata:managegeneralindicators')

    def form_valid(self, form):

        # form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class GeneralIndicatorUpdateView(UpdateView):

    model = GeneralIndicator
    # model_form.html -> indicator_form.html
    # form_class = IndicatorForm
    fields = ['indicator_label', 'include_in_chart', 'definition']
    success_url = reverse_lazy('portaldata:managegeneralindicators')

    def form_valid(self, form):

        # form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


# class IndicatorListView(ListView):
#     model = Indicator
#     # model_list.html -> indicator_list.html

#     context_object_name = "Indicators"

@login_required
def indicator_list_view(request):
    """
    Render the page which contains the table.
    That will in turn invoke (via Ajax) object_datatable_view(), to fill the table content
    """
    # model = Track
    template_name = "portaldata/manage_indicator_list.html"

    # context = {'reporting_year': Get_Reporting_Year()}

    return render(request, template_name)  # , context=context)


class IndicatorListtableView(AjaxDatatableView):

    # def render_row_details(self, pk, request=None):
    #     # self.model.objects.get(pk=pk)
    #     ind_data = self.model.objects.get(pk=pk)
    #     # print(ind_data)
    #     # history = IndicatorDataValidationHistory.objects.filter(
    #     #     indicator_data=ind_data)
    #     # 'history': history,
    #     context = {'ind_data': ind_data}

    #     return render_to_string('portaldata/render_row_details.html', context)

    model = Indicator
    code = 'indicator'
    title = _('Indicator')
    initial_order = []  # [["focus_area", "asc"], ["pk", "asc"]]
    # [["focus_area", "asc"],
    length_menu = [[20, 50, 100, -1], [20, 50, 100, 'all']]
    search_values_separator = '+'
    show_date_filters = False

    def sort_queryset(self, params, qs):

        if len(params['orders']):
            # if [indicator_number: ASC]
            qs = qs.order_by(
                *[order.get_order_mode() for order in params['orders']])
        return qs

    # qs = IndicatorData.objects.filter(reporting_year=Get_Reporting_Year(), indicator__status='Active',
    #                                   indicator__focus_area__focusarea_status=True).values('indicator__label', 'indicator__focus_area__title').distinct()

    # # converts ValuesQuerySet into Python list
    # indicators_list = tuple(set(
    #     [(q['indicator__label'], q['indicator__label']) for q in qs]))

    # focusareas_list = tuple(set(
    #     [(q['indicator__focus_area__title'], q['indicator__focus_area__title']) for q in qs]))

    # validation_status = ((INDICATORDATA_STATUS.ready, 'Ready for validation'), (
    #     INDICATORDATA_STATUS.returned, 'Returned for revision'), (INDICATORDATA_STATUS.validated, 'Validated'))

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'pk', 'visible': False, 'orderable': True, },


        {'name': 'focus_area', 'visible': True, 'searchable': True, 'orderable': True,
            'foreign_field': 'focus_area__title', 'choices': True, 'autofilter': True, },

        {'name': 'indicator_number', 'title': 'S/N', 'visible': True, 'searchable': True, 'orderable': True,
         'choices': True, 'autofilter': True, 'sort_field': "id"},

        {'name': 'label', 'title': 'Indicator', 'visible': True, 'searchable': True, 'orderable': True,
         'choices': True, 'autofilter': True, },

        {'name': 'definition', 'visible': False, },

        {'name': 'data_type', 'visible': True, 'searchable': True, 'orderable': True,
         'choices': True, 'autofilter': True, },

        {'name': 'indicator_type', 'title': 'Type',  'visible': True, 'searchable': True, 'orderable': True,
         'choices': True, 'autofilter': True, },

        {'name': 'status', 'visible': True, 'searchable': True, 'orderable': True,
         'choices': True, 'autofilter': True, },

        {'name': 'indicator_assigned_to', 'title': 'Assigned to', 'visible': True, 'searchable': True, 'orderable': True,
         'choices': True, 'autofilter': True, },

        {'name': 'openDefinition', 'title': 'Definition',
            'searchable': False, 'orderable': False, 'className': 'text-center', },

        {'name': 'update', 'title': 'Edit', 'className': 'text-center',
            'searchable': False, 'width': 50, 'orderable': False, },

    ]

    def customize_row(self, row, obj):
        row['update'] = """
            <button name = 'update-indicator'  type = "button"
            onclick = "var id=this.closest('tr').id.substr(4); location.href=('/portaldata/update-indicator/' + id)";

           class = "sendback bs-modal btn btn-esm btn-primary" >
                 <span data-toggle = "tooltip" title = "Edit/Update Indicator" class = "fa fa-pencil-alt" > </span >
               </button>




        """
        # id = obj.id

        row['openDefinition'] = """



            <button name = 'definition' value=this.closest('tr').id.substr(4)  "
           class = "sendback bs-modal btn btn-esm btn-primary" >
                 <span data-toggle = "tooltip" title = "View Definition" class = "fa fa-eye" > </span >
               </button>




        """


@method_decorator(login_required, name='dispatch')
class FocusAreaCreateView(CreateView):
    model = FocusArea
    # model_form.html -> indicator_form.html

    form_class = FocusAreaForm
    success_url = reverse_lazy('portaldata:managefocusarea')

    def get_initial(self):
        # Get the initial dictionary from the superclass method
        initial = super(FocusAreaCreateView, self).get_initial()
        # Copy the dictionary so we don't accidentally change a mutable dict
        # initial = initial.copy()
        initial['sn'] = FocusArea.next_sn(FocusArea)  # type: ignore
        return initial

    def form_valid(self, form):

        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class FocusAreaUpdateView(UpdateView):
    model = FocusArea
    form_class = FocusAreaForm
    # fields = ['title', 'description', 'focusarea_status']
    success_url = reverse_lazy('portaldata:managefocusarea')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class FocusAreaListView(ListView):
    model = FocusArea
    context_object_name = "FocusAreas"


@login_required
def manage_indicatorassignment(request):

    exisiting_indicator_assign_data = AssignedIndicator.objects.prefetch_related('indicator').filter(
        indicator__status='Active', indicator__indicator_assigned_to=IND_ASSIGNED_TO.ORGANIZATIONS)

    initial_indicator_data = [{'indicator': q}
                              for q in Indicator.objects.filter(status='Active', indicator_assigned_to=IND_ASSIGNED_TO.ORGANIZATIONS)]

    IndicatorAssignEditFormSet = modelformset_factory(
        AssignedIndicator, form=IndicatorAssignEditForm, can_delete=False, extra=0)

    # if there is an existing data, fetch for edit
    if (exisiting_indicator_assign_data):

        formset = IndicatorAssignEditFormSet(
            request.POST or None, queryset=exisiting_indicator_assign_data)

        if request.method == 'POST':
            formset = IndicatorAssignEditFormSet(
                request.POST or None, queryset=exisiting_indicator_assign_data)
            # print(formset)
            if formset.is_valid():

                # formset.save()
                for form in formset:
                    if form.is_valid():

                        instance = form.save(commit=False)

                        instance.updated_by = request.user

                        instance.save()

                return HttpResponseRedirect(
                    reverse_lazy('portaldata:indicator-assignment',))

    else:  # there is no exisitng data, fetch all indicators for creating data:

        IndicatorAssignEntryFormSet = formset_factory(
            IndicatorAssignEntryForm, extra=0)

        formset = IndicatorAssignEntryFormSet(
            request.POST or None)

        if request.method == 'POST':

            formset = IndicatorAssignEntryFormSet(request.POST)
            # print(formset)
            if formset.is_valid():
                for form in formset.forms:

                    if form.is_valid():
                        instance = form.save(commit=False)

                        instance.created_by = request.user
                        instance.updated_by = request.user

                        instance.save()
                return HttpResponseRedirect(
                    reverse_lazy(
                        'portaldata:indicator-assignment',))

        else:
            formset = IndicatorAssignEntryFormSet(
                initial=initial_indicator_data)

    context = {'formset': formset, 'initial_indicator_data': initial_indicator_data,
               'exisiting_indicator_assign_data': exisiting_indicator_assign_data}
    return render(request, 'portaldata/indicator-assignment.html', context=context)


@ csrf_exempt
def PublishUnpublish(request):

    if request.method == 'POST':
        id = request.POST.get('id')

    # return render(request, 'portaldata/publish_form.html', context=context)
    return HttpResponse(status=200)


@ csrf_exempt
def publish_data(request):

    indicator_data = IndicatorData.objects.all().values('reporting_year'
                                                        ).distinct().order_by('-reporting_year')

    context = {'indicator_data': indicator_data}

    if request.method == 'POST':
        reporting_year = request.POST.get('reporting_year')

        if reporting_year:

            try:
                published_year = Published.objects.get(
                    reporting_year=reporting_year)

                if published_year.published_status == True:
                    published_year.published_status = False
                    published_year.save()
                elif published_year.published_status == False:
                    published_year.published_status = True
                    published_year.save()

            except:
                published_year = Published(
                    reporting_year=reporting_year, published_status=True, updated_by=request.user)
                published_year.save()

            # messages.success(
            #     request, f'{reporting_year} Data Published Successfully!')

    return render(request, 'portaldata/publish_form.html', context=context)


# def data_by_year_status(reporting_year, validation_status):
#     return 0

#     indicator_data = list(IndicatorData.objects.all().values('reporting_year', 'validation_status'
#                                                              ).annotate(total=Count('validation_status')
#                                                                         ).order_by('-reporting_year', 'validation_status'))

#     data_by_year_and_status = list(
#         filter(lambda ind: ind['reporting_year'] == reporting_year and ind['validation_status'] == validation_status, indicator_data))

#     if data_by_year_and_status:
#         data_count_by_year_status = data_by_year_and_status[0].get('total')
#     else:
#         data_count_by_year_status = 0

#     return data_count_by_year_status


# def sendSystemWideNotification(request):
#     pass
    # notify.send(request.user, recipient=users,
    #                     verb='Revision Request', description=comment if comment else "Please revise this indicator")
    # if request.method == 'POST':
    #     sender = User.objects.get(username=request.user)
    #     receiver = User.objects.get(id=request.POST.get('user_id'))
    #     notify.send(sender, recipient=receiver, verb='Message',
    #                 description=request.POST.get('message'))
    #     return redirect('index')

    # return HttpResponse("Please login from admin site for sending messages")


# def email_notifications(request):

#     #notifications = Notification.objects.filter(emailed=False)

#     subject = 'SADC ICT Observatory - Unread Notifications'
#     email_from = settings.EMAIL_HOST_USER
#     notifications = Notification.objects.filter(emailed=False)

#     notifications = Notification.objects.filter(emailed=False).values(
#         'recipient').annotate(total=Count('id')).order_by()

#     for n in notifications:
#         recipient = User.objects.get(id=n.get("recipient"))
#         recipient_list = [recipient.email, ]

#         message = f'''
# Dear {recipient.get_full_name().title()}

# You have {n.get("total")} unread notifications. Please log into your account to read.

# SADC Secretariat
# http://www.sadc.org
#         '''
#         send_mail(subject, message, email_from, recipient_list)

#     Notification.objects.filter(emailed=False).update(emailed=True)

#     return HttpResponse("sent")
