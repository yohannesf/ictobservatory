import os
from django import forms
from django.conf import settings

filepath = os.path.join(settings.BASE_DIR, 'templates')


class DateEntry(forms.DateTimeInput):
    print(filepath)

    #newfilepath = "D:\\OneDrive\\Documents\\sadc_local\\templates\\widgets\\datepicker.html"
    template_name = ('portaldata/widgets/datepicker.html')
    #template_name = newfilepath
