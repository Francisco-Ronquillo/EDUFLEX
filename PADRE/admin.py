from django.contrib import admin
from PADRE.models import *
@admin.register(Padre)
class PadreAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'genero', 'usuario', 'email', 'fecha_nac' )
    search_fields = ('nombres', 'apellidos', 'usuario', 'email')

