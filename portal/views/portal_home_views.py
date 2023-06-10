
from django.shortcuts import render
from portal.forms import HomePageFilterYear
from core.sharedfunctions import get_latest_published_year
from django.shortcuts import render
from .chart_views import (chart_telecom_revenue, chart_ict_contrib_gdp,
                          chart_telecom_investment,  chart_mobile_penetration_rate,
                          chart_fixed_telephone_line, chart_pop_coveredby_mobl_network,
                          chart_mobl_geog_coverage, chart_internet_user_penetration,
                          chart_inter_internet_bandwidth,
                          chart_inter_internet_bandwidth_per_user,
                          chart_inter_internet_bandwidth_per_inhabitant,
                          chart_fixed_telephone_tariffs, chart_sms_tariff,
                          chart_existence_of_policy_by_ms, chart_existing_ict_regulation,
                          chart_literacy_rate,
                          chart_population, chart_population_male_female, chart_gpd_per_capita,
                          chart_gni_per_capita, chart_exchange_rate,
                          scorecard_avg_internet_penetration,
                          scorecard_sadc_mobile_penetration,
                          scorecard_avg_pop_coverage_3g,
                          scorecard_sadc_network_coverage)


'''
Global variables used to populate score cards in the home page
'''
# sadc_mobile_penetration = ''

#avg_pop_coverage_3g = ''
#sadc_network_coverage = ''
#avg_internet_penetration = ''

#total_population = ''

#total_internet_users = ''


def index(request):
    '''
    Main home page
    This view renders all the charts and score cards in the home page
    '''

    form = HomePageFilterYear(request.GET or None)

    year = get_latest_published_year()

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
        'sadc_network_coverage': scorecard_sadc_network_coverage(),
        'avg_pop_coverage_3g': scorecard_avg_pop_coverage_3g(),
        # 'avg_pop_coverage_3g': avg_pop_coverage_3g,
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

    year = get_latest_published_year()

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
