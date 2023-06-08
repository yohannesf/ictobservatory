
from django.http import HttpRequest, HttpResponse
import requests
import json
from django.shortcuts import render
from core.views import Get_Reporting_Year
from portaldata.models import INDICATORDATA_STATUS, Indicator, IndicatorData

from django.db.models import F, Q, When
from django.http import JsonResponse


def get_validated_data(indicator, reporting_year):
    '''Takes indicator and year and returns submitted and validated data for the year by indicator'''
    data = list(IndicatorData.objects.filter(
        indicator=indicator, reporting_year=reporting_year,
        submitted=True, validation_status=INDICATORDATA_STATUS.validated
    ).values(code=F('member_state__member_state_iso3_code'),
             name=F('member_state__member_state'),
             shortname=F('member_state__member_state_short_name'),
             value=F('ind_value_adjusted')))

    return JsonResponse(data, safe=False)


def map_view(request):
    indicator = Indicator.objects.filter(id=1).first()

    data = json.loads(get_validated_data(indicator=indicator,
                                         reporting_year='2022').content)

    print(data)

    context = {'map': map(data)}
    return render(request, 'portal/generate-maps.html', context=context)


def map(data):

    topology = requests.get(
        'https://code.highcharts.com/mapdata/custom/africa.topo.json').json()

    begin = '''
    (async () => {

    const topology = await fetch(
        'https://code.highcharts.com/mapdata/custom/africa.topo.json'
    ).then(response => response.json());

    '''

    # Instantiate the map
    # Highcharts.mapChart('container',
    map = {'chart': {'map': topology},
           'title': {
        'text': 'Nordic countries',
        'align': 'left'
    },

        'subtitle': {
        'text': 'Demo of drawing all areas in the map, only highlighting partial data',
        'align': 'left'
    },

        'accessibility': {
        'typeDescription': 'Map of Europe.',
        'point': {
            'describeNull': 'false'
        }
    },

        'legend': {
        'enabled': 'false'
    },

        'mapNavigation': {
        'enabled': 'true',
        'buttonOptions': {
            'align': 'right'
        }
    },
        'mapView': {
        'projection': {
            'name': 'WebMercator'
        },
            'center': [22, -15],
            'zoom': 3.5
    },

        'series': [{
            'name': 'Country',
            'data': data,

            # 'data': [
            #     {'code': 'AGO', 'value': 1},
            #     {'code': 'BWA', 'value': 2},
            #     {'code': 'COM', 'value': 3},
            #     {'code': 'COD', 'value': 4},
            #     {'code': 'SWZ', 'value': 5},
            #     {'code': 'LSO', 'value': 6},
            #     {'code': 'MDG', 'value': 7},
            #     {'code': 'MWI', 'value': 8},
            #     {'code': 'MUS', 'value': 9},
            #     {'code': 'MOZ', 'value': 10},
            #     {'code': 'NAM', 'value': 11},
            #     {'code': 'SYC', 'value': 12},
            #     {'code': 'ZAF', 'value': 13},
            #     {'code': 'TZA', 'value': 14},
            #     {'code': 'ZMB', 'value': 15},
            #     {'code': 'ZWE', 'value': 16}

            # ],
            'joinBy': ['iso-a3', 'code'],
            # allAreas: true,
            'dataLabels': {
                'enabled': 'true',
                'color': '#FFFFFF',
                'format': '{point.shortname}',
                'format': '{point.name}',
                'nullFormat': ''
            },
            'tooltip': {
                'headerFormat': '',
                'pointFormat': '{point.name}: {point.value}'
            }
        }]
    }

    end = ';})();'

    html = f'''
   <div id="container" class="text-primary chart-area" >
    <script>

    {begin}
    Highcharts.mapChart('container', {map}){end}

    </script>
     </div>

    '''

    return html
