
from django.db.models import Q
from django.conf import settings

from django.template import Library
from core.sharedfunctions import get_current_reporting_year, data_by_year_status

from portaldata.models import INDICATORDATA_STATUS, ExchangeRateData, Indicator, IndicatorData, MemberState, Published
# from portaldata.views.admin_views import data_by_year_status
# from portaldata.views.admin_views import indicator_data_by_year_status

register = Library()

# Start Region -  Per focus area


@register.simple_tag
def getActiveRequiredindicatorsbyassignedto(focusarea, assginedto, *args):
    return focusarea.count_active_required_indicators_by_assignment(assginedto)


@register.simple_tag
def getCompletedActiveRequiredindicatorsbyassignedto(focusarea, assginedto, memberstate, *args):
    # memberstate = MemberState.objects.get(pk=memberstate)
    return focusarea.count_completed_indicators_by_assignment(assginedto, memberstate, get_current_reporting_year())


@register.simple_tag
def calculateprogress(focusarea, assignedto, memberstate, *args):
    try:
        ind_progress = round(
            getCompletedActiveRequiredindicatorsbyassignedto(
                focusarea, assignedto, memberstate)
            / getActiveRequiredindicatorsbyassignedto(focusarea, assignedto) * 100)
        return ind_progress
    except ZeroDivisionError:
        ind_progress = 0
    return ind_progress


@register.simple_tag
def getSubmitted(focusarea, assignedto, memberstate, *args):
    # memberstate = MemberState.objects.get(pk=memberstate)
    return focusarea.check_submitted(assignedto, memberstate, get_current_reporting_year())


@register.simple_tag
def getRevisionRequest(focusarea, assignedto, memberstate, *args):
    # memberstate = MemberState.objects.get(pk=memberstate)
    return focusarea.get_revision_request(assignedto, memberstate, get_current_reporting_year())


@register.simple_tag
def getRevisionRequest_any(assignedto, memberstate, *args):

    ind_count = IndicatorData.objects.filter(
        indicator__indicator_assigned_to=assignedto,
        reporting_year=get_current_reporting_year(),
        member_state=memberstate,
        submitted=False,
        validation_status=INDICATORDATA_STATUS.returned,
    ).count()
    # memberstate = MemberState.objects.get(pk=memberstate)
    return ind_count


@register.simple_tag
def getRevisionRequestOrg(indicator, org, *args):
    # memberstate = MemberState.objects.get(pk=memberstate)
    return indicator.get_revision_request(org, get_current_reporting_year())


# End Region - Per focus area


# Start Region - Overall progress

@register.simple_tag
def countallactiveindicators(assignedto):
    '''For Member States  +1 is to ensure exchange rate data is also required  '''
    ind_count = Indicator.objects.filter(focus_area__focusarea_status=True,
                                         status='Active', required=True, indicator_assigned_to=assignedto).count()
    return ind_count + 1


@register.simple_tag
def countallactiveindicatorsOrg(org):
    '''For Organisations'''
    ind_count = Indicator.objects.filter(focus_area__focusarea_status=True,
                                         status='Active', required=True, assignedindicator__assigned_to_organisation=org).count()
    return ind_count


@register.simple_tag
def countallcompletedindicators(assignedto, memberstate):
    '''For Member States'''
    ind_count = IndicatorData.objects.filter(indicator__required=True, indicator__indicator_assigned_to=assignedto,
                                             member_state=memberstate, indicator__focus_area__focusarea_status=True,
                                             reporting_year=get_current_reporting_year(),
                                             ).exclude(value_NA=False, ind_value__exact=''
                                                       ).exclude(value_NA=False, ind_value__isnull=True).count()
    return ind_count + isExchangeDataCompleted(memberstate)


@register.simple_tag
def countalloptionalcompletedindicators(assignedto, memberstate):
    '''For Member States'''
    ind_count = IndicatorData.objects.filter(indicator__required=False, indicator__indicator_assigned_to=assignedto,
                                             member_state=memberstate, indicator__focus_area__focusarea_status=True,
                                             reporting_year=get_current_reporting_year(),
                                             ).exclude(~Q(value_NA=True) & (Q(ind_value='') | Q(ind_value=None))).count()
    # ind_count = IndicatorData.objects.filter(indicator__required=False, indicator__indicator_assigned_to=assignedto,
    #                                          member_state=memberstate, indicator__focus_area__focusarea_status=True,
    #                                          reporting_year=get_current_reporting_year(),
    #                                          ).exclude(ind_value__exact=''
    #                                                    ).exclude(ind_value__isnull=True).count()

    return ind_count


@register.simple_tag
def countallcompletedindicatorsOrg(org):
    '''For Organisations'''
    ind_count = IndicatorData.objects.filter(indicator__required=True, indicator__assignedindicator__assigned_to_organisation=org,
                                             indicator__focus_area__focusarea_status=True, member_state__memberstate_status=True,
                                             reporting_year=get_current_reporting_year(),
                                             ).exclude(value_NA=False, ind_value__exact=''
                                                       ).exclude(value_NA=False, ind_value__isnull=True).count()
    return ind_count


@register.simple_tag
def calculateoverallprogress(assignedto, memberstate, *args):
    '''For Member States'''
    try:
        ind_progress = round(
            countallcompletedindicators(
                assignedto, memberstate)
            / countallactiveindicators(assignedto) * 100)
        return ind_progress
    except ZeroDivisionError:
        ind_progress = 0
    return ind_progress


def count_active_member_states():
    active_member_states = MemberState.objects.filter(
        memberstate_status=True).count()
    return active_member_states


@register.simple_tag
def calculateoverallprogressOrg(org, *args):
    '''For Organisations'''
    try:
        ind_progress = round(
            countallcompletedindicatorsOrg(org)
            / (countallactiveindicatorsOrg(org) * count_active_member_states()) * 100)
        return ind_progress
    except ZeroDivisionError:
        ind_progress = 0
    return ind_progress


@register.simple_tag
def getOverallToSubmit(assignedto, memberstate, *args):
    '''For Member States'''

    ind_count = IndicatorData.objects.filter(submitted=False, reporting_year=get_current_reporting_year(),
                                             indicator__indicator_assigned_to=assignedto,
                                             indicator__focus_area__focusarea_status=True,
                                             member_state=memberstate).exclude(~Q(value_NA=True) & (Q(ind_value='') | Q(ind_value=None))).count()
    # ind_count = IndicatorData.objects.filter(submitted=False, reporting_year=get_current_reporting_year(),
    #                                          indicator__indicator_assigned_to=assignedto,
    #                                          indicator__focus_area__focusarea_status=True,
    #                                          member_state=memberstate).exclude(~Q(value_NA=True) & (Q(ind_value='') | Q(ind_value=None))).count()
    print(ind_count)
    return ind_count + getExchangeDataUnsubmitted(memberstate)


@ register.simple_tag
def getOverallToSubmitOrg(org, *args):
    '''For Organisations'''
    ind_count = IndicatorData.objects.filter(submitted=False, reporting_year=get_current_reporting_year(),
                                             indicator__assignedindicator__assigned_to_organisation=org,
                                             indicator__focus_area__focusarea_status=True,
                                             member_state__memberstate_status=True,
                                             ).count()
    return ind_count


# End Region - Overall progress


@ register.simple_tag
def isExchangeDataCompleted(memberstate, *args):
    # memberstate = MemberState.objects.get(pk=memberstate)

    completed = ExchangeRateData.objects.filter(currency__member_state=memberstate,
                                                reporting_year=get_current_reporting_year()).count()
    return completed


@ register.simple_tag
def getExchangeDataUnsubmitted(memberstate, *args):
    # memberstate = MemberState.objects.get(pk=memberstate)
    ind_count = ExchangeRateData.objects.filter(currency__member_state=memberstate, submitted=False,
                                                reporting_year=get_current_reporting_year()).count()

    return ind_count


@ register.simple_tag
def getCountbyYearandStatus(reporting_year, validation_status):
    '''Count of indicators by their status (validated, ready, returned) for the selected reporting year'''
    ind_count = data_by_year_status(
        reporting_year, validation_status)

    return ind_count


@register.simple_tag
def getPublishedStatus(reporting_year):
    '''Returns the status of published indicators for years'''
    published = Published.objects.filter(reporting_year=reporting_year)

    if published:
        status = published[0].published_status
    else:
        status = False

    return status
