from django.contrib import admin
from NIÑO.models import *
@admin.register(Niño)
class NiñoAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'genero', 'usuario', 'email', 'fecha_nac', 'especialidad','codigo')
    search_fields = ('nombres', 'apellidos', 'usuario', 'email')
    list_filter = ('genero', 'especialidad')
@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'niño', 'puntaje', 'distracciones', 'fecha', 'duracion_evaluacion')
    search_fields = ('titulo', 'niño__nombres', 'niño__apellidos')
    list_filter = ('fecha',)
    ordering = ('-fecha',)