
from statistics import mean

from portaldata.models import INDICATORDATA_STATUS, ExchangeRateData, GeneralIndicatorData, IndicatorData, MemberState, Chart, ChartConfig, ScoreCard, ScoreCardConfig

from ..charts import ColumnChart, LineChart, StackedChart, SpiderWebChart, SunBurstChart


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
avg_pop_coverage_3g = ''
sadc_network_coverage = ''

avg_internet_penetration = ''

total_population = ''

total_internet_users = ''


def get_validated_data(indicator, reporting_year):
    '''Takes indicator and year and returns submitted and validated data for the year by indicator'''
    return IndicatorData.objects.filter(
        indicator=indicator, reporting_year=reporting_year,
        submitted=True, validation_status=INDICATORDATA_STATUS.validated)


def sum_val(data_dict, indicator_label):
    total = 0
    if data_dict:
        if indicator_label in data_dict:
            if data_dict[indicator_label]:
                try:
                    for i in data_dict[indicator_label]:
                        if i != '':
                            total += float(i)

                    return round(total, 2)
                except:
                    return 0
            else:

                return 0
        else:

            return 0

    else:

        return 0


def mean_val(data_dict, indicator_label, round_to=2):
    if data_dict:
        if indicator_label in data_dict:
            if data_dict[indicator_label]:
                try:
                    return round(mean(d for d in data_dict[indicator_label] if d != ''), round_to)
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
        try:
            percent = [mean(k)*100 for k in zip(*result_list)]  # type: ignore

            return percent
        except:
            return 0
    else:
        return 0


def calculate_per_user(bandwidth, internet_user):
    if internet_user and bandwidth:
        try:
            return round(float(bandwidth) / float(internet_user), 2)
        except:
            return ''
    else:
        return ''


def scorecard_avg_pop_coverage_3g():
    return avg_pop_coverage_3g


def scorecard_sadc_network_coverage():
    return sadc_network_coverage


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

            indicator_data = list(get_validated_data(
                indicator=item.indicator, reporting_year=year).values_list("ind_value_adjusted", flat=True))
            # indicator_data = list(IndicatorData.objects.filter(
            #     indicator=item.indicator, reporting_year=year).values_list("ind_value_adjusted", flat=True))

            if item.num_denom:
                if item.num_denom == 'num':
                    item_option = "num"
                    query_list_num.append(indicator_data)
                elif item.num_denom == 'denom':
                    item_option = "denom"
                    query_list_denom.append(indicator_data)
                else:
                    # item_option = "other"
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
                except:
                    pass
    else:
        if query_list_num:
            if any(isinstance(el, list) for el in query_list_num):
                ls = [item for sublist in query_list_num for item in sublist]

                for item in ls:
                    try:
                        num += float(item)
                    except:
                        pass
            else:
                for item in query_list_num:
                    try:
                        num += float(item)
                    except:
                        pass

        if query_list_denom:
            if any(isinstance(el, list) for el in query_list_denom):
                ls = [item for sublist in query_list_denom for item in sublist]

                for item in ls:
                    try:
                        denom += float(item)
                    except:
                        pass
            else:
                for item in query_list_denom:
                    try:
                        denom += float(item)
                    except:
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
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(chart_name='chart_population').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        chart_description = chart.description
        aggregation = chart.aggregation

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
                    indicator=item.indicator, reporting_year=year)

                query_list.append(indicator_data)

    # cts = [entry.member_state.member_state_short_name or entry.member_state.member_state
    #        for qs in query_list for entry in qs]
    # print(cts)

    # chart_configs = {
    #     item.indicator: item for item in ChartConfig.objects.filter(chart=chart)}
    # print(chart_configs)

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
                             year=year, chart_description=chart_description)

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
    chart_description = ''

    chart = Chart.objects.filter(
        chart_name='chart_population_male_female').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                            chart_color=color_lightblue_lightgreen,
                            chart_description=chart_description)  # ,

    return recieved


def chart_gpd_per_capita(year):
    ''' This is for GDP per Capita Chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(chart_name='chart_gdp').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                             chart_title=chart_title,
                             y_axis_title=y_axis_title, year=year, chart_description=chart_description)

    return chart_html


def chart_gni_per_capita(year):
    ''' This is for GNI per Capita Chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''

    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(chart_name='chart_gni').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                             y_axis_title=y_axis_title, year=year, chart_description=chart_description)

    return chart_html


def chart_telecom_revenue(year):
    '''For the Telecommunications Revenue Chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    chart_description = ''

    main_stack_label = ''

    data_dict = {}

    chart = Chart.objects.filter(chart_name='chart_telecom_revenue').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                try:
                    data.append(round(float(entry.ind_value_adjusted), 2))
                except:
                    data.append(float(entry.ind_value_adjusted))
            else:
                data.append(entry.ind_value_adjusted)
        data_dict[indicator_label] = data

    recieved = StackedChart(categories=categories, data_dict=data_dict,
                            chart_title=chart_title, y_axis_title=y_axis_title, year=year,
                            stacking='normal',
                            grouped_stack=main_stack_label,
                            valign='bottom', floating=False, chart_description=chart_description)  # ,

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
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_internet_user_penetration').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        population_indicator = ChartConfig.objects.filter(
            series_name="Population").first()

        population_indicator = population_indicator.indicator if population_indicator else 0

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
                    indicator=item.indicator, reporting_year=year)

                '''per100 canculates the Per 100 inhabitat with the value/population * 100'''
                if item.extra_calculation == 'per100':

                    qs = []
                    population = 0
                    for i in indicator_data:
                        if population_indicator:

                            try:
                                population = IndicatorData.objects.get(
                                    indicator=population_indicator, reporting_year=year,
                                    member_state=i.member_state).ind_value

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
                             width='120', chart_color=sixcolors, chart_description=chart_description)

    return chart_html


def chart_telecom_investment(year):
    ''' This is for Telecommunications Investment Chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(chart_name='chart_telecom_investment').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                try:
                    data.append(round(float(entry.ind_value_adjusted), 2))
                except:
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
                             year=year, chart_color=tricolors, chart_description=chart_description)

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
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_existing_ict_regulation').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                                chart_title=chart_title, y_axis_title=y_axis_title, year=year, chart_description=chart_description)

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
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_existence_of_policy_by_ms').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                             chart_color=color_lightblue, chart_description=chart_description)

    return chart_html


def chart_mobile_penetration_rate(year):
    ''' This is for Mobile Penetration Rate in the SADC region'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_mobile_penetration_rate').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                           chart_title=chart_title, y_axis_title=y_axis_title, year=year, chart_description=chart_description)

    return chart_html


def chart_fixed_telephone_line(year):
    ''' This is for Fixed Telephone Lines chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_fixed_telephone_line').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                             chart_color=color_blue, chart_description=chart_description)

    return chart_html


def chart_pop_coveredby_mobl_network(year):
    ''' This is for Population Covered by Mobile Network Chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_pop_coveredby_mobl_network').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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

        try:
            avg_pop_coverage_3g = round(
                mean(d for d in pop_coverage_3g if d != ''), 1)
        except:
            avg_pop_coverage_3g = "-"

        # scorecard_avg_pop_coverage_3g(avg_pop_coverage_3g)

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
                             chart_color=tricolors, chart_description=chart_description)

    return chart_html


def chart_mobl_geog_coverage(year):
    ''' This is for Mobile Geographic Coverage Chart'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_mobl_geog_coverage').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                             chart_color=color_green, chart_description=chart_description)

    return chart_html


def chart_inter_internet_bandwidth(year):
    ''' This is for International Internet Bandwidth (Mbits/s)'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_inter_internet_bandwidth').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                             chart_color=color_blue, chart_description=chart_description)

    return chart_html


def chart_inter_internet_bandwidth_per_inhabitant(year):
    ''' This is for International Internet Bandwidth Per Inhabitant (kbit/s)'''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_inter_internet_bandwidth_per_inhabitant').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

               # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year, chart_description=chart_description)

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

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
            calculate_per_user, data_dict['International Internet Bandwidth'], data_dict['Total Internet Subscribers']))

    if aggregation:
        '''if the chart requires aggregation of data across member states'''
        if aggregation == 'sum':
            categories.append("SADC Total")

            data_dict[indicator_label].append(
                sum_val(data_dict, indicator_label))

        elif aggregation == 'avg':

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
                categories.append("SADC Average")  # type: ignore

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
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_fixed_telephone_tariffs').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                try:
                    data.append(round(float(entry.ind_value_adjusted), 4))
                except:
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
                    mean_val(data_dict, indicator_label, 4))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title,
                             y_axis_title=y_axis_title, year=year,
                             round='3', chart_color=sixcolors, chart_description=chart_description)

    return chart_html


def chart_sms_tariff(year):
    ''' This is for Mobile Cellular SMS Tariff '''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_sms_tariff').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                try:
                    data.append(round(float(entry.ind_value_adjusted), 4))
                except:
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
                mean_val(data_dict, indicator_label, 4))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title,
                             y_axis_title=y_axis_title, year=year, round='3', chart_description=chart_description)

    return chart_html


def chart_literacy_rate(year):
    ''' This is for Literacy Rate '''

    categories = []

    query_list = []

    indicator_label = ''

    chart_title = ''
    y_axis_title = ''
    aggregation = ''
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_literacy_rate').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description

        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                             y_axis_title=y_axis_title, year=year, round='0',
                             max_value=100, chart_description=chart_description)

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
    chart_description = ''

    data_dict = {}

    chart = Chart.objects.filter(
        chart_name='chart_ict_contrib_gdp').first()

    if chart:
        chart_title = chart.chart_title
        y_axis_title = chart.y_axis_title
        aggregation = chart.aggregation
        chart_description = chart.description
        indicators_list = ChartConfig.objects.filter(chart=chart)

        if indicators_list:

            for item in indicators_list:

                # indicator_data = IndicatorData.objects.filter(
                #     indicator=item.indicator, reporting_year=year)
                indicator_data = get_validated_data(
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
                               chart_title=chart_title, y_axis_title=y_axis_title, year=year, chart_description=chart_description)

    return chart_html


def chart_exchange_rate(year):
    ''' This is for Exchange Rate '''

    categories = []

    query_list = []

    indicator_label = 'Exchange Rate'

    chart_title = 'Exchange Rate (Local Currency to USD)'
    y_axis_title = 'USD'
    aggregation = 'avg'
    chart_description = ''
    #chart_description = chart.description

    data_dict = {}

    exchange_rate_queryset = ExchangeRateData.objects.filter(
        reporting_year=year, submitted=True)

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

                try:
                    data.append(round(1/float(entry.exchange_rate), 5))
                except:
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
                mean_val(data_dict, indicator_label, 5))

    chart_html = ColumnChart(categories=categories, data_dict=data_dict,
                             chart_title=chart_title, y_axis_title=y_axis_title, year=year, round='3')

    return chart_html
