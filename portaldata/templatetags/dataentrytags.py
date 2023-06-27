from django.template import Library
from core.sharedfunctions import get_current_reporting_year, get_num_days_remaining, is_reporting_period

from portaldata.models import DATA_TYPE
register = Library()


@register.filter(name='addclass')
def addclass(field, class_attr):
    return field.as_widget(attrs={'class': class_attr})


@register.simple_tag
def reporting_year():
    return get_current_reporting_year()


@register.simple_tag
def num_days_left():
    return get_num_days_remaining()


@register.simple_tag
def check_within_reporting_period(additional_days=None):
    return is_reporting_period(additional_days=additional_days)


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


@register.simple_tag
def get_currency_type_information(indicator):

    if indicator.data_type == DATA_TYPE.currency and indicator.type_of_currency == 'usd':
        return '(USD)'
    elif indicator.data_type == DATA_TYPE.currency:
        return '(local currency)'
    else:
        return None
