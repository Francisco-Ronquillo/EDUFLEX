from django.urls import path
from NIÑO.views import *
app_name = 'niño'
urlpatterns = [
    path('dashboardKid/', DashboardKid.as_view(), name='dashboardKid'),
    path('juegos_recomendados/', JuegosRecomendadosView.as_view(), name='juegos_recomendados'),
    path('niveles_disgrafia/', niveles_disgrafiaView.as_view(), name='niveles_disgrafia'),
    path('juego_completar/', juego_completar_palabraView.as_view(), name='completar_palabra'),
    path('guardar_progreso/', GuardarProgresoView.as_view(), name='guardar_progreso'),
]