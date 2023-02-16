from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.index, name='index'),
    path('socio-economic/', views.socio_economic, name='socio-economic-charts'),
    path('query-data/', views.generate_report, name='generate-report'),

    # path('chart/', views.bar_chart, name='chart'),
    # path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    # path('summary/<int:pk>/', views.SummaryResponseSurveyView.as_view(),
    #      name='summary'),
    #path('highchart/', views.highchart, name='highchart'),

]
