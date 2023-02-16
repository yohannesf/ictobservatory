from django.conf import settings

# date input format
DATE_INPUT_FORMAT = settings.DATE_INPUT_FORMAT if hasattr(settings, 'DATE_INPUT_FORMAT') else \
    ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%y', '%d/%m/%Y']

# validators
field_validators = {
    'max_length': {
        'email': 150,
        'text': 250,
        'url': 250
    }
}
if hasattr(settings, 'SURVEY_FIELD_VALIDATORS'):
    max_length = settings.SURVEY_FIELD_VALIDATORS.get('max_length')
    if max_length:
        field_validators['max_length'].update(max_length)
SURVEY_FIELD_VALIDATORS = field_validators

# charjs source
CHART_JS_SRC = settings.CHART_JS_SRC if hasattr(
    settings, 'CHART_JS_SRC') else '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
