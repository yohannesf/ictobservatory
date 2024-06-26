
import datetime
from django.db.models import Count


def get_published_years():
    '''Get Published Years from database'''
    from portaldata.models import Published

    year = []

    year = list(Published.objects.filter(
        published_status=True).values_list('reporting_year', flat=True).order_by('-reporting_year'))

    return year


def get_current_reporting_year():
    '''Get the current reporting year'''
    from portaldata.models import ReportingPeriod

    rpt_end_date = ReportingPeriod.objects.filter(
        current=True).values_list('reporting_end_date', flat=True)

    if rpt_end_date:
        rpt_end_date = rpt_end_date[0]
        return str(rpt_end_date.year)
    else:
        return str(datetime.date.today().year)


def get_latest_published_year():
    '''Get Latest Published Year'''
    from portaldata.models import Published

    year = None
    year = list(Published.objects.filter(
        published_status=True).values_list('reporting_year', flat=True).order_by('-reporting_year'))

    if year:
        year = year[0]
    else:
        year = get_current_reporting_year()
    return year


def data_by_year_status(reporting_year, validation_status):
    '''
    For each year with data, show the number of indicator data by status
    Status: ready for validation, validated, returned for revision

    '''
    from portaldata.models import IndicatorData

    indicator_data = list(IndicatorData.objects.all().values('reporting_year', 'validation_status'
                                                             ).annotate(total=Count('validation_status')
                                                                        ).order_by('-reporting_year', 'validation_status'))

    data_by_year_and_status = list(
        filter(lambda ind: ind['reporting_year'] == reporting_year and ind['validation_status'] == validation_status, indicator_data))

    if data_by_year_and_status:
        data_count_by_year_status = data_by_year_and_status[0].get('total')
    else:
        data_count_by_year_status = 0

    return data_count_by_year_status


def get_num_days_remaining():
    '''Get the number of days left for the current reporting year. '''
    from portaldata.models import ReportingPeriod

    if is_reporting_period():

        rpt_end_date = ReportingPeriod.objects.filter(
            current=True).values_list('reporting_end_date', flat=True)

        if rpt_end_date:

            rpt_end_date = rpt_end_date[0]

            num_days_remaining = (rpt_end_date - datetime.date.today()).days
            return num_days_remaining

        else:
            return None
    else:
        return None


def is_reporting_period(additional_days=None):
    '''Check wheter current date (today) within the reporting perid '''
    from portaldata.models import ReportingPeriod

    r_start_date = datetime.date.today()
    r_end_date = datetime.date.today()

    rpt_start_date = ReportingPeriod.objects.filter(
        current=True).values_list('reporting_start_date', flat=True)

    if rpt_start_date:
        r_start_date = rpt_start_date[0]

    rpt_end_date = ReportingPeriod.objects.filter(
        current=True).values_list('reporting_end_date', flat=True)

    if rpt_end_date:
        r_end_date = rpt_end_date[0]

    if additional_days:

        try:

            if datetime.date.today() >= r_start_date and datetime.date.today() <= r_end_date + datetime.timedelta(days=int(additional_days)):

                return True
            else:
                return False
        except:
            return False

    else:

        # if datetime.date.today() == r_start_date and datetime.date.today() == r_end_date:
        #     return False
        if datetime.date.today() >= r_start_date and datetime.date.today() <= r_end_date:
            return True
        else:
            return False
