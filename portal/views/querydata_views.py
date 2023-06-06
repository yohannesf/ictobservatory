
from django.contrib.humanize.templatetags.humanize import intcomma

from django_tables2 import RequestConfig

from django.db.models import Max

from datetime import datetime
from django_tables2.export.export import TableExport
import django_tables2 as tables

from django.shortcuts import render
from portal.forms import FilterForm


from portaldata.models import Indicator, IndicatorData, INDICATORDATA_STATUS, Published


from django.shortcuts import render


from django_pivot.pivot import pivot


def get_published_years_for_query():
    '''Get Published Years from database'''

    # from portaldata.models import Published
    year = []
    year = list(Published.objects.filter(
        published_status=True).values_list('reporting_year', flat=True).order_by('-reporting_year'))

    return year


def generate_report(request):
    '''
    Report / Query Generator
    First implement the filter
    '''

    form = FilterForm(request.GET or None)

    currency_data_type = ''

    currency_indicators = []

    context = {}

    dict_values = []

    pivot_table = None

    ind_data = None

    if request.method == "GET":

        indicators_qs = Indicator.objects.filter(
            status='Active', focus_area__focusarea_status=True).values()

        currency_indicators = list(indicators_qs.filter(
            data_type=0).values_list("id", flat=True))

        export_format = request.GET.get('_export', None)

        indicators = request.GET.getlist('indicator_filter_field')
        ms = request.GET.getlist('memberstate_filter_field')

        years = request.GET.getlist('year_filter_field')

        if indicators or ms or years:

            ind_data = IndicatorData.objects.filter(submitted=True, validation_status=INDICATORDATA_STATUS.validated).order_by(
                'member_state__member_state', 'indicator')

            if ms and ms != ['all'] and 'all' not in ms:
                ind_data = ind_data.filter(member_state__in=list(ms))

            if indicators and indicators != ['all'] and 'all' not in indicators:
                ind_data = ind_data.filter(indicator__in=list(indicators))

            # get_published_years_for_query()
            # this is not needed

            if years and years != ['Select All'] and 'Select All' not in years:
                ind_data = ind_data.filter(reporting_year__in=years)
            else:
                ind_data = ind_data.filter(
                    reporting_year__in=get_published_years_for_query())

            if 'filter_usd' in request.GET:

                currency_data_type = '''
                Data for all currency types is converted to USD.
                '''

                pivot_table = pivot(ind_data,
                                    ['indicator__label',
                                        'member_state__member_state'],
                                    'reporting_year', 'ind_value_adjusted', aggregation=Max)  # type: ignore

            elif 'filter_lc' in request.GET:

                currency_data_type = '''Data for all currency types is in Local Currency 
               '''

                pivot_table = pivot(ind_data,
                                    ['indicator__label',
                                        'member_state__member_state'],
                                    'reporting_year', 'ind_value', aggregation=Max)  # type: ignore

            else:

                currency_data_type = None

                pivot_table = pivot(ind_data,
                                    ['indicator__label',
                                        'member_state__member_state'],
                                    'reporting_year', 'ind_value', aggregation=Max)  # type: ignore

            for item in list(pivot_table):
                dict_values = list(item.keys())

            dict_values = dict_values[2:]

            class IndicatorDataTable(tables.Table):

                member_state__member_state = tables.Column()
                indicator__label = tables.Column()

                def render_2021(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)

                def render_2022(self, value):

                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)

                def render_2023(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)

                def render_2024(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)

                class Meta:
                    sequence = ("member_state__member_state",
                                "indicator__label", "...")
                    attrs = {
                        "class": "table table-striped table-bordered dt-responsive compact nowrap"}
                    paginator_class = tables.LazyPaginator
                    empty_text = 'Query did not return any results. Please refine your search.'

            tbl = IndicatorDataTable('')

            for colname in dict_values:
                column = tables.Column(orderable=False, empty_values=None)

                tbl.base_columns[colname] = column  # type: ignore

            tbl = IndicatorDataTable(pivot_table)

            RequestConfig(request).configure(tbl)

            tbl.paginate(page=request.GET.get("page", 1), per_page=25)

            if TableExport.is_valid_format(export_format):

                time_now = datetime.now().strftime("%D_%H_%M")
                file_name = f"{time_now} - SADC ICT Observatory Data"

                exporter = TableExport(export_format, tbl)

                return exporter.response(f"{file_name}"'.{}'.format(export_format))
        else:
            tbl = None

            pivot_table = None

    context = {"table": tbl, "form": form, "currency_indicators": currency_indicators,
               "currency_data_type": currency_data_type}

    return render(request, "portal/generatereport.html", context=context)
