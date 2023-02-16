from crispy_forms.helper import FormHelper
from decimal import Decimal
import json
from typing import List, Tuple

from django import forms
from django.db.models import Count
from django.core.validators import MaxLengthValidator
from django.forms import BaseModelFormSet
from core.views import Get_Reporting_Year

from portaldata.admin import IndicatorAssignedAdmin
from portaldata.widgets import DateEntry
from ..app_settings import DATE_INPUT_FORMAT, SURVEY_FIELD_VALIDATORS
from ..validators import validate_ratio, PERCENTAGE_VALIDATOR


from ..models import AssignedIndicator, Currency, ExchangeRateData, Indicator, FocusArea, IndicatorData, DATA_TYPE, Organisation


def make_choices(question: Indicator) -> List[Tuple[str, str]]:
    choices = []
    for choice in question.choices.split(','):  # type: ignore
        choice = choice.strip()
        choices.append((choice.replace(' ', '_').lower(), choice))
    choices.insert(0, ('', 'Choose..'))
    return choices


class IndicatorDataEntryForm(forms.ModelForm):
    class Meta:
        model = IndicatorData
        fields = ['indicator', 'ind_value',
                  'comments', 'attachment', 'value_NA']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 1, 'cols': 30}),
            'value_NA': forms.CheckboxInput(),
        }
        # fields = '__all__'

    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial", {})

        super(IndicatorDataEntryForm, self).__init__(*args, **kwargs)

       # self.fields['created_by'] =

        for k, v in initial.items():
            if v.data_type == DATA_TYPE.select:
                choices = make_choices(v)
                self.fields['ind_value'] = forms.ChoiceField(
                    choices=choices
                )
                self.fields['ind_value'].widget.attrs.update(
                    {'class': 'form-select'})
            elif v.data_type == DATA_TYPE.number:
                self.fields['ind_value'] = forms.IntegerField(
                )
                self.fields['ind_value'].widget.attrs.update(
                    {'class': 'form-control'})
            elif v.data_type == DATA_TYPE.percentage:
                # self.fields['ind_value'] = forms.DecimalField(max_digits=6,
                #                                           decimal_places=2, validators=PERCENTAGE_VALIDATOR)
                # print("here")

                self.fields['ind_value'] = forms.DecimalField(max_digits=5,
                                                              decimal_places=2)  # type: ignore
                self.fields['ind_value'].widget.attrs.update(
                    {'class': 'form-control'})
            elif v.data_type == DATA_TYPE.currency:
                self.fields['ind_value'] = forms.DecimalField(
                    max_digits=20, decimal_places=4)
                self.fields['ind_value'].widget.attrs.update(
                    {'class': 'form-control'})

            elif v.data_type == DATA_TYPE.decimal:
                # print(type(self.fields['ind_value']))
                self.fields['ind_value'] = forms.DecimalField(
                    max_digits=6, decimal_places=2)
                # print(type(self.fields['ind_value']))
                self.fields['ind_value'].widget.attrs.update(
                    {'class': 'form-control'})

            elif v.data_type == DATA_TYPE.url:
                self.fields['ind_value'] = forms.URLField(
                    validators=[MaxLengthValidator(
                        SURVEY_FIELD_VALIDATORS['max_length']['url'])]
                )
                self.fields['ind_value'].widget.attrs.update(
                    {'class': 'form-control'})

            elif v.data_type == DATA_TYPE.email:
                self.fields['ind_value'] = forms.EmailField(
                    validators=[MaxLengthValidator(
                        SURVEY_FIELD_VALIDATORS['max_length']['email'])])
                self.fields['ind_value'].widget.attrs.update(
                    {'class': 'form-control'})

            elif v.data_type == DATA_TYPE.date:
                self.fields['ind_value'] = forms.DateField(
                    # widget=DateSurvey(),
                    input_formats=DATE_INPUT_FORMAT
                )
            elif v.data_type == DATA_TYPE.text_area:
                self.fields['ind_value'] = forms.CharField(
                    widget=forms.Textarea(attrs={'rows': 3})
                )
                self.fields['ind_value'].widget.attrs.update(
                    {'class': 'form-control'})

    # def clean(self):
    #     data = self.cleaned_data
    #     v = data['ind_value']
    #     x = Decimal(v)
    #     print(type(x))

        # validate_ratio(Decimal(data['ind_value']))
        # if data['num_values'] != data['num_average'] *3:
        #     raise forms.ValidationError('values must be three times average')


class IndicatorDataEditForm(forms.ModelForm):

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

        # for kw in kwargs:
        #     print(kw)

        # v = self.instance

        # v = kwargs.get('instance')
        # v = self.instance
        # r = kwargs.get('renderer')
        # print(r)

        super().__init__(*args, **kwargs)

        # self.fields['comments'].widget.attrs['rows'] = 1

        v = self.instance  # type: ignore

        # v.submitted

        # print(self.instance.indicator.indicatordata)

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


class ExchangeRateDataForm(forms.ModelForm):
    # field['exchange_rate_date'] = forms.DateField(
    #     widget=forms.SelectDateWidget())

    class Meta:
        model = ExchangeRateData
        fields = ['currency', 'exchange_rate',
                  'exchange_rate_date', ]

        # widgets = {
        #     'exchange_rate_date': forms.DateField(
        #         widget=forms.SelectDateWidget()),

        # }

    def __init__(self, *args, **kwargs):

        ms = kwargs.pop('ms', None)
        ins = kwargs.get("instance", {})

        #ins = kwargs.pop('instance', None)

        super(ExchangeRateDataForm, self).__init__(*args, **kwargs)

        self.fields['currency'] = forms.ModelChoiceField(queryset=Currency.objects.filter(
            member_state=ms))
        self.fields['currency'].initial = Currency.objects.get(
            member_state=ms)

        self.fields['exchange_rate_date'] = forms.DateField(
            widget=forms.TextInput(attrs={'type': 'date'}), required=False)

        if ins:

            if ins.submitted:  # type: ignore
                self.fields['exchange_rate'].widget.attrs['readonly'] = True
                self.fields['exchange_rate_date'].widget.attrs['readonly'] = True
                self.fields['currency'].widget.attrs['readonly'] = True
        #self.fields['currency'].enabled = False

        #self.fields['exchange_rate_date'].required = False

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
