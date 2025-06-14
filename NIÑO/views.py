from django.shortcuts import redirect, get_object_or_404, render
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal
from .models import ProgresoNiño
from NIÑO.models import Niño,Reporte
from threading import Thread
from NIÑO.modelo_deteccion import resultado_final,gen_frames_background,stop_event,deteccion_finalizada
from datetime import datetime
from datetime import timedelta
from .models import ProgresoNiño, ProgresoCartas



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


class niveles_disgrafiaView(View):
    def get(self, request):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return redirect('accounts:login')
        niño = Niño.objects.get(pk=nino_id)
        progreso, _ = ProgresoNiño.objects.get_or_create(niño=niño)
        return render(request, 'niveles_disgrafia.html', {
            'nivel_desbloqueado': progreso.nivel_desbloqueado
        })


class juego_completar_palabraView(TemplateView):
    template_name = 'completar_palabra.html'

    def dispatch(self, request, *args, **kwargs):

        nino_id = request.session.get('nino_id')
        if not nino_id:
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


@method_decorator(csrf_exempt, name='dispatch')
class GuardarProgresoView(View):
    def post(self, request):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return JsonResponse({}, status=204)

        try:

            nivel = int(request.POST.get('nivel', 0))
            puntaje = Decimal(request.POST.get('puntaje', '0'))
            tiempo = int(request.POST.get('tiempo', 0))

            niño = Niño.objects.get(pk=nino_id)
            progreso, _ = ProgresoNiño.objects.get_or_create(niño=niño)

            if nivel + 1 > progreso.nivel_desbloqueado:
                progreso.nivel_desbloqueado = nivel + 1
            progreso.puntaje_total += puntaje
            progreso.tiempo_total += tiempo
            progreso.save()
            puntaje_real=puntaje-(puntaje* Decimal('0.90'))

            stop_event.set()
            if not deteccion_finalizada.wait(timeout=60):
                return JsonResponse({}, status=204)

            global resultado_final
            if resultado_final and "somnolencias" in resultado_final:
                Reporte.objects.create(
                    niño=niño,
                    titulo=f"Evaluación del {datetime.now().strftime('%d/%m/%Y')}",
                    puntaje=puntaje_real,
                    somnolencias=resultado_final.get("somnolencias", 0),
                    distracciones=resultado_final.get("distracciones", 0),
                    tiempos_somnolencia=resultado_final.get("tiempos_somnolencia", []),
                    tiempos_distraccion=resultado_final.get("tiempos_distraccion", []),
                    duracion_evaluacion=timedelta(seconds=resultado_final.get("duracion_total", 0))
                )
                session_key = f"deteccion_iniciada_{nino_id}"
                request.session[session_key] = False
                request.session.modified = True

                resultado_final.clear()
                deteccion_finalizada.clear()

            return JsonResponse({}, status=204)  # Todo bien, sin contenido

        except Exception:
            return JsonResponse({}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class GuardarProgresoCartasView(View):
    def post(self, request):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return JsonResponse({'error': 'No autenticado'}, status=403)

        nivel = int(request.POST.get('nivel', 0))
        puntaje = int(request.POST.get('puntaje', 0))
        tiempo = int(request.POST.get('tiempo', 0))

        niño = Niño.objects.get(pk=nino_id)
        progreso, _ = ProgresoCartas.objects.get_or_create(niño=niño)

        if nivel + 1 > progreso.nivel_desbloqueado:
            progreso.nivel_desbloqueado = nivel + 1

        progreso.puntaje_total += puntaje
        progreso.tiempo_total += tiempo
        progreso.save()

        return JsonResponse({'estado': 'ok'})

class juego_cartasView(TemplateView):
    template_name = 'cartas.html'

class NivelesCartasView(View):
    def get(self, request):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return redirect('accounts:login')

        niño = Niño.objects.get(pk=nino_id)
        progreso, _ = ProgresoCartas.objects.get_or_create(niño=niño)

        return render(request, 'niveles_cartas.html', {
            'nivel_desbloqueado': progreso.nivel_desbloqueado
        })


