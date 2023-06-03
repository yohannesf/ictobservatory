"""
A form to be used by Member States for data entry. It contains indicator data entry and exchange rate data entry forms.
"""

from datetime import date
import datetime
from crispy_forms.helper import FormHelper

from typing import List, Tuple

from django import forms

from django.core.validators import MaxLengthValidator


from ..app_settings import DATE_INPUT_FORMAT, SURVEY_FIELD_VALIDATORS


from ..models import (
    Currency,
    ExchangeRateData,
    Indicator,
    FocusArea,
    IndicatorData,
    DATA_TYPE,
)


def make_choices(question: Indicator) -> List[Tuple[str, str]]:
    choices = []
    for choice in question.choices.split(","):  # type: ignore
        choice = choice.strip()
        choices.append((choice.replace(" ", "_"), choice))
    choices.insert(0, ("", "------"))
    return choices


class IndicatorDataEntryForm(forms.ModelForm):
    """
    Form for entering indicator data for Member States
    This will be used for new data entry.
    If data is entered and saved once, the code below will handle the data entry.
    """

    class Meta:
        model = IndicatorData
        fields = ["indicator", "ind_value",
                  "comments", "attachment", "value_NA"]
        widgets = {
            "comments": forms.Textarea(attrs={"rows": 1, "cols": 30}),
            "value_NA": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial", {})

        super(IndicatorDataEntryForm, self).__init__(*args, **kwargs)

        self.fields["value_NA"].widget.attrs[
            "onclick"] = "javascript:toggleIndValue(this.id);"

        for k, v in initial.items():
            if v.data_type == DATA_TYPE.select:
                choices = make_choices(v)
                self.fields["ind_value"] = forms.ChoiceField(choices=choices)
                self.fields["ind_value"].widget.attrs.update(
                    {"class": "form-select"})
            elif v.data_type == DATA_TYPE.number:
                self.fields["ind_value"] = forms.IntegerField()
                self.fields["ind_value"].widget.attrs.update(
                    {"class": "form-control"})
            elif v.data_type == DATA_TYPE.percentage:
                self.fields["ind_value"] = forms.DecimalField(
                    max_digits=5, decimal_places=2
                )  # type: ignore

                self.fields["ind_value"].widget.attrs.update(
                    {"class": "form-control"})
            elif v.data_type == DATA_TYPE.currency:
                self.fields["ind_value"] = forms.DecimalField(
                    max_digits=20, decimal_places=4
                )
                self.fields["ind_value"].widget.attrs.update(
                    {"class": "form-control"})

            elif v.data_type == DATA_TYPE.decimal:
                self.fields["ind_value"] = forms.DecimalField(
                    max_digits=6, decimal_places=2
                )

                self.fields["ind_value"].widget.attrs.update(
                    {"class": "form-control"})

            elif v.data_type == DATA_TYPE.url:
                self.fields["ind_value"] = forms.URLField(
                    validators=[
                        MaxLengthValidator(
                            SURVEY_FIELD_VALIDATORS["max_length"]["url"])
                    ]
                )
                self.fields["ind_value"].widget.attrs.update(
                    {"class": "form-control"})

            elif v.data_type == DATA_TYPE.email:
                self.fields["ind_value"] = forms.EmailField(
                    validators=[
                        MaxLengthValidator(
                            SURVEY_FIELD_VALIDATORS["max_length"]["email"]
                        )
                    ]
                )
                self.fields["ind_value"].widget.attrs.update(
                    {"class": "form-control"})

            elif v.data_type == DATA_TYPE.date:
                self.fields["ind_value"] = forms.DateField(
                    input_formats=DATE_INPUT_FORMAT
                )
            elif v.data_type == DATA_TYPE.text_area:
                self.fields["ind_value"] = forms.CharField(
                    widget=forms.Textarea(attrs={"rows": 3})
                )
                self.fields["ind_value"].widget.attrs.update(
                    {"class": "form-control"})


class IndicatorDataEditForm(forms.ModelForm):

    """
    Form for entering indicator data for Member States
    This will be used for editing data entry.
    If data is entered as new, the code above will handle the data entry.
    """

    class Meta:
        model = IndicatorData

        exclude = ("updated_by",)

        widgets = {
            "comments": forms.Textarea(attrs={"rows": 1, "cols": 30}),
            "value_NA": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        v = self.instance  # type: ignore

        self.fields["value_NA"].widget.attrs[
            "onclick"
        ] = "javascript:toggleIndValue(this.id);"

        if v.indicator.data_type == DATA_TYPE.select:
            choices = make_choices(v.indicator)
            self.fields["ind_value"] = forms.ChoiceField(choices=choices)
            self.fields["ind_value"].widget.attrs.update(
                {"class": "form-select"})

        elif v.indicator.data_type == DATA_TYPE.number:
            self.fields["ind_value"] = forms.IntegerField()
            self.fields["ind_value"].widget.attrs.update(
                {"class": "form-control"})

        elif v.indicator.data_type == DATA_TYPE.percentage:
            self.fields["ind_value"] = forms.DecimalField(
                max_digits=5, decimal_places=2
            )  # type: ignore
            self.fields["ind_value"].widget.attrs.update(
                {"class": "form-control"})

        elif v.indicator.data_type == DATA_TYPE.currency:
            self.fields["ind_value"] = forms.DecimalField(
                max_digits=20, decimal_places=4
            )
            self.fields["ind_value"].widget.attrs.update(
                {"class": "form-control"})

        elif v.indicator.data_type == DATA_TYPE.decimal:
            self.fields["ind_value"] = forms.DecimalField(
                max_digits=6, decimal_places=2
            )
            self.fields["ind_value"].widget.attrs.update(
                {"class": "form-control"})

        elif v.indicator.data_type == DATA_TYPE.url:
            self.fields["ind_value"] = forms.URLField(
                validators=[
                    MaxLengthValidator(
                        SURVEY_FIELD_VALIDATORS["max_length"]["url"])
                ]
            )
            self.fields["ind_value"].widget.attrs.update(
                {"class": "form-control"})
        elif v.indicator.data_type == DATA_TYPE.email:
            self.fields["ind_value"] = forms.EmailField(
                validators=[
                    MaxLengthValidator(
                        SURVEY_FIELD_VALIDATORS["max_length"]["email"])
                ]
            )
            self.fields["ind_value"].widget.attrs.update(
                {"class": "form-control"})
        elif v.indicator.data_type == DATA_TYPE.date:
            self.fields["ind_value"] = forms.DateField(
                input_formats=DATE_INPUT_FORMAT)
        elif v.indicator.data_type == DATA_TYPE.text_area:
            self.fields["ind_value"] = forms.CharField(
                widget=forms.Textarea(attrs={"rows": 1})
            )
            self.fields["ind_value"].widget.attrs.update(
                {"class": "form-control"})

        self.fields["ind_value"].required = False

        if v.value_NA == True:
            self.fields["ind_value"].disabled = True

        if v.submitted:
            self.fields["ind_value"].disabled = True
            self.fields["comments"].disabled = True
            self.fields["value_NA"].disabled = True


class ExchangeRateDataForm(forms.ModelForm):

    """Form for entering Exchange Rate Data"""

    class Meta:
        model = ExchangeRateData
        fields = [
            "currency",
            "exchange_rate",
            "exchange_rate_date",
        ]

    def __init__(self, *args, **kwargs):
        ms = kwargs.pop("ms", None)
        ins = kwargs.get("instance", {})

        super(ExchangeRateDataForm, self).__init__(*args, **kwargs)

        self.fields["currency"] = forms.ModelChoiceField(
            queryset=Currency.objects.filter(member_state=ms)
        )
        self.fields["currency"].initial = Currency.objects.get(member_state=ms)

        self.fields["exchange_rate_date"] = forms.DateField(
            widget=forms.TextInput(attrs={"type": "date"}), required=False
        )

        if ins:
            if ins.submitted:  # type: ignore
                self.fields["exchange_rate"].widget.attrs["readonly"] = True
                self.fields["exchange_rate_date"].widget.attrs["readonly"] = True
                self.fields["currency"].widget.attrs["readonly"] = True

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-4"

    def clean(self):
        cleaned_data = super().clean()
        exchange_rate_date = cleaned_data.get("exchange_rate_date")

        if exchange_rate_date:
            if datetime.date.today() < exchange_rate_date:
                raise forms.ValidationError("Date cannot be in the future.")
