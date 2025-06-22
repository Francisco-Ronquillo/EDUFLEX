from django.urls import path
from NIÑO.views import *

app_name = 'niño'

urlpatterns = [
    path('dashboardKid/', DashboardKid.as_view(), name='dashboardKid'),
    path('juegos_recomendados/', JuegosRecomendadosView.as_view(), name='juegos_recomendados'),
    path('niveles_disgrafia/', niveles_disgrafiaView.as_view(), name='niveles_disgrafia'),
    path('juego_completar/', juego_completar_palabraView.as_view(), name='completar_palabra'),
    path('guardar_progreso/', GuardarProgresoView.as_view(), name='guardar_progreso'),
    path('guardar_progreso_cartas/', GuardarProgresoCartasView.as_view(), name='guardar_progreso_cartas'),
    path('juego_cartas/', juego_cartasView.as_view(), name='juego_cartas'),
    path('niveles_cartas/', NivelesCartasView.as_view(), name='niveles_cartas'),
    path('preferencias/', PreferenciasUsuarioView.as_view(), name='preferencias'),
    path('editar-perfil/', EditarPerfilView.as_view(), name='editar_perfil'),
    path('guardar_progreso_multiplicacion/', GuardarProgresoMultiplicacionView.as_view(), name='guardar_progreso_multiplicacion'),
    path('juego_multiplicacion/', JuegoMultiplicacionView.as_view(), name='juego_multiplicacion'),
    path('niveles_discalculia/', NivelesDiscalculiaView.as_view(), name='niveles_discalculia'),
    path('cerrar_juego/', cerrar_juegoView.as_view(), name='cerrar_juego'),
]
