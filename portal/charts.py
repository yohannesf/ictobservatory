import random
import string
from dataclasses import dataclass, field
import json
from typing import List

# from palettable.colorbrewer.qualitative import Dark2_7 as palette
# from palettable.cmocean.diverging import Balance_20 as palette
# from palettable.colorbrewer.qualitative import Paired_12 as palette
# from palettable.cubehelix import cubehelix3_16 as palette
# from palettable.lightbartlein.diverging import BlueDarkRed18_6 as palette
from palettable.lightbartlein.diverging import BlueDarkRed12_6 as palette  # type: ignore
# from palettable.lightbartlein.diverging import BlueDarkRed18_2 as palette
# from palettable.lightbartlein.diverging import BlueDarkRed18_18 as palette

# COLORS = [
#     '#64748b', '#a1a1aa', '#374151', '#78716c', '#d6d3d1', '#fca5a5', '#ef4444', '#7f1d1d',
#     '#fb923c', '#c2410c', '#fcd34d', '#b45309', '#fde047', '#bef264', '#ca8a04', '#65a30d',
#     '#86efac', '#15803d', '#059669', '#a7f3d0', '#14b8a6', '#06b6d4', '#155e75', '#0ea5e9',
#     '#075985', '#3b82f6', '#1e3a8a', '#818cf8', '#a78bfa', '#a855f7', '#6b21a8', '#c026d3',
#     '#db2777', '#fda4af', '#e11d48', '#9f1239'
# ]

COLORS = ['#2C318A', '#1a8e58',  '#1c70e5', '#00425A', '#1f6dff',   '#0f367f', '#02B052', '#362FD9', '#28da87',  '#17814f', '#0d4d2f',
          '#C49801', '#b18803', '#134b99', '#fdc204', '#d7a503', '#1857cc', '#0c3265', '#3C84AB', '#7d6002', '#493801', '#FC7300', '#21b46f', '#1F8A70', '#BFDB38']


def get_random_colors(num, colors=[]):
    """
    function to generate a random hex color list

    ``num`` the number of colors required

    ``colors`` the existing color list - additional
    colors will be added if colors exist
    """
    if len(colors) > 0:

        return colors

    while len(colors) < num:
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))

        if color not in colors:
            colors.append(color)

    return colors


def get_colors():
    """
    Get colors from palette.colors or randomly generate a list
    of colors.  This works great with the palettable module
    but this is not required and will call get_random_colors
    if palette.color is not set
    """
    try:
        return palette.hex_colors
    except:
        return get_random_colors(6)


'''
HIGH CHARTS IMPLEMENTATION FUNCTIONS
'''


def setOptions():
    '''
    Set general options
    A function to set general options
    '''

    return '''Highcharts.setOptions({
                     lang: {

                        thousandsSep: ','
                        }
                        }
                    );'''


def ColumnChart(categories, data_dict, chart_title, y_axis_title, year, valign='bottom', floating=False, layout='horizontal', round='1', width=''):
    '''
    A function to generate column charts.
        Categories - Categories
        Data_dict - dictionary of data with series name
    Returns a list with Chart html, chart_title, year, and the chart container

    '''

    series = []
    color = get_random_colors((len(data_dict)*5), colors=COLORS)

    percent_value = '%' if y_axis_title == '%' else ''

    for k, v in data_dict.items():

        series.append({
            'name': k,
            'data': v,
            'color': color[random.randint(0, len(color)-1)],
            'showInLegend': False if len(data_dict) == 1 else True

        })

    chart = {

        'chart': {'renderTo': 'container', 'type': 'column', },
        'xAxis': {'categories': categories, 'labels': {'textOverflow': 'none'}},
        'title': {'text': None},
        'yAxis': {'title': {'text': y_axis_title}, 'labels': {'overflow': 'wrap'}, },
        'credits': {'enabled': False},

        'legend': {'verticalAlign': valign,  'align': 'center', 'floating': floating,  'layout': layout, 'itemStyle': {'width': width}},
        # 'plotOptions': {'series': {'dataLabels': {'enabled': 'true', 'rotation': 270, 'y': -25,   'crop': False, 'overflow': 'none'}}},
        'series': series,
        'exporting':  {'chartOptions':
                       {
                           'title': {'text': chart_title},
                           'subtitle': {'text': 'Year: ' + year},
                           #    'plotOptions': {'series': {'dataLabels': {
                           #        'enabled': 'true', 'rotation': 270, 'y': -25, 'crop': False, 'overflow': 'none'}}}
                       },
                       'filename': chart_title + '_' + year,
                       'sourceWidth': 1000,

                       'buttons': {'contextButton': {'enabled': False}}
                       },
        'tooltip': {'shared': False,
                    'pointFormat': '{series.name}: <b>{point.y:,.'+round+'f}'+percent_value+'</b><br/>'

                    },
        'lang': {
            'noData': 'No Data'
        },

        'noData': {
            'style': {
                'fontWeight': 'bold',
                'fontSize': '15px',
                'color': '#303030'
            }
        }


    }

    dump = json.dumps(chart)

    container_title = chart_title

    container_title = container_title.replace('(', '')
    container_title = container_title.replace(')', '')
    container_title = container_title.replace('/', '')
    container_title = container_title.replace('%', '')

    container = container_title.replace(' ', '')+'_container'

    html = f'''
    <div id="{container}" class="text-primary chart-area" >
    <script>
    {setOptions()}
    Highcharts.chart('{container}', { dump });
    </script>
    </div>
    '''

    return [html, chart_title, year, container]


def LineChart(categories, data_dict, chart_title, y_axis_title, year):  # Line Charts
    series = []
    color = get_random_colors((len(data_dict)*5))

    for k, v in data_dict.items():

        series.append({
            'name': k,
            'data': v,
            'color': color[random.randint(0, len(color)-1)],
            # if single series, don't show in legend
            'showInLegend': False if len(data_dict) == 1 else True
        })

    percent_value = '%' if (
        y_axis_title == '%' or y_axis_title == 'Percent') else ''

    chart = {

        'chart': {'renderTo': 'container', 'type': 'line', },
        'xAxis': {'categories': categories, 'labels': {'textOverflow': 'none'}},
        'title': {'text': None},
        'yAxis': {'title': {'text': y_axis_title}, 'labels': {'overflow': 'wrap'}, },
        'credits': {'enabled': False},
        'legend': {'verticalAlign': 'top',  'align': 'right', 'floating': True,  'layout': 'vertical'},
        # 'plotOptions': {'series': {'dataLabels': {'enabled': 'true', 'rotation': 270, 'y': -25,   'crop': False, 'overflow': 'none'}}},
        'series': series,
        'exporting':  {'chartOptions':
                       {
                           'title': {'text': chart_title},
                           'subtitle': {'text': 'Year: ' + year},
                           #    'plotOptions': {'series': {'dataLabels': {
                           #        'enabled': 'true', 'rotation': 270, 'y': -25, 'crop': False, 'overflow': 'none'}}}
                       },
                       'filename': chart_title + '_' + year,
                       'sourceWidth': 1000,

                       'buttons': {'contextButton': {'enabled': False}}
                       },
        'tooltip': {'shared': False,
                    'pointFormat': '{series.name}: <b>{point.y:,.1f}'+percent_value+'</b><br/>'},
    }

    dump = json.dumps(chart)

    container_title = chart_title

    container_title = container_title.replace('(', '')
    container_title = container_title.replace(')', '')
    container_title = container_title.replace('/', '')
    container_title = container_title.replace('%', '')

    container = container_title.replace(' ', '')+'_container'

    html = f'''
    <div id="{container}" class="text-primary chart-area" >
    <script>
    {setOptions()}
    Highcharts.chart('{container}', { dump });
    </script>
    </div>
    '''

    return [html, chart_title, year, container]


def StackedChart(categories, data_dict, chart_title, y_axis_title, year, stacking='normal', grouped_stack='', valign='bottom', floating=False):  # Stacked
    series = []
    color = get_random_colors((len(data_dict)*5), colors=COLORS)

    for k, v in data_dict.items():

        series.append({
            'name': k,
            'data': v,
            # 'color': color[random.randint(0, len(color)-1)],
            'stack': 'Main' if k == grouped_stack else 'Other',
            'showInLegend': False if len(data_dict) == 1 else True
        })

    percent_value = '%' if (
        y_axis_title == '%' or y_axis_title == 'Percent') else ''

    chart = {

        'chart': {'renderTo': 'container', 'type': 'column', },
        'xAxis': {'categories': categories, 'labels': {'textOverflow': 'none'}},
        'title': {'text': None},
        'yAxis': {'title': {'text': y_axis_title}, 'labels': {'overflow': 'wrap'},
                  'stackLabels': {'enabled': False, 'style': {'fontSize': '9px', 'textOutline': 'none'}}, },
        'credits': {'enabled': False},
        'legend': {'verticalAlign': valign,  'align': 'center', 'floating': floating,  'layout': 'horizontal', },
        # 'plotOptions': {'series': {'dataLabels': {'enabled': 'true', 'rotation': 270, 'y': -25,   'crop': False, 'overflow': 'none'}}},
        'plotOptions': {'column': {'stacking': stacking,
                        'dataLabels': {'enabled': False, 'style': {'fontSize': '9px', 'textOutline': 'none'}}}},
        'series': series,
        'exporting':  {'chartOptions':
                       {
                           'title': {'text': chart_title},
                           'subtitle': {'text': 'Year: ' + year},
                           #    'plotOptions': {'series': {'dataLabels': {
                           #        'enabled': 'true',  'crop': False, 'overflow': 'none'}}}
                       },
                       'filename': chart_title + '_' + year,
                       'sourceWidth': 1000,

                       'buttons': {'contextButton': {'enabled': False}}
                       },
        'tooltip': {'shared': False,
                    'pointFormat': '{series.name}: <b>{point.y:,.1f}'+percent_value+'</b><br/>'

                    },
    }

    dump = json.dumps(chart)

    container_title = chart_title

    container_title = container_title.replace('(', '')
    container_title = container_title.replace(')', '')
    container_title = container_title.replace('/', '')
    container_title = container_title.replace('%', '')

    container = container_title.replace(' ', '')+'_container'

    html = f'''
    <div id="{container}" class="text-primary chart-area" >
    <script>
    {setOptions()}
    Highcharts.chart('{container}', { dump });
    </script>
    </div>
    '''

    return [html, chart_title, year, container]


def SpiderWebChart(categories, data_dict, chart_title, y_axis_title, year):  # Spiderweb chart
    series = []
    color = get_random_colors((len(data_dict)*5))

    for k, v in data_dict.items():

        series.append({
            'name': k,
            'data': v,
            'color': color[random.randint(0, len(color)-1)],
            'pointPlacement': 'on',
            'showInLegend': False if len(data_dict) == 1 else True
        })

    chart = {

        # https://jsfiddle.net/fv374ssL/14/

        'chart': {'renderTo': 'container', 'polar': 'true', 'type': 'area', 'spacing': [20, 5, 20, 5], },
        'xAxis': {'categories': categories, 'tickmarkPlacement': 'on', 'lineWidth': '0',
                  'labels': {'allowOverlap': False, 'style': {
                      'whiteSpace': 'nowrap',

                      'fontSize': '10px'
                  }, }},
        'title': {'text': None},
        'pane': {'size': '95%'},
        'yAxis': {'gridLineInterpolation': 'polygon',  'lineWidth': 2,  'min': 0,
                  'labels': {'format': '{value}%'}},
        'credits': {'enabled': False},
        'legend': {'verticalAlign': 'top',  'align': 'right', 'floating': True,  'layout': 'vertical'},
        # # 'plotOptions': {'series': {'dataLabels': {'enabled': 'true', 'rotation': 270, 'y': -25,   'crop': False, 'overflow': 'none'}}},

        'series': series,
        # 'caption': {'text': 'AVERAGE EXISTENCE OF RELEVANT ICT POLICY, REGULATION, GUIDELINE INSTITUTIONAL STRUCTURE ACROSS THE SADC REGION'},
        'exporting':  {'chartOptions':
                       {
                           'title': {'text': chart_title},
                           'subtitle': {'text': 'Year: ' + year},
                           #    'plotOptions': {'series': {'dataLabels': {
                           #        'enabled': 'true', 'style': {'fontSize': '9px'}, 'crop': False, 'overflow': 'none'}}}
                       },
                       'filename': chart_title + '_' + year,
                       'sourceWidth': 1000,

                       'buttons': {'contextButton': {'enabled': False}}
                       },

        'tooltip': {'shared': True,
                    'pointFormat': '{series.name}: <b>{point.y:,.1f}%</b><br/>'
                    },
    }

    dump = json.dumps(chart)

    container_title = chart_title

    container_title = container_title.replace('(', '')
    container_title = container_title.replace(')', '')
    container_title = container_title.replace('/', '')
    container_title = container_title.replace('%', '')

    container = container_title.replace(' ', '')+'_container'

    html = f'''
    <div id="{container}" class="text-primary chart-area" >
    <script>
    {setOptions()}
    Highcharts.chart('{container}', { dump });
    </script>
    </div>
    '''

    return [html, chart_title, year, container]


def SunBurstChart(categories, data_dict, chart_title, y_axis_title, year):  # Variable Pie Charts
    data = []
    color = get_random_colors((len(data_dict)*5))

    for k, v in data_dict.items():

        data.append({
            'name': k,
            'y': v,
            'z': 119,
            'color': color[random.randint(0, len(color)-1)],
            # if single series, don't show in legend
            'showInLegend': False if len(data_dict) == 1 else True
        })

    chart = {

        'chart': {'renderTo': 'container', 'type': 'variablepie', },
        'xAxis': {'categories': categories, 'labels': {'textOverflow': 'none'}},
        'title': {'text': None},
        'yAxis': {'title': {'text': y_axis_title}, 'labels': {'overflow': 'wrap'}, },
        'credits': {'enabled': False},
        'legend': {'verticalAlign': 'top',  'align': 'right', 'floating': True,  'layout': 'vertical'},
        # 'plotOptions': {'series': {'dataLabels': {'enabled': 'true', 'rotation': 270, 'y': -25,   'crop': False, 'overflow': 'none'}}},
        'series': [{
            'minPointSize': 10,
            'innerSize': '50%',
            'zMin': 0,
            'name': 'Data',
            'data': data,
            'dataLabels': {'format': '{point.name}<br>{point.y}%', 'align': 'center', },
        }
        ],


        'exporting':  {'chartOptions':
                       {
                           'title': {'text': chart_title},
                           'subtitle': {'text': 'Year: ' + year},
                           #    'plotOptions': {'series': {'dataLabels': {
                           #        'enabled': 'true', }}},  # 'rotation': 270, 'y': -25, 'crop': False, 'overflow': 'none'}}}
                       },
                       'filename': chart_title + '_' + year,
                       'sourceWidth': 1000,

                       'buttons': {'contextButton': {'enabled': False}}
                       },

        'tooltip': {'shared': True,
                    'pointFormat': '{series.name}: <b>{point.y}%</b><br/>'
                    },
    }

    dump = json.dumps(chart)

    container_title = chart_title

    container_title = container_title.replace('(', '')
    container_title = container_title.replace(')', '')
    container_title = container_title.replace('/', '')
    container_title = container_title.replace('%', '')

    container = container_title.replace(' ', '')+'_container'

    html = f'''
    <div id="{container}" class="text-primary chart-area" >
    <script>
    {setOptions()}
    Highcharts.chart('{container}', { dump });
    </script>
    </div>
    '''

    return [html, chart_title, year, container]
