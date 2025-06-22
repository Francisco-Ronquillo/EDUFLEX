from django.urls import path
from PADRE.views import *
app_name = 'padre'
urlpatterns = [
path('dashboardDad/',DashboardDad.as_view(),name='dashboardDad'),
path('reportKid/',reportKid.as_view(),name='reportKid'),
path('desvincular-nino/<int:pk>/', DesvincularNinoView.as_view(), name='desvincular_nino'),
path('report_total/<int:pk>/',reportTotal.as_view(),name='report_total'),
path('verReporte/<int:pk>/',verReporte.as_view(),name='verReporte'),
path('estadisticas_generales', estadisticasGenerales.as_view(),name='estadisticas_generales'),
]