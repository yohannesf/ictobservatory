from django import forms

from django_select2.forms import Select2MultipleWidget
from core.sharedfunctions import get_published_years
from core.views import Get_Reporting_Year

from portaldata.models import Indicator, MemberState


# def get_published_years():
#     '''Get Published Years from database'''

#     from portaldata.models import Published
#     year = None
#     year = list(Published.objects.filter(
#         published_status=True).values('reporting_year').order_by('-reporting_year'))
#     # print(year)
#     return year


def latest_published_year():
    '''Get Latest Published Year'''

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

    '''Year Filter Form on Home Page'''

    year_filter = forms.ChoiceField(
        choices=[])
    # years_qs = None

    def __init__(self, *args, **kwargs):

        super(HomePageFilterYear, self).__init__(*args, **kwargs)

        if get_published_years():
            years_qs = get_published_years()
            print(years_qs)

        else:
            #years_qs = [{'reporting_year': Get_Reporting_Year()}]
            years_qs = [Get_Reporting_Year()]
            print(years_qs)

        YEAR_CHOICES = tuple((),)

        for i in years_qs:
            YEAR_CHOICES += ((i, i),)
        # for i in years_qs:
        #     for k, v in i.items():
        #         YEAR_CHOICES += ((v, v),)

        self.fields['year_filter'] = forms.ChoiceField(
            choices=YEAR_CHOICES)
        self.fields['year_filter'].required = False


class FilterForm(forms.Form):

    '''Year, Indicators and Memberstates filter form on Query Data page'''

    year_filter_field = forms.ChoiceField(choices=[])
    indicator_filter_field = forms.ChoiceField(choices=[])
    memberstate_filter_field = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        memberstates_qs = MemberState.objects.filter(
            memberstate_status=True).values().order_by('member_state')

        MEMBERSTATE_CHOICES = sorted(tuple(set(
            [(q['id'], q['member_state']) for q in memberstates_qs])))

        indicators_qs = Indicator.objects.filter(
            status='Active', focus_area__focusarea_status=True).values()

        # currency_indicators = list(indicators_qs.filter(
        #     data_type=3).values_list("id", flat=True))

        # print(currency_indicators)

        INDICATOR_CHOICES = sorted(tuple(set(
            [(q['id'], q['label']) for q in indicators_qs])))

        years_qs = []

        if get_published_years():
            years_qs = get_published_years()

        else:
            #years_qs = [{'reporting_year': Get_Reporting_Year()}]
            years_qs = [Get_Reporting_Year()]

        #years_qs.insert(0, {'reporting_year': 'Select All'})
        years_qs.insert(0,  'Select All')

        YEAR_CHOICES = tuple((),)
        for i in years_qs:
            YEAR_CHOICES += ((i, i),)
        # for i in years_qs:
        #     for k, v in i.items():
        #         YEAR_CHOICES += ((v, v),)

        MEMBERSTATE_CHOICES.insert(0, ["all", "Select All"])  # type: ignore

        # YEAR_CHOICES.insert(0, ["all", "Select All"])  # type: ignore
        INDICATOR_CHOICES.insert(0, ["all", "Select All"])  # type: ignore

        self.fields['indicator_filter_field'] = forms.MultipleChoiceField(
            choices=INDICATOR_CHOICES, widget=Select2MultipleWidget)

        self.fields['memberstate_filter_field'] = forms.MultipleChoiceField(
            choices=MEMBERSTATE_CHOICES, widget=Select2MultipleWidget)
        self.fields['year_filter_field'] = forms.MultipleChoiceField(
            choices=YEAR_CHOICES, widget=Select2MultipleWidget)

        self.fields["indicator_filter_field"].widget.attrs[
            "onchange"] = "javascript:ChangeButtonText(this.id);"

        self.fields['indicator_filter_field'].required = False
        self.fields['memberstate_filter_field'].required = False
        self.fields['year_filter_field'].required = False
