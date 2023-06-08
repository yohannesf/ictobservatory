from django.urls import path

from portal.views.map_views import map_view
from .views.portal_home_views import index, socio_economic, about
from .views.querydata_views import generate_report

app_name = 'portal'

urlpatterns = [
    #'''Home Page'''
    path('', index, name='index'),

    #'''Socio Economic Charts page'''
    path('socio-economic/', socio_economic, name='socio-economic-charts'),


    #'''Query Data page'''
    path('query-data/', generate_report, name='generate-report'),


    #'''About Page'''
    path('about/', about, name='about'),


    path('map/', map_view, name='map'),



]
