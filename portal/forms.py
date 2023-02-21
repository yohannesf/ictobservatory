from django import forms
from django.forms import Form, ChoiceField, CharField
from django_select2.forms import Select2MultipleWidget, Select2Widget
from core.views import Get_Reporting_Year

from portaldata.models import Indicator, IndicatorData, MemberState


def published_years():
    from portaldata.models import Published
    year = None
    year = list(Published.objects.filter(
        published_status=True).values('reporting_year').order_by('-reporting_year'))
    return year


def latest_published_year():
    from portaldata.models import Published
    year = None
    year = list(Published.objects.filter(
        published_status=True).values_list('reporting_year', flat=True).order_by('-reporting_year'))

    if year:
        year = year[0]
    else:
        year = Get_Reporting_Year()
    return year


class HomePageFilterYear(forms.Form):

    year_filter = forms.ChoiceField(
        choices=[])
    # years_qs = None

    def __init__(self, *args, **kwargs):
        super(HomePageFilterYear, self).__init__(*args, **kwargs)

        if published_years():
            years_qs = published_years()

        else:
            years_qs = [{'reporting_year': Get_Reporting_Year()}]

        YEAR_CHOICES = tuple((),)

        for i in years_qs:
            for k, v in i.items():
                YEAR_CHOICES += ((v, v),)

        self.fields['year_filter'] = forms.ChoiceField(
            choices=YEAR_CHOICES)
        self.fields['year_filter'].required = False

    # year_filter = forms.ChoiceField(
    #     choices=YEAR_CHOICES)

    # print(YEAR_CHOICES)

    # print(years_qs)

    # print(year_filter_field)

    # def __init__(self, *args, **kwargs):
    #     super(HomePageFilterYear, self).__init__(*args, **kwargs)
    # assign a (computed, I assume) default value to the choice field
    # self.initial['year_filter'] = Get_Reporting_Year()
    # you should NOT do this:
    # self.fields['year_filter'].initial = Get_Reporting_Year()


class FilterForm(forms.Form):

    year_filter_field = forms.ChoiceField(choices=[])
    indicator_filter_field = forms.ChoiceField(choices=[])
    memberstate_filter_field = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        memberstates_qs = MemberState.objects.filter(
            memberstate_status=True).values().order_by('member_state')

        MEMBERSTATE_CHOICES = sorted(tuple(set(
            [(q['id'], q['member_state']) for q in memberstates_qs])))

        indicators_qs = Indicator.objects.filter(status='Active').values()

        INDICATOR_CHOICES = sorted(tuple(set(
            [(q['id'], q['label']) for q in indicators_qs])))

    # print(IndicatorData.objects.values('reporting_year').distinct().order_by())

        if published_years():
            years_qs = published_years()

        else:
            years_qs = [{'reporting_year': Get_Reporting_Year()}]

        # years_qs = list(IndicatorData.objects.values(
        #     'reporting_year').distinct().order_by())

        YEAR_CHOICES = tuple((),)
        for i in years_qs:
            for k, v in i.items():
                YEAR_CHOICES += ((v, v),)

        self.fields['indicator_filter_field'] = forms.MultipleChoiceField(
            choices=INDICATOR_CHOICES, widget=Select2MultipleWidget)

        self.fields['memberstate_filter_field'] = forms.MultipleChoiceField(
            choices=MEMBERSTATE_CHOICES, widget=Select2MultipleWidget)
        self.fields['year_filter_field'] = forms.MultipleChoiceField(
            choices=YEAR_CHOICES, widget=Select2MultipleWidget)

        self.fields['indicator_filter_field'].required = False
        self.fields['memberstate_filter_field'].required = False
        self.fields['year_filter_field'].required = False
