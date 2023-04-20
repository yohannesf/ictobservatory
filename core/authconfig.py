# 'authconfig.py'
from django.apps import AppConfig


class CustomAuthConfig(AppConfig):
    name = 'django.contrib.auth'
    verbose_name = 'Authentication and Authorisation'
