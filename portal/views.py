

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma

from django_tables2 import RequestConfig

from django.db.models import Max
from statistics import mean
from datetime import datetime
from django_tables2.export.export import TableExport
import django_tables2 as tables

from django.shortcuts import render
from portal.forms import FilterForm, HomePageFilterYear, get_published_years, latest_published_year


from portaldata.models import ExchangeRateData, GeneralIndicatorData, Indicator, IndicatorData, INDICATORDATA_STATUS, MemberState, Chart, ChartConfig, CHART_TYPE, Published, ScoreCard, ScoreCardConfig


from django.shortcuts import render

from .charts import ColumnChart, LineChart, StackedChart, SpiderWebChart, SunBurstChart

from django_pivot.pivot import pivot

color_blue = ['#2C318A']
color_green = ['#02B052']
color_yellow = ['#C49801']
color_lightblue = ['#3A40B8']
color_lightgreen = ['#02CE5E']

color_lightblue_lightgreen = [color_lightblue[0], color_lightgreen[0]]

tricolors = [color_blue[0], color_green[0], color_yellow[0]]
sixcolors = ['#2C318A', '#02B052',  '#C49801',
             '#BFDB38', '#3C84AB',   '#493801']


'''
Global variables used to populate score cards in the home page
'''
#sadc_mobile_penetration = ''

sadc_network_coverage = ''

avg_pop_coverage_3g = ''

avg_internet_penetration = ''

total_population = ''

total_internet_users = ''


def index(request):
    '''
    Main home page
    This view renders all the charts and score cards in the home page
    '''

    form = HomePageFilterYear(request.GET or None)

    year = latest_published_year()

    if request.method == "GET":

        year_filter = request.GET.get('year_filter')
        if year_filter:
            year = year_filter

    charts = [

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





        chart_literacy_rate(year),
    ]

    score_cards = {
        'sadc_mobile_penetration': scorecard_sadc_mobile_penetration(year),
        'sadc_network_coverage': sadc_network_coverage,
        'avg_pop_coverage_3g': avg_pop_coverage_3g,
        'avg_internet_penetration': scorecard_avg_internet_penetration(year)}

    context = {
        'form': form,
        'charts': charts,
        'score_cards': score_cards

    }
    return render(request, 'portal/index.html', context=context)


def about(request):

    return render(request, 'portal/about.html')


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

    context = {
        'form': form,

        'charts': charts,


    }

    return render(request, 'portal/socio-economic-charts.html', context=context)


def sum_val(data_dict, indicator_label):
    total = 0
    if data_dict:
        if indicator_label in data_dict:
            if data_dict[indicator_label]:
                for i in data_dict[indicator_label]:
                    if i != '':
                        total += float(i)

                return round(total, 2)
            else:

                return 0
        else:

            return 0

    else:

        return 0


def mean_val(data_dict, indicator_label):
    if data_dict:
        if indicator_label in data_dict:
            if data_dict[indicator_label]:
                try:
                    return round(mean(d for d in data_dict[indicator_label] if d != ''), 2)
                except:
                    return 0
            else:
                return 0
        else:
            return 0
    else:
        return 0


def percentage_per_indicator(result_list):

    if result_list:
        percent = [mean(k)*100 for k in zip(*result_list)]

        return percent
    else:
        return 0


def perUser(bandwidth, internet_user):
    if internet_user and bandwidth:
        return round(float(bandwidth) / float(internet_user), 2)
    else:
        return ''


def scorecard_sadc_mobile_penetration(year):
    "This is for the Average SADC Mobile Penetration Scorecard"

    scorecard = ScoreCard.objects.filter(
        scorecard_name='sadc_mobile_penetration').first()

    if scorecard:

        return scorecard_calculation(scorecard, year)
    else:
        return "-"


def scorecard_avg_internet_penetration(year):
    "This is for the Average SADC Internet Penetration Scorecard"

    scorecard = ScoreCard.objects.filter(
        scorecard_name='avg_internet_penetration').first()

    if scorecard:

        return scorecard_calculation(scorecard, year)
    else:
        return "-"


def scorecard_calculation(scorecard, year):
    query_list_num = []
    query_list_denom = []

    query_list = []

    indicators_list = ScoreCardConfig.objects.filter(scorecard=scorecard)

    if indicators_list:

        for item in indicators_list:

            item_option = item.indicator.label

            indicator_data = list(IndicatorData.objects.filter(
                indicator=item.indicator, reporting_year=year).values_list("ind_value_adjusted", flat=True))

            if item.num_denom:
                if item.num_denom == 'num':
                    item_option = "num"
                    query_list_num.append(indicator_data)
                elif item.num_denom == 'denom':
                    item_option = "denom"
                    query_list_denom.append(indicator_data)
                else:
                    #item_option = "other"
                    query_list.append(indicator_data)
            else:
                query_list.append(indicator_data)

    query_list_num = (query_list_num[0]
                      if query_list_num else query_list_num)
    query_list_denom = (
        query_list_denom[0] if query_list_denom else query_list_denom)

    num = 0
    denom = 0

    if len(query_list_num) == len(query_list_denom):

        for i in range(len(query_list_num)):
            if query_list_num[i] and query_list_denom[i]:

                try:
                    num += float(query_list_num[i])
                    denom += float(query_list_denom[i])
                except ValueError:
                    pass
    else:
        if query_list_num:
            if any(isinstance(el, list) for el in query_list_num):
                ls = [item for sublist in query_list_num for item in sublist]

                for item in ls:
                    try:
                        num += float(item)
                    except ValueError:
                        pass
            else:
                for item in query_list_num:
                    try:
                        num += float(item)
                    except ValueError:
                        pass

        if query_list_denom:
            if any(isinstance(el, list) for el in query_list_denom):
                ls = [item for sublist in query_list_denom for item in sublist]

                for item in ls:
                    try:
                        denom += float(item)
                    except ValueError:
                        pass
            else:
                for item in query_list_denom:
                    try:
                        denom += float(item)
                    except ValueError:
                        pass

    try:
        return (num/denom)*100
    except:
        return "-"

    # return True


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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

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

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

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

                data_dict[indicator_label].append(
                    sum_val(data_dict, indicator_label))

            elif aggregation == 'avg':
                categories.append("SADC Average")

                data_dict[indicator_label].append(
                    mean_val(data_dict, indicator_label))

    recieved = StackedChart(categories=categories,
                            data_dict=data_dict,
                            chart_title=chart_title,
                            y_axis_title=y_axis_title,
                            year=year, stacking='percent',
                            grouped_stack=main_stack_label,
                            chart_color=color_lightblue_lightgreen)  # ,

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_telecom_revenue(year):
    '''For the Telecommunications Revenue Chart'''

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

    # global total_population

    # if population_list:
    #     total_population = round(sum(float(d)
    #                              for d in population_list if d != ''), 2)

    # global avg_internet_penetration

    # if total_internet_users and total_population:
    #     try:
    #         avg_internet_penetration = round(float(
    #             total_internet_users)/float(total_population), 2)
    #     except:
    #         avg_internet_penetration = '-'

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
            '''if the chart requires aggregation of data across member states'''
            if aggregation == 'sum':
                categories.append("SADC Total")

                data_dict[indicator_label].append(
                    sum_val(data_dict, indicator_label))
            elif aggregation == 'avg':
                categories.append("SADC Average")

                data_dict[indicator_label].append(round(
                    mean_val(data_dict, indicator_label), 2))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year,
                             valign='bottom', floating=False, layout='horizontal',
                             width='120', chart_color=sixcolors)

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title,
                             year=year, chart_color=tricolors)

    return chart_html


def chart_existing_ict_regulation(year):
    ''' This is for Existing ICT regulation Spiderweb Chart'''

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    data_app = {}

    for qs in query_list:

        data = []

        for entry in qs:

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

        if aggregation:
            '''if the chart requires aggregation of data across member states'''
            if aggregation == 'sum':
                categories.append("SADC Total")

                data_dict[indicator_label].append(
                    sum_val(data_dict, indicator_label))

            elif aggregation == 'avg':
                categories.append("SADC Average")

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
    '''This is for the existence of policy by member states chart (column chart)'''

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    data_app = {}

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

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            data_app[label].append(
                mean_val(data_app, label))

    chart_html = ColumnChart(categories=categories,
                             data_dict=data_app,
                             chart_title=chart_title,
                             y_axis_title=y_axis_title,
                             year=year, round='2',
                             max_value=100,
                             chart_color=color_lightblue)

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            # data_dict[indicator_label].append(
            #     mean_val(data_dict, indicator_label))

            # Implementation through score card confiuration
            data_dict[indicator_label].append(
                scorecard_sadc_mobile_penetration(year))

    chart_html = LineChart(categories=categories, data_dict=data_dict,
                           chart_title=chart_title, y_axis_title=y_axis_title, year=year)

    return chart_html


def chart_fixed_telephone_line(year):
    ''' This is for Fixed Telephone Lines chart'''

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories,
                             data_dict=data_dict,
                             chart_title=chart_title,
                             y_axis_title=y_axis_title,
                             year=year,
                             chart_color=color_blue)

    return chart_html


def chart_pop_coveredby_mobl_network(year):
    ''' This is for Population Covered by Mobile Network Chart'''

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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

    global avg_pop_coverage_3g
    if 'Percentage of population covered by at least a 3G mobile network' in data_dict:

        pop_coverage_3g = data_dict['Percentage of population covered by at least a 3G mobile network']

        avg_pop_coverage_3g = round(
            mean(d for d in pop_coverage_3g if d != ''), 1)

    else:

        avg_pop_coverage_3g = "-"

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories,
                             data_dict=data_dict,
                             chart_title=chart_title,
                             y_axis_title=y_axis_title,
                             year=year,
                             chart_color=tricolors)

    return chart_html


def chart_mobl_geog_coverage(year):
    ''' This is for Mobile Geographic Coverage Chart'''

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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

        global sadc_network_coverage

        sadc_network_coverage = round(mean_val(data_dict, indicator_label), 1)

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories,
                             data_dict=data_dict,
                             chart_title=chart_title,
                             y_axis_title=y_axis_title,
                             year=year,
                             chart_color=color_green)

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories,
                             data_dict=data_dict,
                             chart_title=chart_title,
                             y_axis_title=y_axis_title,
                             year=year,
                             chart_color=color_blue)

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

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

            indicator_label = chart_indicator.series_name if chart_indicator and chart_indicator.series_name else entry.indicator.label

            if indicator_label != 'Total Internet Subscribers':
                indicator_label = 'International Internet Bandwidth'

            if (entry.ind_value_adjusted):
                data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)

        data_dict[indicator_label] = data

    data_calc = {}

    label = 'internet users'

    if 'International Internet Bandwidth' in data_dict and 'Total Internet Subscribers' in data_dict:
        data_calc[label] = list(map(
            perUser, data_dict['International Internet Bandwidth'], data_dict['Total Internet Subscribers']))

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':

            categories.append("SADC Average")  # type: ignore

            total_bandwidth = sum_val(
                data_dict, 'International Internet Bandwidth')

            total_users = sum_val(
                data_dict, 'Total Internet Subscribers')

            # global total_internet_users
            # global avg_internet_penetration

            # total_internet_users = total_users

            # if total_internet_users and total_population:
            #     try:
            #         avg_internet_penetration = round(float(
            #             total_internet_users)/float(total_population), 2)
            #     except:
            #         avg_internet_penetration = '-'

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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
            '''if the chart requires aggregation of data across member states'''
            if aggregation == 'sum':
                categories.append("SADC Total")

                data_dict[indicator_label].append(
                    sum_val(data_dict, indicator_label))

            elif aggregation == 'avg':
                categories.append("SADC Average")

                data_dict[indicator_label].append(
                    mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title,
                             y_axis_title=y_axis_title, year=year,
                             round='3', chart_color=sixcolors)

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

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
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year, round='0', max_value=100)

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

                indicator_data = IndicatorData.objects.filter(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

        for qs in query_list:

            data = []

            for entry in qs:

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

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

        elif aggregation == 'yesPercentage':
            categories.append(indicator_label)

            spiderweb_data.append(mean_val(
                data_dict, indicator_label)*100)

    data_dict = dict(zip(categories, data_dict[indicator_label]))

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

            if entry.currency.member_state.member_state_short_name:
                categories.append(
                    entry.currency.member_state.member_state_short_name)
            else:
                categories.append(entry.currency.member_state.member_state)

            if (entry.exchange_rate):
                data.append(1/float(entry.exchange_rate))
            else:
                data.append('')

        data_dict[indicator_label] = data

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':
            categories.append("SADC Average")

            data_dict[indicator_label].append(
                mean_val(data_dict, indicator_label))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year, round='3')

    return chart_html


def get_published_years_for_query():
    '''Get Published Years from database'''

    #from portaldata.models import Published
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

    context = {}

    dict_values = []

    pivot_table = None

    ind_data = None

    if request.method == "GET":

        export_format = request.GET.get('_export', None)

        indicators = request.GET.getlist('indicator_filter_field')
        ms = request.GET.getlist('memberstate_filter_field')

        years = request.GET.getlist('year_filter_field')

        if indicators or ms or years:

            ind_data = IndicatorData.objects.filter(validation_status=INDICATORDATA_STATUS.validated).order_by(
                'member_state__member_state', 'indicator')

            if ms and ms != ['all'] and 'all' not in ms:
                ind_data = ind_data.filter(member_state__in=list(ms))

            if indicators and indicators != ['all'] and 'all' not in indicators:
                ind_data = ind_data.filter(indicator__in=list(indicators))

            # get_published_years_for_query()
            #this is not needed

            if years and years != ['Select All'] and 'Select All' not in years:
                ind_data = ind_data.filter(reporting_year__in=years)
            else:
                ind_data = ind_data.filter(
                    reporting_year__in=get_published_years_for_query())

            if 'filter_usd' in request.GET:

                currency_data_type = '''
                Data for all currency types is convered to USD.
                '''

                pivot_table = pivot(ind_data,
                                    ['indicator__label',
                                        'member_state__member_state'],
                                    'reporting_year', 'ind_value_adjusted', aggregation=Max)  # type: ignore
            else:

                currency_data_type = '''Data for all currency types is in Local Currency 
               '''

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

                # type: ignore
                tbl.base_columns[colname] = column

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

    context = {"table": tbl, "form": form,
               "currency_data_type": currency_data_type}

    return render(request, "portal/generatereport.html", context=context)
