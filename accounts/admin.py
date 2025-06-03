from django.contrib import admin
from accounts.models import CodigoRecuperacion

@admin.register(CodigoRecuperacion)
class CodigoRecuperacionAdmin(admin.ModelAdmin):
    list_display = ('email', 'codigo', 'creado_en', 'expirado_display')
    search_fields = ('email', 'codigo')
    list_filter = ('creado_en',)

    def expirado_display(self, obj):
        return obj.expirado()
    expirado_display.boolean = True
    expirado_display.short_description = '¿Expirado?'



