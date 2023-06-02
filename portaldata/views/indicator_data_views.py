from django.db import transaction
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from notifications.signals import notify
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ajax_datatable.views import AjaxDatatableView
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.forms import formset_factory, modelformset_factory
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from core.decorators import group_required
from core.models import SystemUser, User
from core.views import Get_Reporting_Year
from ..models import (
    DATA_TYPE,
    IND_ASSIGNED_TO,
    INDICATORDATA_STATUS,
    ExchangeRateData,
    FocusArea,
    GeneralIndicator,
    GeneralIndicatorData,
    Indicator,
    IndicatorData,
    MemberState,
)
from ..forms.indicator_data_entry_edit_by_ms import (
    IndicatorDataEntryForm,
    IndicatorDataEditForm,
)
from ..forms.indicator_data_entry_edit_by_orgs import (
    GeneralIndicatorDataForm,
    IndicatorDataEntryFormOrg,
    IndicatorDataEditFormOrg,
)


@login_required
# @group_required('Member State')
def dataentryprogress(request):
    """Data Entry Progress page for Member States"""

    focusareas = FocusArea.objects.filter(
        focusarea_status=True)  # type: ignore

    context = {"focusareas": focusareas}
    return render(request, "portaldata/data-entry-progress.html", context=context)


@login_required
# @group_required('Organisation')
def dataentryprogressorg(request):
    """Data Entry Progress page for Organisations"""

    indicators = Indicator.objects.filter(
        status="Active",
        indicator_assigned_to=IND_ASSIGNED_TO.ORGANIZATIONS,
        focus_area__focusarea_status=True,
        assignedindicator__assigned_to_organisation=request.user.getUserOrganisation(),
    )

    context = {
        "indicators": indicators,
    }
    return render(request, "portaldata/data-entry-progress-org.html", context=context)


@login_required
def manage_general_indicatordata(request):
    """General Indicator Data View"""

    qs_gen_ind_data = GeneralIndicatorData.objects.filter(
        reporting_year=Get_Reporting_Year()
    )

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
        GeneralIndicatorData,
        fields=("general_indicator", "indicator_value"),
        extra=num_extra,
    )
    GeneralIndicatorDataFormSet = modelformset_factory(
        GeneralIndicatorData, form=GeneralIndicatorDataForm, extra=num_extra
    )

    if request.method == "POST":
        formset = GeneralIndicatorDataFormSet(request.POST)

        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.reporting_year = Get_Reporting_Year()
                instance.updated_by = request.user
                instance.save()

            messages.success(request, "Saved")
            # return HttpResponseRedirect(
            #     reverse_lazy('portaldata:index',))
    else:
        formset = GeneralIndicatorDataFormSet(
            queryset=GeneralIndicatorData.objects.filter(
                reporting_year=Get_Reporting_Year()
            )
        )

    context = {"formset": formset}
    return render(request, "portaldata/data-entry-sadc.html", context=context)


@login_required
# @group_required('Member State')
def manage_indicatordata(request, id):
    """
    Data Entry / Edit by Member States
    """

    focusarea_title = FocusArea.objects.get(pk=id).title

    exisiting_indicator_data = IndicatorData.objects.prefetch_related(
        "indicator"
    ).filter(
        indicator__focus_area=id,
        indicator__status="Active",
        indicator__indicator_assigned_to=IND_ASSIGNED_TO.MEMBER_STATES,
        reporting_year=Get_Reporting_Year(),
        member_state=request.user.getUserMemberState(),
    )

    initial_indicator_data = [
        {"indicator": q}
        for q in Indicator.objects.filter(
            focus_area=id, focus_area__focusarea_status=True
        ).filter(status="Active", indicator_assigned_to=IND_ASSIGNED_TO.MEMBER_STATES)
    ]

    IndicatorDataEditFormSet = modelformset_factory(
        IndicatorData, form=IndicatorDataEditForm, can_delete=False, extra=0
    )

    """if there is an existing data, fetch for edit"""
    if exisiting_indicator_data:
        formset = IndicatorDataEditFormSet(
            request.POST or None, queryset=exisiting_indicator_data
        )

        if request.method == "POST":
            formset = IndicatorDataEditFormSet(
                request.POST or None, queryset=exisiting_indicator_data
            )

            if formset.is_valid():
                for form in formset:
                    if form.is_valid():
                        instance = form.save(commit=False)

                        instance.updated_by = request.user

                        instance.save()
                messages.success(request, "Saved")
                return HttpResponseRedirect(
                    reverse_lazy("portaldata:manage_indicatordata",
                                 kwargs={"id": id})
                )

    else:
        """if there are no exisitng data, fetch all indicators for creating data:"""

        IndicatorDataEntryFormSet = formset_factory(
            IndicatorDataEntryForm, extra=0)

        formset = IndicatorDataEntryFormSet(request.POST or None)

        if request.method == "POST":
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
                messages.success(request, "Saved")
                return HttpResponseRedirect(
                    reverse_lazy("portaldata:manage_indicatordata",
                                 kwargs={"id": id})
                )

        else:
            formset = IndicatorDataEntryFormSet(initial=initial_indicator_data)

    context = {
        "formset": formset,
        "initial_indicator_data": initial_indicator_data,
        "exisiting_indicator_data": exisiting_indicator_data,
        "focusarea_title": focusarea_title,
    }
    return render(request, "portaldata/data-entry.html", context=context)


@login_required
# @group_required('Member State')
def view_indicatordata(request):
    """
    Function to show Member States their indicator data on backend. Submitted or in draft status.
    """
    """
    Render the page which contains the table.
    That will in turn invoke (via Ajax) object_datatable_view(), to fill the table content
    """

    # print(type(request.user.getUserMemberState()))

    template_name = "portaldata/view_indicator_data_by_ms.html"

    context = {"reporting_year": Get_Reporting_Year(
    ), "member_state": request.user.getUserMemberState()}

    return render(request, template_name, context=context)


class ViewIndicatorDatatableView(AjaxDatatableView):

    # TO DO: Update queryset to filter all data entered by member states
    # for the current reporting year

    def get_initial_queryset(self, request=None):

        try:

            if 'member_state' in request.REQUEST:
                member_state = request.REQUEST.get('member_state')

                queryset = IndicatorData.objects.filter(
                    # indicator__status="Active",
                    member_state__member_state__exact=member_state,
                    # indicator__focus_area__focusarea_status=True,
                    reporting_year=Get_Reporting_Year(),
                )

                return queryset
            else:
                return None
        except:
            return None

    def render_row_details(self, pk, request=None):
        ind_data = self.model.objects.get(pk=pk)

        context = {"ind_data": ind_data}

        return render_to_string("portaldata/render_row_details_member_states.html", context)

    model = IndicatorData
    code = "indicatordata"
    title = _("IndicatorData")
    initial_order = []  # [["member_state", "asc"], ["indicator", "asc"]]
    length_menu = [[-1], ["All"]]
    search_values_separator = "+"
    show_date_filters = False

    qs = (
        IndicatorData.objects.filter(
            reporting_year=Get_Reporting_Year(),
            indicator__status="Active",
            indicator__focus_area__focusarea_status=True,
        )
        .values("indicator__label", "indicator__focus_area__title")
        .exclude(validation_status=INDICATORDATA_STATUS.draft)
        .distinct()
    )

    """converts ValuesQuerySet into Python list"""
    indicators_list = tuple(
        set([(q["indicator__label"], q["indicator__label"]) for q in qs])
    )

    focusareas_list = tuple(
        set([(q["indicator__focus_area__title"],
            q["indicator__focus_area__title"]) for q in qs])
    )

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {
            "name": "pk", "visible": False,
        },
        {
            "name": "reporting_year", "visible": False,
        },

        {
            "name": "Focus Area", "visible": True, "searchable": True, "orderable": True,
            "foreign_field": "indicator__focus_area__title", "choices": True, "autofilter": True, "width": 100


        },
        {
            "name": "S/N", "title": "S/N", "visible": True, "searchable": True, "orderable": True,
            "foreign_field": "indicator__indicator_number", "choices": True, "autofilter": True,
            "sort_field": "indicator__pk",  "width": 100
        },
        {
            "name": "indicator", "visible": True, "searchable": True, "orderable": True,
            "sort_field": "indicator__pk", "foreign_field": "indicator__label", "choices": True,
            "autofilter": True, "className": "wrapit",
        },
        {
            "name": "format_value", "title": "&nbsp;&nbsp;Data&nbsp;&nbsp;", "visible": True,
            "searchable": False,  "className": "text-center",
            "width": 130,
        },
        {
            "name": "comments", "title": "Comment", "visible": True,
            "searchable": False, "width": 200,
            # "width": 300,
        },
        {
            "name": "format_submitted_status", "title": "Status", "searchable": False,
            "visible": True,  "max_length": 50, "width": 60, "orderable": False,
            # "autofilter": True,"choices": True, 'boolean': True,
        },
        {
            "name": "last_update", "visible": False,
        },
        {
            "name": "updated_by", "visible": False,
        },
    ]


@login_required
# @group_required('Organisation')
def manage_indicatordata_organisation(request, id):
    """
    Data Entry / Edit by Organizations
    """

    initial_indicator_data = Indicator.objects.get(pk=id)

    exisiting_indicator_data = IndicatorData.objects.prefetch_related(
        "indicator"
    ).filter(
        indicator=id,
        indicator__status="Active",
        member_state__memberstate_status=True,
        reporting_year=Get_Reporting_Year(),
    )

    member_state_initial_data = [
        {"member_state": q} for q in MemberState.objects.filter(memberstate_status=True)
    ]

    IndicatorDataEditFormSet = modelformset_factory(
        IndicatorData, form=IndicatorDataEditFormOrg, can_delete=False, extra=0
    )

    IndicatorDataEntryFormSet = formset_factory(
        IndicatorDataEntryFormOrg, extra=0)

    if exisiting_indicator_data:
        formset = IndicatorDataEditFormSet(
            request.POST or None, queryset=exisiting_indicator_data
        )

        if request.method == "POST":
            formset = IndicatorDataEditFormSet(
                request.POST or None, queryset=exisiting_indicator_data
            )

            if formset.is_valid():
                for form in formset:
                    if form.is_valid():
                        instance = form.save(commit=False)

                        instance.updated_by = request.user

                        instance.save()
                messages.success(request, "Saved")
                return HttpResponseRedirect(
                    reverse_lazy(
                        "portaldata:manage_indicatordata_organisation",
                        kwargs={"id": id},
                    )
                )

    else:
        if request.method == "POST":
            formset = IndicatorDataEntryFormSet(
                request.POST,
                request.FILES,
                form_kwargs={"indicator": initial_indicator_data},
            )

            if formset.is_valid():
                for form in formset.forms:
                    if form.is_valid():
                        instance = form.save(commit=False)

                        instance.reporting_year = Get_Reporting_Year()

                        instance.created_by = request.user
                        instance.updated_by = request.user

                        instance.save()
                messages.success(request, "Saved")
                return HttpResponseRedirect(
                    reverse_lazy(
                        "portaldata:manage_indicatordata_organisation",
                        kwargs={"id": id},
                    )
                )

        else:
            formset = IndicatorDataEntryFormSet(
                initial=member_state_initial_data,
                form_kwargs={"indicator": initial_indicator_data},
            )

    context = {
        "formset": formset,
        "initial_indicator_data": initial_indicator_data,
        "exisiting_indicator_data": exisiting_indicator_data,
    }
    return render(request, "portaldata/data-entry-organisation.html", context=context)


@login_required
@group_required("Member State", "Organisation", "SADC")
def showdefinition(request, id):
    indicator = Indicator.objects.get(pk=id)
    return render(request, "portaldata/_definition.html", {"indicator": indicator})


def SendNotification_to_admins(name, submittedby, reporting_year):
    """Send Notification to Admin/SADC when data is submitted"""

    # Get users who are in the SADC group (without necessarily being superusers)
    sadc = list(
        SystemUser.objects.filter(
            user_organisation__organisation_name__iexact="SADC"
        ).values_list("user__id", flat=True)
    )

    if sadc:
        users = (
            User.objects.filter(Q(id__in=sadc) | Q(is_superuser=True))
            .distinct()
            .order_by()
        )
    else:
        users = User.objects.filter(Q(is_superuser=True)).distinct().order_by()

    description = f"{name} has submitted data for the {reporting_year} reporting Year. Please visit the indicator validation page to review the data."

    notify.send(
        submittedby, recipient=users, verb="Data Submission", description=description
    )

    email_from = settings.EMAIL_HOST_USER

    recipient_list = []
    for u in users:
        recipient_list.append(u.email)

    # send_mail('Data Submission', description, email_from, recipient_list)


def SendNotification_to_self(member_state, submittedby, reporting_year):
    """Send Notification to self when data is submitted"""

    users = User.objects.filter(systemuser__user_member_state=member_state)

    description = f"""
    {member_state} has submitted data for the {reporting_year} reporting Year. 
    You can download the submitted data from the backend.
    """

    if users:
        notify.send(
            submittedby,
            recipient=users,
            verb="Data Submission",
            description=description,
        )

    email_from = settings.EMAIL_HOST_USER

    recipient_list = []

    if users:
        for u in users:
            recipient_list.append(u.email)

        # send_mail('Data Submission', description, email_from, recipient_list)


def SendNotification_to_self_orgs(organisation, submittedby, reporting_year):
    """Send Notification to self when data is submitted"""

    users = User.objects.filter(systemuser__user_organisation=organisation)

    description = f"""
    {organisation} has submitted data for the {reporting_year} reporting Year. 
    You can download the submitted data from the backend.
    """

    if users:
        notify.send(
            submittedby,
            recipient=users,
            verb="Data Submission",
            description=description,
        )

    email_from = settings.EMAIL_HOST_USER

    recipient_list = []

    if users:
        for u in users:
            recipient_list.append(u.email)

        # send_mail('Data Submission', description, email_from, recipient_list)


def update_currency_indicators_to_usd(reporting_year, member_state=""):
    """
    Once data is submitted, all the currency indicators (except GDP and GNI)
    will be converted from local currency to USD using the exchange rate data
    """

    if not member_state:
        exchange_rate = dict(
            list(
                ExchangeRateData.objects.filter(
                    reporting_year=reporting_year
                ).values_list("currency__member_state__member_state", "exchange_rate")
            )
        )
    else:
        exchange_rate = dict(
            list(
                ExchangeRateData.objects.filter(
                    reporting_year=reporting_year,
                    currency__member_state__member_state=member_state,
                ).values_list("currency__member_state__member_state", "exchange_rate")
            )
        )

    ind_data = IndicatorData.objects.filter(reporting_year=reporting_year)

    with transaction.atomic():
        for data in ind_data:
            if data.ind_value:
                if (
                    data.indicator.data_type == DATA_TYPE.currency
                    and data.indicator.type_of_currency != "usd"
                ):
                    if exchange_rate.get(data.member_state.member_state):
                        # print(IndicatorData.objects.filter(
                        #     pk=data.pk).values("ind_value"))

                        # print(exchange_rate.get(data.member_state.member_state))

                        IndicatorData.objects.filter(pk=data.pk).update(
                            ind_value_adjusted=(
                                float(data.ind_value)
                                / float(
                                    exchange_rate.get(
                                        data.member_state.member_state)
                                )
                            )
                        )  # type: ignore
                else:
                    IndicatorData.objects.filter(pk=data.pk).update(
                        ind_value_adjusted=data.ind_value
                    )


@login_required
@group_required("Member State", "Organisation", "SADC")
def submitIndicatorData(request):
    """Submit Indicator data (by Member States) and send notification to Admin/SADC"""
    # messages.success(request, "Data Submitted Successfully.")
    # return HttpResponseRedirect(
    #     reverse_lazy(
    #         "portaldata:dataentrybyms",
    #     )
    # )
    ExchangeRateData.objects.filter(
        currency__member_state=request.user.getUserMemberState(),
        reporting_year=Get_Reporting_Year(),
    ).update(submitted=True)

    IndicatorData.objects.filter(
        submitted=False,
        reporting_year=Get_Reporting_Year(),
        indicator__indicator_assigned_to=IND_ASSIGNED_TO.MEMBER_STATES,
        indicator__focus_area__focusarea_status=True,
        member_state=request.user.getUserMemberState(),
    ).update(submitted=True, validation_status=INDICATORDATA_STATUS.ready)

    messages.success(request, "Data Submitted Successfully.")

    ms = request.user.getUserMemberState()

    """Here, the function call below ensures local currencies are converted to USD values"""
    update_currency_indicators_to_usd(Get_Reporting_Year(), ms.member_state)

    SendNotification_to_admins(
        ms.member_state, request.user, Get_Reporting_Year())
    SendNotification_to_self(ms, request.user, Get_Reporting_Year())

    return HttpResponseRedirect(
        reverse_lazy(
            "portaldata:dataentrybyms",
        )
    )


@login_required
@group_required("Member State", "Organisation", "SADC")
def submitIndicatorDatabyOrg(request):
    """Submit Indicator data (by Organisations) and send notification to Admin/SADC"""

    IndicatorData.objects.filter(
        submitted=False,
        reporting_year=Get_Reporting_Year(),
        indicator__indicator_assigned_to=IND_ASSIGNED_TO.ORGANIZATIONS,
        indicator__assignedindicator__assigned_to_organisation=request.user.getUserOrganisation(),
        indicator__focus_area__focusarea_status=True,
    ).update(submitted=True, validation_status=INDICATORDATA_STATUS.ready)

    messages.success(request, "Data Submitted Successfully")

    org = request.user.getUserOrganisation()

    """Here, the function call below ensures local currencies are converted to USD values"""
    update_currency_indicators_to_usd(Get_Reporting_Year())

    SendNotification_to_admins(
        org.organisation_name, request.user, Get_Reporting_Year()
    )
    SendNotification_to_self_orgs(org, request.user, Get_Reporting_Year())

    return HttpResponseRedirect(
        reverse_lazy(
            "portaldata:dataentrybyorg",
        )
    )
