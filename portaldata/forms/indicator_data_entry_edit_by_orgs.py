from django.core.exceptions import NON_FIELD_ERRORS
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


class IndicatorDataEntryFormOrg(forms.ModelForm):

    class Meta:
        model = IndicatorData
        fields = ['id', 'indicator', 'member_state', 'value_NA',
                  'ind_value', 'comments', 'attachment']

        widgets = {
            'comments': forms.Textarea(attrs={'rows': 1, 'cols': 30}),
            'value_NA': forms.CheckboxInput(),
        }

    def __init__(self, *args, indicator, **kwargs):

        self.indicator = indicator

        super().__init__(*args, **kwargs)

        self.fields['indicator'].initial = self.indicator

        if self.indicator.data_type == DATA_TYPE.select:
            # pass
            # print(make_choices(v))
            choices = make_choices(self.indicator)
            self.fields['ind_value'] = forms.ChoiceField(
                choices=choices
            )
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-select'})
        elif self.indicator.data_type == DATA_TYPE.number:
            self.fields['ind_value'] = forms.IntegerField()
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})

        elif self.indicator.data_type == DATA_TYPE.percentage:
            self.fields['ind_value'] = forms.DecimalField(max_digits=5,
                                                          decimal_places=2)  # type: ignore
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})

        elif self.indicator.data_type == DATA_TYPE.currency:
            self.fields['ind_value'] = forms.DecimalField(
                max_digits=20, decimal_places=4)
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})

        elif self.indicator.data_type == DATA_TYPE.decimal:
            self.fields['ind_value'] = forms.DecimalField(
                max_digits=6, decimal_places=2)
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})
        elif self.indicator.data_type == DATA_TYPE.url:
            self.fields['ind_value'] = forms.URLField(

                validators=[MaxLengthValidator(
                    SURVEY_FIELD_VALIDATORS['max_length']['url'])]
            )
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})
        elif self.indicator.data_type == DATA_TYPE.email:
            self.fields['ind_value'] = forms.EmailField(

                validators=[MaxLengthValidator(
                    SURVEY_FIELD_VALIDATORS['max_length']['email'])]
            )
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})
        elif self.indicator.data_type == DATA_TYPE.date:
            self.fields['ind_value'] = forms.DateField(
                # widget=DateSurvey(),
                input_formats=DATE_INPUT_FORMAT
            )
        elif self.indicator.data_type == DATA_TYPE.text_area:
            self.fields['ind_value'] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 1})
            )
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})

        self.fields['ind_value'].required = False

        # if (self.submitted):
        #     self.fields['ind_value'].disabled = True
        #     self.fields['comments'].disabled = True
        #     self.fields['value_NA'].disabled = True


class IndicatorDataEditFormOrg(forms.ModelForm):

    class Meta:
        model = IndicatorData
        # fields = ['id', 'indicator', 'ind_value', 'comments', 'attachment']
        exclude = ('updated_by',)
        # fields = "__all__"
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 1, 'cols': 30}),
            'value_NA': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        v = self.instance  # type: ignore

        if v.indicator.data_type == DATA_TYPE.select:
            # pass
            # print(make_choices(v))
            choices = make_choices(v.indicator)
            self.fields['ind_value'] = forms.ChoiceField(
                choices=choices
            )
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-select'})
        elif v.indicator.data_type == DATA_TYPE.number:
            self.fields['ind_value'] = forms.IntegerField()
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})
        elif v.indicator.data_type == DATA_TYPE.percentage:
            self.fields['ind_value'] = forms.DecimalField(max_digits=5,
                                                          decimal_places=2)  # type: ignore
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})

        elif v.indicator.data_type == DATA_TYPE.currency:
            self.fields['ind_value'] = forms.DecimalField(
                max_digits=20, decimal_places=4)
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})

        elif v.indicator.data_type == DATA_TYPE.decimal:
            self.fields['ind_value'] = forms.DecimalField(
                max_digits=6, decimal_places=2)
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})

        elif v.indicator.data_type == DATA_TYPE.url:
            self.fields['ind_value'] = forms.URLField(

                validators=[MaxLengthValidator(
                    SURVEY_FIELD_VALIDATORS['max_length']['url'])]
            )
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})
        elif v.indicator.data_type == DATA_TYPE.email:
            self.fields['ind_value'] = forms.EmailField(

                validators=[MaxLengthValidator(
                    SURVEY_FIELD_VALIDATORS['max_length']['email'])]
            )
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})
        elif v.indicator.data_type == DATA_TYPE.date:
            self.fields['ind_value'] = forms.DateField(
                # widget=DateSurvey(),
                input_formats=DATE_INPUT_FORMAT
            )
        elif v.indicator.data_type == DATA_TYPE.text_area:
            self.fields['ind_value'] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 1})
            )
            self.fields['ind_value'].widget.attrs.update(
                {'class': 'form-control'})

        self.fields['ind_value'].required = False

        if (v.submitted):
            self.fields['ind_value'].disabled = True
            self.fields['comments'].disabled = True
            self.fields['value_NA'].disabled = True


class GeneralIndicatorDataForm(forms.ModelForm):

    class Meta:
        model = GeneralIndicatorData
        fields = ('general_indicator', 'indicator_value')

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
            }
        }


# t = GeneralIndicator.objects.all().count()
# print(t)
# GeneralIndicatorDataFormSet = modelformset_factory(
#     GeneralIndicatorData, fields=('general_indicator', 'indicator_value'))
