
from crispy_forms.helper import FormHelper
from decimal import Decimal
import json
from typing import List, Tuple

from django import forms
from django.db.models import Count
from django.core.validators import MaxLengthValidator
from django.forms import BaseModelFormSet, modelformset_factory
from core.views import Get_Reporting_Year

from portaldata.admin import IndicatorAssignedAdmin
from portaldata.widgets import DateEntry
from ..app_settings import DATE_INPUT_FORMAT, SURVEY_FIELD_VALIDATORS
from ..validators import validate_ratio, PERCENTAGE_VALIDATOR


from ..models import AssignedIndicator, Currency, ExchangeRateData, GeneralIndicator, GeneralIndicatorData, Indicator, FocusArea, IndicatorData, DATA_TYPE, Organisation


def make_choices(question: Indicator) -> List[Tuple[str, str]]:
    choices = []
    for choice in question.choices.split(','):  # type: ignore
        choice = choice.strip()
        choices.append((choice.replace(' ', '_').lower(), choice))
    choices.insert(0, ('', 'Choose..'))
    return choices


# Returns the next indicator number for the selected focus area


def next_indicator_number():

    # count the number of indicators per focus area and group them
    # result = [(id, "Abbreviation",#)] -> [(1,"ICT-ECOM", 4)]
    mycount = FocusArea.objects.values_list('id', 'abbreviation').order_by(
        'id').annotate(c=Count('indicator'))

    # Use list comprehension to covert the previous list into a Tuples list then convert it into Dictionary
    # result = [{id:"ICT-ECON-5"}]
    next_indicator_num = dict(
        [(x[0], x[1] + "-" + str(x[2]+1)) for x in mycount])

    # result = dict(next_indicator_num)
    # Convert the dictionary to JSON (for use in JavaScript)
    resultJson = json.dumps(next_indicator_num)

    return resultJson


class FocusAreaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.sn = FocusArea.next_sn(FocusArea)  # type: ignore
        self.fields['description'] = forms.CharField(
            widget=forms.Textarea(attrs={'rows': 3}), required=False)
        #self.fields['sn'].widget.attrs['readonly'] = True
        self.fields['sn'].widget.attrs['readonly'] = True
        self.fields['sn'].widget.attrs['class'] = 'form-control'

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-6'

    class Meta:
        model = FocusArea
        exclude = ('created_by', 'updated_by',
                   'next_indicator_num',)


class IndicatorForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.next_indicator_num = next_indicator_number()

        self.fields['definition'] = forms.CharField(
            widget=forms.Textarea(attrs={'rows': 3}))

        self.fields['choices'] = forms.CharField(
            widget=forms.Textarea(attrs={'rows': 2}))

        self.fields['choices'].required = False

        #self.fields['type_of_currency'].required = False

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-6'

    class Meta:
        model = Indicator
        exclude = ('type_of_currency', 'created_by',
                   'updated_by',  'attachment')


# class BaseFormSet(BaseModelFormSet):
#     def __init__(self, *args, **kwargs):
#         super(BaseFormSet, self).__init__(*args, **kwargs)
#         for form in self.forms:
#             form.empty_permitted = False


class IndicatorAssignEntryForm(forms.ModelForm):
    class Meta:
        model = AssignedIndicator
        fields = ['indicator', 'assigned_to_organisation']

    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial", {})

        super(IndicatorAssignEntryForm, self).__init__(*args, **kwargs)

        filter_active_orgs = Organisation.objects.filter(
            organisation_status=True)

        self.fields['assigned_to_organisation'].queryset = filter_active_orgs


class IndicatorAssignEditForm(forms.ModelForm):

    class Meta:
        model = AssignedIndicator
        # fields = ['id', 'indicator', 'value', 'comments', 'attachment']
        exclude = ('updated_by',)
        # fields = "__all__"

    def __init__(self, *args, **kwargs):

        super(IndicatorAssignEditForm, self).__init__(*args, **kwargs)

        v = self.instance  # type: ignore

        filter_active_orgs = Organisation.objects.filter(
            organisation_status=True)

        self.fields['assigned_to_organisation'].queryset = filter_active_orgs
