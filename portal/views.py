

import signal
import os
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma

from django_tables2 import RequestConfig

from django.db.models import Avg, F, Max
from statistics import mean
from collections import namedtuple
from datetime import datetime
from django_tables2.export.export import TableExport
import django_tables2 as tables
import random
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from core.models import SystemUser
from core.views import Get_Reporting_Year
from portal.chartsdjsf import SummaryResponse
from portal.forms import FilterForm, HomePageFilterYear, latest_published_year
from portaldata.admin import ExchangeRateDataAdmin

from portaldata.models import ExchangeRateData, GeneralIndicatorData, Indicator, IndicatorData, INDICATORDATA_STATUS, MemberState, Chart, ChartConfig, CHART_TYPE
from django.template import loader
import json
from django.db.models import Count, Q
from django.shortcuts import render

from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
# from djf_surveys.mixin import ContextTitleMixin
from .charts import ColumnChart, LineChart, StackedChart, SpiderWebChart, SunBurstChart

from django_pivot.pivot import pivot

# Create your views here.

# COLORS = [
#     '#64748b', '#a1a1aa', '#374151', '#78716c', '#d6d3d1', '#fca5a5', '#ef4444', '#7f1d1d',
#     '#fb923c', '#c2410c', '#fcd34d', '#b45309', '#fde047', '#bef264', '#ca8a04', '#65a30d',
#     '#86efac', '#15803d', '#059669', '#a7f3d0', '#14b8a6', '#06b6d4', '#155e75', '#0ea5e9',
#     '#075985', '#3b82f6', '#1e3a8a', '#818cf8', '#a78bfa', '#a855f7', '#6b21a8', '#c026d3',
#     '#db2777', '#fda4af', '#e11d48', '#9f1239'
# ]

sadc_mobile_penetration = ''

sadc_network_coverage = ''

avg_pop_coverage_3g = ''

avg_internet_penetration = ''

total_population = ''

total_internet_users = ''


def index(request):

    # sadc_mobile_penetration = ''

    # t = pivotit()

    if settings.KILL_OS == 'True':
        os.kill(os.getpid(), signal.SIGINT)

    year = latest_published_year()

    # year = Get_Reporting_Year()

    # if request.user.is_authenticated:
    #     us = request.user.getSysUser()
    # print(us.user_organisation)

    form = HomePageFilterYear()

    if request.method == "GET":

        year_filter = request.GET.get('year_filter')
        if year_filter:
            year = year_filter
        # print(year_filter)

    # chartitContext = highchart()

    # ch = [chartitContext, "GNI per Capita"]

    # gni_gdp = chartGNIGDP(year)
    # #gni_gdp = chart_population(year)
    # gni_gdp_line = lineChartGNIGDP()
    # gni_gdp_stacked = stackedChartGNIGDP()
    # #gni_gdp_stacked = chart_telecom_revenue(year)
    # regulation_radar = spiderwebChartRegulations()
    # regulation_sunburst = SunBurstChartRegulation()

    # chart_pop_male_female = chart_population_male_female(year)

    # print(total_population)

    # if total_population and total_internet_users:
    #     try:
    #         avg_internet_penetration = round(
    #             float(total_internet_users)/float(total_population))
    #     except:
    #         avg_internet_penetration = 0

    # print(avg_internet_penetration)
    # print(sadc_network_coverage)

    charts = [
        #   chart_population(year),
        #   chart_population_male_female(year),
        #   chart_gpd_per_capita(year),
        #   chart_gni_per_capita(year),
        chart_telecom_revenue(year),
        chart_ict_contrib_gdp(year),
        chart_telecom_investment(year),


        chart_mobile_penetration_rate(year),
        chart_fixed_telephone_line(year),
        chart_pop_coveredby_mobl_network(year),
        chart_mobl_geog_coverage(year),
        chart_internet_user_penetration(year),


        chart_inter_internet_bandwidth(year),
        chart_inter_internet_bandwidth_per_user(year),
        chart_inter_internet_bandwidth_per_inhabitant(year),



        chart_fixed_telephone_tariffs(year),
        chart_sms_tariff(year),


        chart_existence_of_policy_by_ms(year),
        chart_existing_ict_regulation(year),


        # chart_exchange_rate(year),


        chart_literacy_rate(year),
    ]

    score_cards = {
        'sadc_mobile_penetration': sadc_mobile_penetration,
        'sadc_network_coverage': sadc_network_coverage,
        'avg_pop_coverage_3g': avg_pop_coverage_3g,
        'avg_internet_penetration': avg_internet_penetration}

    # ml = [multiple, "title"]
    # print(multiple)
    # form = HomePageFilterYear(request.GET)
    # print(form)
    context = {
        'form': form,
        # 'gni_gdp': gni_gdp,

        # 'gni': ch,
        # 'gni_gdp_line': gni_gdp_line,
        # 'gni_gdp_stacked': gni_gdp_stacked,
        # 'regulation_radar': regulation_radar,
        # 'regulation_sunburst': regulation_sunburst,
        'charts': charts,
        'score_cards': score_cards

    }
    settings.KILL_OS = 'False'
    # print(chartitContext)
    return render(request, 'portal/index.html', context=context)


def socio_economic(request):

    form = HomePageFilterYear(request.GET or None)

    year = latest_published_year()

    if request.method == "GET":
        year_filter = request.GET.get('year_filter')
        if year_filter:
            year = year_filter

    charts = [chart_population(year),
              chart_population_male_female(year),
              chart_gpd_per_capita(year),
              chart_gni_per_capita(year),

              chart_exchange_rate(year),
              ]

    # ml = [multiple, "title"]
    # print(multiple)
    # form = HomePageFilterYear(request.GET)
    # print(form)
    context = {
        'form': form,

        'charts': charts,


    }
    # print(chartitContext)
    return render(request, 'portal/socio-economic-charts.html', context=context)


def sum_val(data_dict, indicator_label):
    total = 0
    if data_dict:
        if indicator_label in data_dict:
            if data_dict[indicator_label]:
                for i in data_dict[indicator_label]:
                    if i != '':
                        total += float(i)

                # print(round(total))
                return round(total, 2)
            else:

                return 0
        else:

            return 0

        # return round(sum(d for d in data_dict[indicator_label] if d != ''), 2)
    else:

        return 0


def mean_val(data_dict, indicator_label):
    if data_dict:
        if indicator_label in data_dict:
            if data_dict[indicator_label]:
                return round(mean(d for d in data_dict[indicator_label] if d != ''), 2)
            else:
                return 0
        else:
            return 0
    else:
        return 0


def percentage_per_indicator(result_list):

    # percent = [(g + h + i+j+k+l+m+n) / 8 for g, h, i, j, k, l, m, n in
    #            zip(*infra)]
    if result_list:
        percent = [mean(k) for k in zip(*result_list)]

        return percent
    else:
        return 0


def perUser(bandwidth, internet_user):
    if internet_user and bandwidth:
        return round(float(bandwidth) / float(internet_user), 2)
    else:
        return ''


def chart_population(year):
    ''' This is for Population Chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(chart_name='chart_population').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_population_male_female(year):
    '''For the Population Male/Female '''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    main_stack_label = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_population_male_female').first()

    # print(chart)

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                if item.extra_calculation == 'mainstack':
                    main_stack_label = item.indicator.label

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

        if aggregation:

            if aggregation == 'sum':
                categories.append("SADC Total")

                # sum_val = sum(
                #     d for d in data_dict[indicator_label] if d != '')

                data_dict[indicator_label].append(
                    sum_val(data_dict, indicator_label))

            elif aggregation == 'avg':
                categories.append("SADC Average")

                # mean_val = mean(
                #     d for d in data_dict[indicator_label] if d != '')

                data_dict[indicator_label].append(
                    mean_val(data_dict, indicator_label))

    # print(data_dict)

    recieved = StackedChart(categories=categories, data_dict=data_dict,
                            chart_title=chart_title, y_axis_title=y_axis_title, year=year, stacking='percent', grouped_stack=main_stack_label)  # ,

    return recieved


def chart_gpd_per_capita(year):
    ''' This is for GDP per Capita Chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(chart_name='chart_gdp').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_gni_per_capita(year):
    ''' This is for GNI per Capita Chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(chart_name='chart_gni').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_telecom_revenue(year):
    '''For the Telecommunications Revenue'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''

    main_stack_label = ''

    data_dict = {}

    chart = Chart.objects.filter(chart_name='chart_telecom_revenue').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                '''Main Stack is the first column chart in the stacked charts that shows the Total Revenue'''
                if item.extra_calculation == 'mainstack':
                    main_stack_label = item.series_name if item.series_name else item.indicator.label

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)
        data_dict[indicator_label] = data

    recieved = StackedChart(categories=categories, data_dict=data_dict,
                            chart_title=chart_title, y_axis_title=y_axis_title, year=year,
                            stacking='normal', grouped_stack=main_stack_label, valign='bottom', floating=False)  # ,

    return recieved


def chart_internet_user_penetration(year):
    ''' This is for Internet User Penetration Chart'''

    categories = []

    query_list = []

    population_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_internet_user_penetration').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        population_indicator = ChartConfig.objects.filter(
            series_name="Population").first()

        population_indicator = population_indicator.indicator if population_indicator else 0

        if indicators_list:

            for item in indicators_list:

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                '''per100 canculates the Per 100 inhabitat with the value/population * 100'''
                if item.extra_calculation == 'per100':

                    qs = []
                    population = 0
                    for i in indicator_data:
                        if population_indicator:
                            # print(type(population_indicator))
                            try:
                                population = IndicatorData.objects.get(
                                    indicator=population_indicator, reporting_year=year, member_state=i.member_state).ind_value
                                population_list.append(
                                    population) if population not in population_list else population_list
                                if i.ind_value_adjusted and population:
                                    per100 = round((float(
                                        i.ind_value_adjusted) / float(population))*100, 2)

                                else:
                                    per100 = ''

                                i.ind_value_adjusted = str(per100)

                            except:
                                pass

                query_list.append(indicator_data)

    global total_population

    if population_list:
        total_population = round(sum(float(d)
                                 for d in population_list if d != ''), 2)

    global avg_internet_penetration

    if total_internet_users and total_population:
        try:
            avg_internet_penetration = round(float(
                total_internet_users)/float(total_population), 2)
        except:
            avg_internet_penetration = '-'

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

        if aggregation:
            '''if the chart requires aggregation of data across member states'''
            if aggregation == 'sum':
                categories.append("SADC Total")

                # sum_val = sum(
                #     d for d in data_dict[indicator_label] if d != '')

                data_dict[indicator_label].append(
                    sum_val(data_dict, indicator_label))
            elif aggregation == 'avg':
                categories.append("SADC Average")

                # mean_val = mean(
                #     d for d in data_dict[indicator_label] if d != '')

                data_dict[indicator_label].append(round(
                    mean_val(data_dict, indicator_label), 2))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year,
                             valign='bottom', floating=False, layout='horizontal',
                             width='120')

    return chart_html


def chart_telecom_investment(year):
    ''' This is for Telecommunications Investment Chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(chart_name='chart_telecom_investment').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_existing_ict_regulation(year):
    categories = []

    query_list = []

    spiderweb_data = []
    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_existing_ict_regulation').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    data_app = {}

    for qs in query_list:
        # print(qs)
        data = []
        # categories.append(entry.indicator.label)
        for entry in qs:
            # print(entry)

            # if entry.member_state.member_state_short_name:
            #     categories.append(entry.member_state.member_state_short_name)
            # else:
            #     categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted == 'Yes'):
                data.append(1)
            elif (entry.ind_value_adjusted == 'No'):
                data.append(0)
            else:
                data.append('')

        data_dict[indicator_label] = data

        # print(data_dict)

        if aggregation:
            '''if the chart requires aggregation of data across member states'''
            if aggregation == 'sum':
                categories.append("SADC Total")

                # sum_val = sum(
                #     d for d in data_dict[indicator_label] if d != '')
                data_dict[indicator_label].append(
                    sum_val(data_dict, indicator_label))

            elif aggregation == 'avg':
                categories.append("SADC Average")

                # mean_val = mean(
                #     d for d in data_dict[indicator_label] if d != '')

                data_dict[indicator_label].append(
                    mean_val(data_dict, indicator_label))

            elif aggregation == 'yesPercentage':
                categories.append(indicator_label)

                spiderweb_data.append(mean_val(
                    data_dict, indicator_label)*100)

    data_dict = {}

    data_dict['Existence of policy'] = spiderweb_data

    chart_html = SpiderWebChart(categories=categories, data_dict=data_dict,
                                chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_existence_of_policy_by_ms(year):
    categories = []

    query_list = []

    spiderweb_data = []
    indicator_label = ''

    label = 'ICT policies'

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_existence_of_policy_by_ms').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    data_app = {}

    for qs in query_list:
        # print(qs)
        data = []
        # categories.append(entry.indicator.label)
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(
                    entry.member_state.member_state_short_name) if entry.member_state.member_state_short_name not in categories else categories
            else:
                categories.append(
                    entry.member_state.member_state) if entry.member_state.member_state not in categories else categories

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted == 'Yes'):
                data.append(1)
            elif (entry.ind_value_adjusted == 'No'):
                data.append(0)
            else:
                data.append(0)

        data_dict[indicator_label] = data

    result_list = [[i for i in data_dict[x]] for x in data_dict.keys()]

    data_app[label] = percentage_per_indicator(result_list)

    # for k, v in data_dict[indicator_label].items:
    #     print(k)

    # data_app['label'] = list(map(lambda x: mean_val))

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_app[label].append(
                mean_val(data_app, label))

    # data_dict = {}

    # data_dict['Existence of policy by Member State'] = spiderweb_data

    chart_html = ColumnChart(categories=categories, data_dict=data_app,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year, round='2')

    return chart_html


def chart_mobile_penetration_rate(year):
    ''' This is for Mobile Penetration Rate in the SADC region'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_mobile_penetration_rate').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

            global sadc_mobile_penetration

            sadc_mobile_penetration = mean_val(data_dict, indicator_label)

            # sadc_mobile_penetration()

            # print(sadc_mobile_penetration)

    chart_html = LineChart(categories=categories, data_dict=data_dict,
                           chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_fixed_telephone_line(year):
    ''' This is for Mobile Penetration Rate in the SADC region'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_fixed_telephone_line').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_pop_coveredby_mobl_network(year):
    ''' This is for Mobile Penetration Rate in the SADC region'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_pop_coveredby_mobl_network').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if 'Percentage of population covered by at least a 3G mobile network' in data_dict:

        pop_coverage_3g = data_dict['Percentage of population covered by at least a 3G mobile network']

        global avg_pop_coverage_3g

        avg_pop_coverage_3g = round(
            mean(d for d in pop_coverage_3g if d != ''), )

    # print(
    #     data_dict['Percentage of population covered by at least a 3G mobile network'])

    # # print(
    # #     data_dict.get('Percentage of population covered by at least a 3G mobile network'))

    # avg_pop_coverage_3g = mean_val(
    #     data_dict, indicator_label)
    # print(indicator_label)
    # print(avg_pop_coverage_3g)

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title,
                             year=year)

    return chart_html


def chart_mobl_geog_coverage(year):
    ''' This is for Mobile Penetration Rate in the SADC region'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_mobl_geog_coverage').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

        global sadc_network_coverage

        sadc_network_coverage = round(mean_val(data_dict, indicator_label),)
        # print(sadc_network_coverage)

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_inter_internet_bandwidth(year):
    ''' This is for International Internet Bandwidth (Mbits/s)'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_inter_internet_bandwidth').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_inter_internet_bandwidth_per_inhabitant(year):
    ''' This is for International Internet Bandwidth Per Inhabitant (kbit/s)'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_inter_internet_bandwidth_per_inhabitant').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_inter_internet_bandwidth_per_user(year):
    ''' This is for International Internet Bandwidth Per Internet User (kbit/s)'''

    categories = []
    categories_single = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_inter_internet_bandwidth_per_user').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                if item.extra_calculation == 'mtokbits':

                    qs = []

                    for i in indicator_data:
                        try:

                            if i.ind_value_adjusted:
                                kbits = round((float(
                                    i.ind_value_adjusted) * 1000), 2)

                            else:
                                kbits = ''

                            i.ind_value_adjusted = str(kbits)

                        except:
                            pass

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:

            if entry.member_state.member_state_short_name:
                categories.append(
                    entry.member_state.member_state_short_name) if entry.member_state.member_state_short_name not in categories else categories
            else:
                categories.append(
                    entry.member_state.member_state) if entry.member_state.member_state not in categories else categories

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            # print(chart_indicator.series_name)  # type: ignore
            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if indicator_label != 'Total Internet Subscribers':
                indicator_label = 'International Internet Bandwidth'

            # print(indicator_label)

            # print(indicator_label)
            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    # print(data_dict)

    # print(data_dict['International Internet Bandwidth'])
    # print(data_dict['Total Internet Subscribers'])

    data_calc = {}

    label = 'internet users'

    if 'International Internet Bandwidth' in data_dict and 'Total Internet Subscribers' in data_dict:
        data_calc[label] = list(map(
            perUser, data_dict['International Internet Bandwidth'], data_dict['Total Internet Subscribers']))

    # print(data_calc)

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':

            categories.append("SADC Average")  # type: ignore

            # print(categories_single)
            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            # data_dict[indicator_label].append(
            #     mean_val(data_dict, indicator_label))

            total_bandwidth = sum_val(
                data_dict, 'International Internet Bandwidth')

            total_users = sum_val(
                data_dict, 'Total Internet Subscribers')

            global total_internet_users
            global avg_internet_penetration

            total_internet_users = total_users

            if total_internet_users and total_population:
                try:
                    avg_internet_penetration = round(float(
                        total_internet_users)/float(total_population), 2)
                except:
                    avg_internet_penetration = '-'

            # print(total_bandwidth)
            # print(total_users)

            if total_bandwidth and total_users:

                data_calc[label].append(round(total_bandwidth/total_users, 2))

    general_indicator_data = GeneralIndicatorData.objects.filter(
        general_indicator__include_in_chart=chart, reporting_year=year)

    if general_indicator_data:
        for item in general_indicator_data:
            try:
                data_calc[label].append(round(float(item.indicator_value), 2))
                new_category = item.general_indicator.series_name if item.general_indicator.series_name else item.general_indicator.indicator_label

                categories.append(new_category)

            except:
                pass

    chart_html = ColumnChart(categories=categories, data_dict=data_calc,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_fixed_telephone_tariffs(year):
    ''' This is for Fixed Telephone Tariffs'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_fixed_telephone_tariffs').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

        if aggregation:
            '''if the chart requires aggregation of data across member states'''
            if aggregation == 'sum':
                categories.append("SADC Total")

                # sum_val = sum(
                #     d for d in data_dict[indicator_label] if d != '')
                data_dict[indicator_label].append(
                    sum_val(data_dict, indicator_label))

            elif aggregation == 'avg':
                categories.append("SADC Average")

                # mean_val = mean(
                #     d for d in data_dict[indicator_label] if d != '')

                data_dict[indicator_label].append(
                    mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year, round='3')

    return chart_html


def chart_sms_tariff(year):
    ''' This is for Mobile Cellular SMS Tariff '''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_sms_tariff').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year, round='3')

    return chart_html


def chart_literacy_rate(year):
    ''' This is for Literacy Rate '''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_literacy_rate').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.member_state.member_state_short_name:
                categories.append(entry.member_state.member_state_short_name)
            else:
                categories.append(entry.member_state.member_state)

            chart_indicator = ChartConfig.objects.filter(
                indicator=entry.indicator).first()

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year, round='0')

    return chart_html


def chart_ict_contrib_gdp(year):
    ''' This is for ICT Contribution to GDP (%) '''
    categories = []

    query_list = []

    spiderweb_data = []
    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_ict_contrib_gdp').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # print(type(indicator.indicator))

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

        for qs in query_list:
            # print(qs)
            data = []
            # categories.append(entry.indicator.label)
            for entry in qs:
                # print(entry)

                if entry.member_state.member_state_short_name:
                    categories.append(
                        entry.member_state.member_state_short_name)
                else:
                    categories.append(entry.member_state.member_state)

                chart_indicator = ChartConfig.objects.filter(
                    indicator=entry.indicator).first()

                indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

                if (entry.ind_value_adjusted):
                    data.append(float(entry.ind_value_adjusted))
                else:
                    data.append(entry.ind_value_adjusted)

            data_dict[indicator_label] = data
            # print(categories)

            # print(data_dict)

        # print(data_dict)

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

        elif aggregation == 'yesPercentage':
            categories.append(indicator_label)

            spiderweb_data.append(mean_val(
                data_dict, indicator_label)*100)

    # print(data_dict[indicator_label])

    '''
#     Here, zip function is used to create a list of X,Y data
#     '''

    data_dict = dict(zip(categories, data_dict[indicator_label]))

    # data_dict = {}

    # data_dict['Existence of policy'] = spiderweb_data

    chart_html = SunBurstChart(categories=categories, data_dict=data_dict,
                               chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_exchange_rate(year):
    ''' This is for Exchange Rate '''

    categories = []

    query_list = []

    indicator_label = 'Exchange Rate'

    chart_title = 'Exchange Rate (Local Currency to USD)'
    y_axis_title = 'USD'
    aggregation = 'avg'

    data_dict = {}

    exchange_rate_queryset = ExchangeRateData.objects.filter(
        reporting_year=year)

    query_list.append(exchange_rate_queryset)

    for qs in query_list:
        data = []
        for entry in qs:
            # print(entry)

            if entry.currency.member_state.member_state_short_name:
                categories.append(
                    entry.currency.member_state.member_state_short_name)
            else:
                categories.append(entry.currency.member_state.member_state)

            # chart_indicator = ChartConfig.objects.filter(
            #     indicator=entry.indicator).first()

            # indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if (entry.exchange_rate):
                data.append(1/float(entry.exchange_rate))
            else:
                data.append('')

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            # sum_val = sum(
            #     d for d in data_dict[indicator_label] if d != '')
            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # mean_val = mean(
            #     d for d in data_dict[indicator_label] if d != '')

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year, round='3')

    return chart_html


'''
Report / Query Generator
'''


# class MyTable(tables.Table):
#     member_state__member_state = tables.Column()
#     indicator__label = tables.Column()
#     # order_by=("member_state__member_state"))

#     class Meta:
#         sequence = ("member_state__member_state",
#                     "indicator__label", "...")
#         attrs = {
#             "class": "table table-striped table-bordered dt-responsive compact nowrap"}
#         paginator_class = tables.LazyPaginator
#         empty_text = 'Query did not return any results. Please refine your search.'


class IndicatorDataTable(tables.Table):

    member_state__member_state = tables.Column()
    indicator__label = tables.Column()
    # order_by=("member_state__member_state"))

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


def generate_report(request):
    '''
    Here, first implement the filter


    '''

    years_qs = list(IndicatorData.objects.values_list(
        'reporting_year', flat=True).distinct())

    form = FilterForm(request.GET or None)

    # tbl = IndicatorDataTable('')

    context = {}

    dict_values = []

    # tbl = ''

    pivot_table = None

    if request.method == "GET":
        # ind_data = IndicatorData()

        export_format = request.GET.get('_export', None)

        indicators = request.GET.getlist('indicator_filter_field')
        ms = request.GET.getlist('memberstate_filter_field')
        years = request.GET.getlist('year_filter_field')

        if indicators or ms or years:

            # ind_data = IndicatorData.objects.filter(validation_status=INDICATORDATA_STATUS.validated
            #                                         ).values_list('indicator', 'member_state', 'reporting_year', 'ind_value_adjusted').order_by(
            #     'member_state__member_state', 'indicator')
            ind_data = IndicatorData.objects.filter(validation_status=INDICATORDATA_STATUS.validated).order_by(
                'member_state__member_state', 'indicator')

            if ms:
                ind_data = ind_data.filter(member_state__in=list(ms))

            if indicators:
                ind_data = ind_data.filter(indicator__in=list(indicators))

            if years:
                ind_data = ind_data.filter(reporting_year__in=years)

            # print(ind_data)

            pivot_table = pivot(ind_data,
                                ['indicator__label', 'member_state__member_state'],
                                'reporting_year', 'ind_value_adjusted', aggregation=Max)  # type: ignore

            # print(pivot_table)

            # for record in pivot_table:
            #     print(record)

            for item in list(pivot_table):
                dict_values = list(item.keys())

            dict_values = dict_values[2:]

            # tbl = IndicatorDataTable('')

            # cols = [(k, tables.Column()) for k, v in pivot_table[0].items()]

            # tbl = IndicatorDataTable(
            #     data=pivot_table, extra_columns=cols, orderable=False)

            tbl = IndicatorDataTable('')

            for colname in dict_values:
                column = tables.Column(orderable=False, empty_values=None)

                # type: ignore
                tbl.base_columns[colname] = column

            # for i in tbl.columns:
            #     print(i)

            tbl = IndicatorDataTable(pivot_table)

            RequestConfig(request).configure(tbl)

            tbl.paginate(page=request.GET.get("page", 1), per_page=25)

            if TableExport.is_valid_format(export_format):

                time_now = datetime.now().strftime("%D_%H_%M")
                file_name = f"{time_now} - SADC ICT Observatory Data"
                # table = [[your table object]]
                exporter = TableExport(export_format, tbl)

                return exporter.response(f"{file_name}"'.{}'.format(export_format))
        else:
            tbl = None

            pivot_table = None
            # IndicatorDataTable = IndicatorDataTable('')

    context = {"table": tbl, "form": form}

    return render(request, "portal/generatereport.html", context=context)


# def chartGNIGDP(year):

#     year = '2021'

#     categories = []

#     indicator_label = ''

#     chart_title = ''

#     data_dict = {}

#     gnipercapita_queryset = IndicatorData.objects.filter(
#         indicator_id=2, reporting_year=year)

#     gdppercapita_queryset = IndicatorData.objects.filter(
#         indicator_id=1, reporting_year=year)

#     query_list = [gnipercapita_queryset, gdppercapita_queryset]

#     for qs in query_list:
#         data = []
#         for entry in qs:
#             if entry.member_state.member_state_short_name:
#                 categories.append(entry.member_state.member_state_short_name)
#             else:
#                 categories.append(entry.member_state.member_state)

#             indicator_label = entry.indicator.label

#             if (entry.ind_value_adjusted):
#                 data.append(float(entry.ind_value_adjusted))
#             else:
#                 data.append(entry.ind_value_adjusted)
#         data_dict[indicator_label] = data

#     chart_title = 'GNI and GDP'
#     y_axis_title = 'USD'

#     recieved = ColumnChart(categories=categories, data_dict=data_dict,
#                            chart_title=chart_title, y_axis_title=y_axis_title, year=year)

#     return recieved


# def lineChartGNIGDP():

#     categories = []

#     indicator_label = ''

#     chart_title = ''

#     data_dict = {}

#     gnipercapita_queryset = IndicatorData.objects.filter(indicator_id=2)
#     gdppercapita_queryset = IndicatorData.objects.filter(indicator_id=1)
#     query_list = [gnipercapita_queryset, gdppercapita_queryset]

#     for qs in query_list:
#         data = []
#         for entry in qs:
#             if entry.member_state.member_state_short_name:
#                 categories.append(entry.member_state.member_state_short_name)
#             else:
#                 categories.append(entry.member_state.member_state)

#             indicator_label = entry.indicator.label

#             if (entry.ind_value_adjusted):
#                 data.append(float(entry.ind_value_adjusted))
#             else:
#                 data.append(entry.ind_value_adjusted)
#         data_dict[indicator_label] = data

#     chart_title = 'GNI and GDP Line'
#     y_axis_title = 'USD'

#     recieved = LineChart(categories=categories, data_dict=data_dict,
#                          chart_title=chart_title, y_axis_title=y_axis_title, year='2022')

#     return recieved


# def stackedChartGNIGDP():

#     categories = []

#     indicator_label = ''

#     chart_title = ''

#     data_dict = {}

#     gnipercapita_queryset = IndicatorData.objects.filter(indicator_id=2)
#     gdppercapita_queryset = IndicatorData.objects.filter(indicator_id=1)
#     query_list = [gnipercapita_queryset, gdppercapita_queryset]

#     for qs in query_list:
#         data = []
#         for entry in qs:
#             if entry.member_state.member_state_short_name:
#                 categories.append(entry.member_state.member_state_short_name)
#             else:
#                 categories.append(entry.member_state.member_state)

#             indicator_label = entry.indicator.label

#             if (entry.ind_value_adjusted):
#                 data.append(float(entry.ind_value_adjusted))
#             else:
#                 data.append(entry.ind_value_adjusted)
#         data_dict[indicator_label] = data

#     chart_title = 'GNI and GDP Stacked'
#     y_axis_title = 'USD'

#     recieved = StackedChart(categories=categories, data_dict=data_dict,
#                             chart_title=chart_title, y_axis_title=y_axis_title, year='2022')

#     return recieved


# def spiderwebChartRegulations():

#     categories = []

#     indicator_label = ''

#     chart_title = ''

#     data_dict = {}

#     # gnipercapita_queryset = IndicatorData.objects.filter(indicator_id=2)
#     # gdppercapita_queryset = IndicatorData.objects.filter(indicator_id=1)
#     # query_list = [gnipercapita_queryset, gdppercapita_queryset]

#     # for qs in query_list:
#     #     data = []
#     #     for entry in qs:
#     #         categories.append(entry.member_state.member_state)
#     #         indicator_label = entry.indicator.label

#     #         if (entry.ind_value):
#     #             data.append(float(entry.ind_value))
#     #         else:
#     #             data.append(entry.ind_value)
#     #     data_dict[indicator_label] = data

#     categories = ['Infrastructure Sharing', 'Universal Access', 'Precence of Internet Exchange(IEP)',
#                   'Competion in Local Loop Telecoms', 'Competetion in ISP Market', 'Policy in Broadband', 'Presence of Cyber Security Laws', 'Presence of National CIRT']

#     data = [75, 75, 56.25, 43.75, 65.50, 50, 43.75, 43.75]
#     data_dict['Existence of policy'] = data

#     print(data_dict)

#     chart_title = 'AVERAGE EXISTENCE OF RELEVANT ICT POLICY REGULATION GUIDELINE INSTITUTIONAL STRUCTURE ACROSS THE SADC REGION'
#     y_axis_title = 'USD'

#     recieved = SpiderWebChart(categories=categories, data_dict=data_dict,
#                               chart_title=chart_title, y_axis_title=y_axis_title, year='2022')

#     return recieved


# def SunBurstChartRegulation():

#     categories = []

#     indicator_label = ''

#     chart_title = ''

#     data_dict = {}

#     # gnipercapita_queryset = IndicatorData.objects.filter(indicator_id=2)
#     # gdppercapita_queryset = IndicatorData.objects.filter(indicator_id=1)
#     # query_list = [gnipercapita_queryset, gdppercapita_queryset]

#     # for qs in query_list:
#     #     data = []
#     #     for entry in qs:
#     #         categories.append(entry.member_state.member_state)
#     #         indicator_label = entry.indicator.label

#     #         if (entry.ind_value):
#     #             data.append(float(entry.ind_value))
#     #         else:
#     #             data.append(entry.ind_value)
#     #     data_dict[indicator_label] = data

#     categories = ['Infrastructure Sharing', 'Universal Access', 'Presence of Internet Exchange(IEP)',
#                   'Competion in Local Loop Telecoms', 'Competetion in ISP Market', 'Policy in Broadband', 'Presence of Cyber Security Laws', 'Presence of National CIRT']

#     data = [75, 75, 56.25, 43.75, 65.50, 50, 43.75, 43.75]

#     '''
#     Here, zip function is used to create a list of X,Y data
#     '''

#     data_dict = dict(zip(categories, data))

#     chart_title = 'AVERAGE EXISTENCE OF RELEVANT ICT POLICY REGULATION'
#     y_axis_title = 'USD'

#     recieved = SunBurstChart(categories=categories, data_dict=data_dict,
#                              chart_title=chart_title, y_axis_title=y_axis_title, year='2022')

#     return recieved

# def bar_chart(request):

#     labels = []
#     data = []

#     queryset = IndicatorData.objects.filter(indicator_id=2)
#     for entry in queryset:
#         labels.append(entry.member_state.member_state)
#         data.append(entry.ind_value)

#     context = {
#         'labels': labels,
#         'data': data,
#     }

#     return render(request, 'portal/chart.html', context=context)


# def plotchart(request):
#     print("here")
#     chart = bar_chart(request)
#     context = {'thischart': chart}
#     return render(request, 'portal/index.html', context=context)

    # return JsonResponse(data={
    #     'labels': labels,
    #     'data': data,
    # })


# PALETTE = ['#465b65', '#184c9c', '#d33035', '#ffc107', '#28a745', '#6f7f8c',
#            '#6610f2', '#6e9fa5', '#fd7e14', '#e83e8c', '#17a2b8', '#6f42c1']


# def chartIt():

#     thislabels = []
#     data = []
#     indicator_label = ''

#     queryset = IndicatorData.objects.filter(indicator_id=2)
#     query_list = list(queryset)
#     # print(query_list.__getitem__)

#     for entry in queryset:
#         thislabels.append(entry.member_state.member_state)
#         indicator_label = entry.indicator.label
#         # if entry.ind_value.isnumeric() == True:
#         #     x = int(entry.ind_value)
#         #     print(type(x))
#         data.append(entry.ind_value)

#         # create a charts context to hold all of the charts
#     # context = {}

#     # every chart is added the same way so I will just document the first one
#     # create a chart object with a unique chart_id and color palette
#     # if not chart_id or color palette is provided these will be randomly generated
#     # the type of charts does need to be identified here and might iffer from the chartjs type
#     city_payment_bar = Chart(
#         'bar', chart_id='city_payment_bar', palette=PALETTE)
#     # create a pandas pivot_table based on the fields and aggregation we want
#     # stacks are used for either grouping or stacking a certain column
#     # city_payment_radar.from_df(df, values='total', stacks=[
#     #                            'payment'], labels=['city'])
#     # print(len([data]))
#     # print(len(thislabels))
#     city_payment_bar.from_lists(
#         values=data, labels=thislabels, stacks=[indicator_label])
#     # add the presentation of the chart to the charts context
#     # print(city_payment_bar.get_presentation())
#     html_str = []
#     html_str.append(city_payment_bar.get_presentation())
#     # print(html_str)
#     #    .append(city_payment_bar.get_presentation())
#     return " ".join(html_str)


# class Dashboard(TemplateView):
#     template_name = 'portal/dashboard.html'

#     def get_context_data(self, **kwargs):

#         # get the data from the default method
#         context = super().get_context_data(**kwargs)

#         # the fields we will use
#         # df_fields = ['city', 'customer_type', 'gender', 'unit_price', 'quantity',
#         #     'product_line', 'tax', 'total' , 'date', 'time', 'payment',
#         #     'cogs', 'profit', 'rating']

#         # fields to exclude
#         # df_exclude = ['id', 'cogs']

#         # create a datframe with all the records.  chart.js doesn't deal well
#         # with dates in all situations so our method will convert them to strings
#         # however we will need to identify the date columns and the format we want.
#         # I am useing just month and year here.
#         # df = objects_to_df(Purchase, date_cols=['%Y-%m', 'date'])

#         thislabels = []
#         data = []
#         indicator_label = ''

#         queryset = IndicatorData.objects.filter(indicator_id=2)
#         query_list = list(queryset)
#         # print(query_list.__getitem__)

#         for entry in queryset:
#             thislabels.append(entry.member_state.member_state)
#             indicator_label = entry.indicator.label
#             # if entry.ind_value.isnumeric() == True:
#             #     x = int(entry.ind_value)
#             #     print(type(x))
#             data.append(entry.ind_value)

#             # create a charts context to hold all of the charts
#         context['charts'] = []

#         # every chart is added the same way so I will just document the first one
#         # create a chart object with a unique chart_id and color palette
#         # if not chart_id or color palette is provided these will be randomly generated
#         # the type of charts does need to be identified here and might iffer from the chartjs type
#         city_payment_bar = Chart(
#             'bar', chart_id='city_payment_bar', palette=PALETTE)
#         # create a pandas pivot_table based on the fields and aggregation we want
#         # stacks are used for either grouping or stacking a certain column
#         # city_payment_radar.from_df(df, values='total', stacks=[
#         #                            'payment'], labels=['city'])
#         # print(len([data]))
#         # print(len(thislabels))
#         city_payment_bar.from_lists(
#             values=data, labels=thislabels, stacks=[indicator_label])
#         # add the presentation of the chart to the charts context
#         context['charts'].append(city_payment_bar.get_presentation())

#         # exp_polar = Chart('polarArea', chart_id='polar01', palette=PALETTE)
#         # exp_polar.from_df(df, values='total', labels=['payment'])
#         # context['charts'].append(exp_polar.get_presentation())

#         # exp_doughnut = Chart(
#         #     'doughnut', chart_id='doughnut01', palette=PALETTE)
#         # exp_doughnut.from_df(df, values='total', labels=['city'])
#         # context['charts'].append(exp_doughnut.get_presentation())

#         # exp_bar = Chart('bar', chart_id='bar01', palette=PALETTE)
#         # exp_bar.from_df(df, values='total', labels=['city'])
#         # context['charts'].append(exp_bar.get_presentation())

#         # city_payment = Chart(
#         #     'groupedBar', chart_id='city_payment', palette=PALETTE)
#         # city_payment.from_df(df, values='total', stacks=[
#         #                      'payment'], labels=['date'])
#         # context['charts'].append(city_payment.get_presentation())

#         # city_payment_h = Chart(
#         #     'horizontalBar', chart_id='city_payment_h', palette=PALETTE)
#         # city_payment_h.from_df(df, values='total', stacks=[
#         #                        'payment'], labels=['city'])
#         # context['charts'].append(city_payment_h.get_presentation())

#         # city_gender_h = Chart('stackedHorizontalBar',
#         #                       chart_id='city_gender_h', palette=PALETTE)
#         # city_gender_h.from_df(df, values='total', stacks=[
#         #                       'gender'], labels=['city'])
#         # context['charts'].append(city_gender_h.get_presentation())

#         # city_gender = Chart(
#         #     'stackedBar', chart_id='city_gender', palette=PALETTE)
#         # city_gender.from_df(df, values='total', stacks=[
#         #                     'gender'], labels=['city'])
#         # context['charts'].append(city_gender.get_presentation())

#         return context


# class SummaryResponseSurveyView(DetailView):
#     model = Indicator
#     template_name = "portal/summary.html"
#     title_page = 'Summary'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         indicator = Indicator.objects.get(pk=2)
#         summary = SummaryResponse(indicator=indicator)  # self.get_object())
#         context['summary'] = summary
#         # print(summary.generate)
#         return context

    # template_name = "django_tables2/bootstrap-responsive.html"


# def highchart():

#     thislabels = []
#     data = []
#     indicator_label = ''

#     gnipercapita_queryset = IndicatorData.objects.filter(indicator_id=2)

#     query_list = list(gnipercapita_queryset)
#     # print(query_list.__getitem__)

#     for entry in gnipercapita_queryset:
#         if entry.member_state.member_state_short_name:
#             thislabels.append(entry.member_state.member_state_short_name)
#         else:
#             thislabels.append(entry.member_state.member_state)
#         indicator_label = entry.indicator.label

#         if (entry.ind_value_adjusted):
#             data.append(float(entry.ind_value_adjusted))
#         else:
#             data.append(entry.ind_value_adjusted)

#     # dataset = Passenger.objects \
#     #     .values('ticket_class') \
#     #     .annotate(survived_count=Count('ticket_class', filter=Q(survived=True)),
#     #               not_survived_count=Count('ticket_class', filter=Q(survived=False))) \
#     #     .order_by('ticket_class')

#     categories = thislabels
#     # survived_series_data = data

#     survived_series = {
#         'name': indicator_label,
#         'data': data,
#         'showInLegend': False,
#     }

#     chart = {

#         'chart': {'renderTo': 'container', 'type': 'column', 'styledMode': 'true', },
#         'title': {'text': 'Titanic Survivors by Ticket Class'},
#         'xAxis': {'categories': categories, 'labels': {'textOverflow': 'none'}},
#         'plotOptions': {'series': {'dataLabels': {'enabled': 'false', 'rotation': 270, 'y': -20,   'crop': 'false', 'overflow': 'none'}}},
#         'title': {'text': indicator_label},
#         'yAxis': {'title': {'text': 'USD'}, 'labels': {'overflow': 'wrap'}},
#         'credits': {'enabled': False},

#         'series': [survived_series]
#     }

#     dump = json.dumps(chart)

#     container = indicator_label.replace(' ', '')+'_container'
#     script = f'''
#     <div id="{container}" class="text-primary chart-area" >
#     <script>
#     Highcharts.chart('{container}', { dump });
#     </script>
#     </div>
#     '''

#     # print(script)
#     return script

#     return render(request, 'portal/highchart.html', {'chart': dump})
