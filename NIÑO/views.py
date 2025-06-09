from django.shortcuts import redirect
from django.views.generic import TemplateView
from NIÑO.models import Niño
from django.shortcuts import get_object_or_404,render
from django.views import View
from datetime import timedelta
from django.http import JsonResponse
from NIÑO.modelo_deteccion import resultado_final,gen_frames_background,stop_event,deteccion_finalizada
from .models import Reporte
from threading import Thread
from datetime import datetime
import time
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


class InicioDeteccionView(TemplateView):
    template_name = 'ia.html'

    def dispatch(self, request, *args, **kwargs):



        nino_id = request.session.get('nino_id')
        if not nino_id:
            print("❌ Niño no autenticado")
            return redirect('accounts:login')


        session_key = f"deteccion_iniciada_{nino_id}"

        if not request.session.get(session_key):

            request.session[session_key] = True
            request.session.modified = True

            def run_detection():
                gen_frames_background()

            t = Thread(target=run_detection)
            t.daemon = True
            t.start()

        return super().dispatch(request, *args, **kwargs)




class FinalizarDeteccionView(View):
    def get(self, request, *args, **kwargs):

        nino_id = request.session.get('nino_id')
        if not nino_id:
            return JsonResponse({'error': 'No autenticado'}, status=403)

        try:
            nino = Niño.objects.get(id=nino_id)
        except Niño.DoesNotExist:
            return JsonResponse({'error': 'Niño no encontrado'}, status=404)
        stop_event.set()
        print("🛑 Señal enviada para detener la detección")
        if not deteccion_finalizada.wait(timeout=60):
            return JsonResponse({'error': 'La detección no ha terminado a tiempo.'}, status=408)

        global resultado_final

        if not resultado_final or "somnolencias" not in resultado_final:
            return JsonResponse({'error': 'No se obtuvieron resultados válidos de la detección'}, status=500)

        titulo_auto = f"Evaluación del {datetime.now().strftime('%d/%m/%Y')}"
        try:
            Reporte.objects.create(
                niño=nino,
                titulo=titulo_auto,
                somnolencias=resultado_final.get("somnolencias", 0),
                distracciones=resultado_final.get("distracciones", 0),
                tiempos_somnolencia=resultado_final.get("tiempos_somnolencia", []),
                tiempos_distraccion=resultado_final.get("tiempos_distraccion", []),
                duracion_evaluacion=timedelta(seconds=resultado_final.get("duracion_total", 0))
            )
        except Exception as e:
            return JsonResponse({'error': 'Error al guardar el reporte'}, status=500)
        session_key = f"deteccion_iniciada_{nino_id}"
        request.session[session_key] = False
        request.session.modified = True

        resultado = resultado_final.copy()
        resultado_final.clear()
        deteccion_finalizada.clear()

        return JsonResponse(resultado)

