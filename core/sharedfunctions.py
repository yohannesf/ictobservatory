from portaldata.models import Published


def get_published_years():
    '''Get Published Years from database'''

    year = []
    # year = list(Published.objects.filter(
    #     published_status=True).values('reporting_year').order_by('-reporting_year'))
    year = list(Published.objects.filter(
        published_status=True).values_list('reporting_year', flat=True).order_by('-reporting_year'))

    # print(year)
    return year
