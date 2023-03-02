from django import forms
from ..models import IndicatorDataValidationHistory


class IndicatorDataRevision(forms.ModelForm):
    '''
    During indicator data revision request, 
    this form is used as a modal to accept any comments that will be shared with the responsible person
    '''
    class Meta:
        model = IndicatorDataValidationHistory
        fields = ['comments']
