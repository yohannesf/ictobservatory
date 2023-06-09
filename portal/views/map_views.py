
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
        # submitted=True, validation_status=INDICATORDATA_STATUS.validated
    ).values(code=F('member_state__member_state_iso3_code'),
             name=F('member_state__member_state'),
             shortname=F('member_state__member_state_short_name'),
             value=F('ind_value_adjusted'),
             ind_name=F('indicator__label')))

    return JsonResponse(data, safe=False)


def split(a, n):
    k, m = divmod(len(a), n)

    d = list(a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    return d


def is_number(s):
    try:
        complex(s)  # for int, long, float and complex
    except ValueError:
        return False

    return True


# def split(lst, n):
#     k, m = divmod(len(lst), n)
#     # print(k)
#     for i in range(n):
#         print((i+1)*k+min(i+1, m))
#         lst[i*k+min(i, m):(i+1)*k+min(i+1, m)]

#     return lst

def setOptions():
    '''
    Set general options
    A function to set general options for charts
    '''

    return '''Highcharts.setOptions({
                     lang: {

                        thousandsSep: ','
                        }
                        }
                    );'''


def map_view(request):

    context = {'map': map()}
    return render(request, 'portal/generate-maps.html', context=context)


def map():

    indicator = Indicator.objects.filter(id=1).first()

    data = json.loads(get_validated_data(indicator=indicator,
                                         reporting_year=Get_Reporting_Year()).content)

    res = [(float(sub['value']) if is_number(sub['value']) else sub['value'])
           for sub in data]
    #res = [sub['value'] for sub in data]

    res = sorted(res, key=lambda e: (e != '', e))
    #res = sorted(res, key=lambda e: (e is not None, e))

    x = split(res, 4)

    # one = (x[0][-1])
    # two = (x[1][-1])
    # three = (x[2][-1])

    one = (round(x[0][-1]) if is_number(x[0][-1]) else (x[0][-1]))

    two = (round(x[1][-1]) if is_number(x[1][-1]) else (x[1][-1]))
    three = (round(x[2][-1]) if is_number(x[2][-1]) else (x[2][-1]))

    dataclass = []

    if one == '':
        dataclass = []
        dataclass.append({'to': two})
        dataclass.append({'from': two, 'to': three})
        dataclass.append({'from': three})

    if two == '':
        dataclass = []
        dataclass.append({'to': three})

        dataclass.append({'from': three})

    if three == '':
        dataclass = []
        dataclass.append({'from': three})

    # print(one)
    # one = 1
    # two = 2
    # three = 3
    # four = round(x[3][-1])

    # print(x[0][5])

    # print([x])

    topology = requests.get(
        'https://code.highcharts.com/mapdata/custom/africa.topo.json').json()

    # begin = '''
    # (async () => {

    # var md = await fetch(
    #     'https://code.highcharts.com/mapdata/custom/africa.topo.json'
    # ).then(response => response.json());

    # '''

    begin = '{'

    # Instantiate the map
    # Highcharts.mapChart('container',
    map = {

        'chart': {
            # 'map': 'geojson',
            # 'renderTo': 'container',
            # 'height': '60%',
            'spacing': [20, 0, 0, 0],
            # 'plotBorderWidth': 0,
            # 'plotBackgroundColor': '#ffffff',



        },
        'title': {'text': indicator.label, 'align': 'center', },

        # 'subtitle': {
        #     'text': 'Demo of drawing all areas in the map, only highlighting partial data',
        #     'align': 'center'
        # },
        'exporting': {
            'sourceWidth': 600,
            'sourceHeight': 500
        },

        'legend': {
            'enabled': 'true',
            'layout': 'vertical',
            'borderWidth': 0,
            'backgroundColor': 'rgba(255,255,255,0.85)',
            'floating': 'true',
            'verticalAlign': 'bottom',
            'align': 'left',
            # 'y': 25
        },
        'credits': {'enabled': 'false'},


        'colorAxis': {
            'dataClasses': dataclass if dataclass else [
                {'to': one},
                {
                    'from': one,
                    'to': two
                },
                {
                    'from': two,
                    'to': three
                },
                {
                    'from': three
                }],

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
            # 'mapData': 'Highcharts.maps[custom/africa]',
            'mapData': topology,
            # 'type': 'map',
            'animation': {'duration': 1000},
            'name': indicator.label,
            'data': data,

            'joinBy': ['iso-a3', 'code'],
            'nullColor': 'red',

            # 'allAreas': 'true',
            # 'dataLabels': {
            #     'enabled': 'true',
            #     'color': '#FFFFFF',
            #     # 'format': '{point.shortname}',
            #     # 'format': '{point.name}',
            #     'nullFormat': ''
            # },
            # 'tooltip': {
            #     'headerFormat': '',
            #     'pointFormat': '{point.name}: {point.value}'
            # }
        }]
    }

   # end = ';})();'
    end = ';}'

    html = f'''
   <div id="container" >
    <script>
{setOptions()}
    {begin}
    Highcharts.mapChart('container', {map}){end}

    </script>
     </div>

    '''

    return html
