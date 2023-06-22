
from django.core.mail import send_mail

from django.shortcuts import render

from django.utils.translation import gettext_lazy as _
from ajax_datatable.views import AjaxDatatableView


from django.db.models import Q

from core.models import User
from core.sharedfunctions import get_current_reporting_year
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ictobservatory import settings
from portaldata.forms.indicator_data_revision import IndicatorDataRevision
from django.template.loader import render_to_string
from notifications.signals import notify
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from portaldata.models import (IND_ASSIGNED_TO, INDICATORDATA_STATUS,
                               AssignedIndicator, IndicatorData, IndicatorDataValidationHistory, MemberState)


@csrf_exempt
@login_required
@staff_member_required
def validate_data(request):
    '''Validat Data button to update indicator data status as "Validated" '''

    if request.method == 'POST':
        id = request.POST.get('id')

        if IndicatorData.objects.get(pk=id).validation_status == INDICATORDATA_STATUS.validated:
            IndicatorData.objects.filter(pk=id).update(
                validation_status=INDICATORDATA_STATUS.ready)
        else:
            IndicatorData.objects.filter(pk=id).update(
                validation_status=INDICATORDATA_STATUS.validated)

            IndicatorDataValidationHistory.objects.filter(indicator_data_id=id).update(
                current=False)

    # return HttpResponse('All Done!')
    return HttpResponse(status=200)


@csrf_exempt
@login_required
@staff_member_required
def send_back_for_revision(request, id):
    '''Sending indicator data for revision'''

    context = {}

    indicatordata = IndicatorData.objects.get(pk=id)

    '''Filter the list of users to get a notification message'''

    if indicatordata.indicator.indicator_assigned_to == IND_ASSIGNED_TO.ORGANIZATIONS:

        org = AssignedIndicator.objects.get(
            indicator=indicatordata.indicator).assigned_to_organisation

        users = User.objects.filter(
            systemuser__user_organisation=org)

    elif indicatordata.indicator.indicator_assigned_to == IND_ASSIGNED_TO.MEMBER_STATES:

        ms = MemberState.objects.get(
            member_state=indicatordata.member_state)
        users = User.objects.filter(
            systemuser__user_member_state=ms)

    else:  # SADC
        org = AssignedIndicator.objects.get(
            indicator=indicatordata.indicator).assigned_to_organisation

        users = User.objects.filter(
            Q(systemuser__user_organisation=org) | Q(is_superuser=True)).distinct().order_by()

    if request.method == 'POST':

        form = IndicatorDataRevision(request.POST)
        comment = request.POST.get('comment')

        if form.is_valid():

            IndicatorData.objects.filter(pk=id).update(submitted=False,
                                                       validation_status=INDICATORDATA_STATUS.returned)

            instance = form.save(commit=False)

            ind_data = IndicatorData.objects.get(pk=id)

            instance.indicator_data = ind_data
            instance.updated_by = request.user
            instance.previous_data = ind_data.ind_value
            instance.comments = comment

            latest = form.save()

            IndicatorDataValidationHistory.objects.filter(indicator_data=ind_data).update(
                current=Q(pk=latest.pk)
            )

            verb = f"Revision Request ({ind_data.indicator.indicator_number})"

            message = comment if comment else f"Please revise indicator {ind_data.indicator.indicator_number}"

            send_notification(sender=request.user, recipients=users,
                              subject=verb, message=message)

            # notify.send(request.user, recipient=users,
            #             verb=verb, description=comment if comment else f"Please revise indicator {ind_data.indicator.indicator_number}")

            return HttpResponse(status=200)

    else:

        form = IndicatorDataRevision()

    context = {
        'form': form
    }
    return HttpResponse(status=200)
    # return HttpResponse('')
    return render(request, 'portaldata/indicator_data_revision.html', context)


def send_notification(sender, recipients, subject, message):

    try:
        notify.send(sender, recipient=recipients,
                    verb=subject, description=message)
        email_address = []

        for i in recipients:
            email_address.append(i.email)

        # email_notifications(
        #     subject=subject, recipient_list=email_address, message=message)
    except:
        print("something went wrong")


def email_notifications(subject, recipient_list, message):

    email_from = settings.EMAIL_HOST_USER

    send_mail(subject, message, email_from, recipient_list)


@login_required
@staff_member_required
def indicatordata_list_view(request):
    """
    Render the page which contains the table.
    That will in turn invoke (via Ajax) object_datatable_view(), to fill the table content
    """
    # model = Track
    template_name = "portaldata/indicator_data_validation.html"

    context = {'reporting_year': get_current_reporting_year()}

    return render(request, template_name, context=context)


@method_decorator(login_required, name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class IndicatorDatatableView(AjaxDatatableView):

    def get_initial_queryset(self, request=None):

        queryset = IndicatorData.objects.filter(indicator__status='Active', indicator__focus_area__focusarea_status=True,
                                                reporting_year=get_current_reporting_year()
                                                ).exclude(validation_status=INDICATORDATA_STATUS.draft)

        return queryset

    def render_row_details(self, pk, request=None):

        ind_data = self.model.objects.get(pk=pk)

        context = {'ind_data': ind_data}

        return render_to_string('portaldata/render_row_details.html', context)

    model = IndicatorData
    code = 'indicatordata'
    title = _('IndicatorData')
    initial_order = []  # [["member_state", "asc"], ["indicator", "asc"]]
    length_menu = [[25, 50, 100, -1], [25, 50, 100, 'all']]
    search_values_separator = '+'
    show_date_filters = False

    qs = IndicatorData.objects.filter(reporting_year=get_current_reporting_year(), indicator__status='Active',
                                      indicator__focus_area__focusarea_status=True).values('indicator__label', 'indicator__focus_area__title'
                                                                                           ).exclude(validation_status=INDICATORDATA_STATUS.draft).distinct()

    '''converts ValuesQuerySet into Python list'''
    indicators_list = tuple(set(
        [(q['indicator__label'], q['indicator__label']) for q in qs]))

    focusareas_list = tuple(set(
        [(q['indicator__focus_area__title'], q['indicator__focus_area__title']) for q in qs]))

    validation_status = ((INDICATORDATA_STATUS.ready, 'Ready for validation'), (
        INDICATORDATA_STATUS.returned, 'Returned for revision'), (INDICATORDATA_STATUS.validated, 'Validated'))
    v_status = ((INDICATORDATA_STATUS.ready, 'Ready for validation'), (
        INDICATORDATA_STATUS.returned, 'Returned for revision'), (INDICATORDATA_STATUS.validated, 'Validated'))

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'pk', 'visible': False, },

        {'name': 'member_state', 'visible': True, 'searchable': True, 'orderable': True,
            'foreign_field': 'member_state__member_state', 'choices': True, 'autofilter': True, },

        {'name': 'Focus Area', 'visible': True, 'searchable': True, 'orderable': True,
            'foreign_field': 'indicator__focus_area__title', 'choices': focusareas_list, 'autofilter': True, },


        {'name': 'S/N', 'title': 'S/N', 'visible': True, 'searchable': True, 'orderable': True, 'foreign_field': 'indicator__indicator_number',
         'choices': True, 'autofilter': True, 'sort_field': "indicator__pk"},

        {'name': 'indicator', 'visible': True, 'searchable': True, 'orderable': True, 'sort_field': 'indicator__pk',
            'foreign_field': 'indicator__label', 'choices': indicators_list, 'autofilter': True, },


        {'name': 'format_value', 'title': '&nbsp;&nbsp;&nbsp;&nbsp;Data&nbsp;&nbsp;&nbsp;&nbsp;',
            'visible': True,  'className': 'text-center'},



        {'name': 'get_validation_status', 'title': 'Validation Status', 'choices': v_status, 'autofilter': True,
            'visible': False, 'width': 50, 'orderable': False, },

        {'name': 'validation_status', 'title': 'Validation Status', 'choices': validation_status, 'autofilter': True,
            'visible': True, 'width': 50, 'orderable': False, },

        {'name': 'validate', 'title': 'Validate',
            'searchable': False, 'orderable': False, 'className': 'text-center', },

        {'name': 'sendback', 'title': 'Send for revision', 'className': 'text-center',
            'searchable': False, 'width': 50, 'orderable': False, },

    ]

    def customize_row(self, row, obj):

        row['validation_status'] = '<span class="badge validation-status-%s" >%s</span>' % (
            obj.validation_status, row['validation_status']

        ),

        row['validate'] = """
            <button  class="btn btn-primary btn-esm" 
               onclick = "Validate(this.closest('tr').id.substr(4))"
               >

               <span data-toggle="tooltip" title="Validate" class="bi bi-check2-circle" aria-hidden="true"> </span>
            </button>



        """

        row['sendback'] = """

           
            
            <button name = 'send-back' value=this.closest('tr').id.substr(4)  "
           class = "sendback bs-modal btn btn-esm btn-primary" >
                 <span data-toggle = "tooltip" title = "Send back for revision" class = "bi bi-arrow-repeat" > </span >
               </button>

           


        """
