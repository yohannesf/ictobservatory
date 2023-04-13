from django.template import Library
from core.views import Get_Reporting_Year, Get_Num_Days_Left, Is_Reporting_Period

from portaldata.models import DATA_TYPE
register = Library()


@register.filter(name='addclass')
def addclass(field, class_attr):
    return field.as_widget(attrs={'class': class_attr})


@register.simple_tag
def reporting_year():
    return Get_Reporting_Year()


@register.simple_tag
def num_days_left():
    return Get_Num_Days_Left()


@register.simple_tag
def check_within_reporting_period():
    return Is_Reporting_Period()


@register.simple_tag
def getInputDecorator(indicator):

    if indicator.data_type == DATA_TYPE.select:
        return "v"
    elif indicator.data_type == DATA_TYPE.number or indicator.data_type == DATA_TYPE.decimal:
        return '#'
    elif indicator.data_type == DATA_TYPE.percentage:
        return '%'
    elif indicator.data_type == DATA_TYPE.currency:
        return '$'

    # elif indicator.data_type == DATA_TYPE.decimal:
    #     return '#'
    elif indicator.data_type == DATA_TYPE.url or indicator.data_type == DATA_TYPE.email:
        return '@'
    # elif indicator.data_type == DATA_TYPE.email:
    #     return '@'
    elif indicator.data_type == DATA_TYPE.date:
        return ''
    elif indicator.data_type == DATA_TYPE.text_area:
        return '...'
    else:
        return ''

    '''
    elif indicator.data_type == DATA_TYPE.currency and indicator.type_of_currency == 'usd':
        return '$'
    elif indicator.data_type == DATA_TYPE.currency:
        return 'LC'
    '''
