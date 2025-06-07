from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from NIÑO.models import Niño
from django.shortcuts import get_object_or_404,render

class DashboardKid(TemplateView):
    template_name = 'dashboardKid.html'

    def dispatch(self, request, *args, **kwargs):
        if 'nino_id' not in request.session:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)


class JuegosRecomendadosView(View):
    def get(self, request):
        nino_id = request.session.get('nino_id')

        if not nino_id:
            return redirect('accounts:login')

        try:
            nino = get_object_or_404(Niño, pk=nino_id)
            especialidad_niño = nino.especialidad

            juego_a_mostrar = None

            if especialidad_niño == 'D':
                juego_a_mostrar = "Traza y gana"
            elif especialidad_niño == 'DC':
                juego_a_mostrar = "Cuenta conmigo"
            elif especialidad_niño == 'T':
                juego_a_mostrar = "Desafío de concentración"

            return render(request, 'juegos.html', {'juego': juego_a_mostrar})

        except Niño.DoesNotExist:
            return render(request, 'juegos.html', {'juego': None})

class niveles_disgrafiaView(TemplateView):
    template_name = 'niveles_disgrafia.html'