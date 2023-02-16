from django.urls import path, include, re_path

from core.views import change_password

app_name = 'core'

urlpatterns = [
    path('accounts/change-password/', change_password,
         name='account_change_password'),

]
