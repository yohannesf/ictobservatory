
from django.contrib.humanize.templatetags.humanize import intcomma

from django.http import HttpResponse
from django_tables2 import RequestConfig

from django.db.models import Max

from datetime import datetime
from django_tables2.export.export import TableExport
import django_tables2 as tables

from django.shortcuts import render
from core.sharedfunctions import get_published_years
from portal.forms import FilterForm


from portaldata.models import ExchangeRateData, Indicator, IndicatorData, INDICATORDATA_STATUS, Published


from django.shortcuts import render


from django_pivot.pivot import pivot

class ExchangeRateDataTable(tables.Table):
                
                #'currency__currency_label',
                #'currency__member_state__member_state'
                currency__member_state__member_state = tables.Column()
                #currency__currency_label = tables.Column()
                # member_state__member_state = tables.Column()
                # indicator__label = tables.Column()
                

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
                    
                def render_2025(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)
                    
                def render_2026(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)
                def render_2027(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)
                def render_2028(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)
                def render_2029(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)
                def render_2030(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)

                class Meta:
                    sequence = ("currency__member_state__member_state", "..."
                                #,"currency__currency_label", "..."
                                )
                    attrs = {
                        "class": "table table-striped table-bordered dt-responsive compact nowrap"}
                    paginator_class = tables.LazyPaginator
                    empty_text = 'Query did not return any results. Please refine your search.'


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
                    
                def render_2025(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)
                    
                def render_2026(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)
                def render_2027(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)
                def render_2028(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)
                def render_2029(self, value):
                    try:
                        value = round(float(value), 2)
                        return intcomma(value)
                    except:
                        return intcomma(value)
                def render_2030(self, value):
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

def generate_report(request):
    '''
    Report / Query Generator
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
        
        
        
        #print(indicators_qs)

        #date_type=0 is data type for currency type
        currency_indicators = list(indicators_qs.filter(
            data_type=0).values_list("id", flat=True))

        export_format = request.GET.get('_export', None)

        indicators = request.GET.getlist('indicator_filter_field')
        ms = request.GET.getlist('memberstate_filter_field')

        years = request.GET.getlist('year_filter_field')
        
        
        if indicators == ['exchange_rate'] : 
            exchange_data = ExchangeRateData.objects.filter(submitted=True)
            #print(exchange_data)
            if ms and ms != ['all'] and 'all' not in ms:
                
                exchange_data = exchange_data.filter(currency__member_state__in=list(ms))
            if years and years != ['Select All'] and 'Select All' not in years:
                exchange_data = exchange_data.filter(reporting_year__in=years)
            else:
                exchange_data = exchange_data.filter(
                    reporting_year__in=get_published_years())
                
            pivot_table = pivot(exchange_data,
                                    ['currency__currency_label',
                                        'currency__member_state__member_state'],
                                    'reporting_year', 'exchange_rate', aggregation=Max)  # type: ignore
            print(pivot_table)
            for item in list(pivot_table):
                dict_values = list(item.keys())

            dict_values = dict_values[2:]
            print(dict_values)
            tbl = ExchangeRateDataTable('')

            for colname in dict_values:
                column = tables.Column(orderable=False, empty_values=None)

                tbl.base_columns[colname] = column  # type: ignore

            tbl = ExchangeRateDataTable(pivot_table)

            print(tbl)

            RequestConfig(request).configure(tbl)

            tbl.paginate(page=request.GET.get("page", 1), per_page=25)

            if TableExport.is_valid_format(export_format):

                time_now = datetime.now().strftime("%D_%H_%M")
                file_name = f"{time_now} - SADC ICT Observatory Data"

                exporter = TableExport(export_format, tbl)

                return exporter.response(f"{file_name}"'.{}'.format(export_format))
            context = {"table": tbl, "form": form, "currency_indicators": currency_indicators,
               "currency_data_type": currency_data_type}

            return render(request, "portal/generatereport.html", context=context)
            
            #return  HttpResponse("heya")
        elif 'exchange_rate' in indicators:
            indicators.pop(indicators.index('exchange_rate'))
            


       

        
       
             

        if indicators or ms or years:
            #return  HttpResponse("heya3")
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
                    reporting_year__in=get_published_years())

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
