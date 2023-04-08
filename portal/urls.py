from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    #'''Home Page'''
    path('', views.index, name='index'),

    #'''Socio Economic Charts page'''
    path('socio-economic/', views.socio_economic, name='socio-economic-charts'),


    #'''Query Data page'''
    path('query-data/', views.generate_report, name='generate-report'),


    #'''About Page'''
    path('about/', views.about, name='about'),



]
