from django import forms
from ..models import IndicatorDataValidationHistory


class IndicatorDataRevision(forms.ModelForm):
    class Meta:
        model = IndicatorDataValidationHistory
        fields = ['comments']
