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
                juego_a_mostrar = "Ordena las palabras"
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
        ultimo_reporte = Reporte.objects.order_by('-id').first()
        nuevo_id = ultimo_reporte.id + 1 if ultimo_reporte else 1
        session_key = f"deteccion_iniciada_{nino_id}"
        tiempo_key = f"tiempo_inicio_deteccion_{nino_id}"

        iniciado = request.session.get(session_key, False)
        tiempo_inicio_str = request.session.get(tiempo_key)


        if iniciado and tiempo_inicio_str:
            try:
                tiempo_inicio = datetime.fromisoformat(tiempo_inicio_str)
                if datetime.now() - tiempo_inicio > timedelta(minutes=2):
                    iniciado = False
                    request.session[session_key] = False
                    request.session.pop(tiempo_key, None)
            except Exception:
                # Fallo al leer el tiempo → reiniciar por seguridad
                iniciado = False
                request.session[session_key] = False
                request.session.pop(tiempo_key, None)

        if not iniciado:
            request.session[session_key] = True
            request.session[tiempo_key] = datetime.now().isoformat()
            request.session.modified = True

            def run_detection():
                gen_frames_background(nino_id,nuevo_id)

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
                    titulo=f"Digrafia, nivel {nivel}",
                    puntaje=puntaje_real,
                    somnolencias=resultado_final.get("somnolencias", 0),
                    distracciones=resultado_final.get("distracciones", 0),
                    tiempos_somnolencia=resultado_final.get("tiempos_somnolencia", []),
                    tiempos_distraccion=resultado_final.get("tiempos_distraccion", []),
                    frames_somnolencia=resultado_final.get("frames_somnolencia", []),
                    frames_distraccion = resultado_final.get("frames_distraccion", []),
                    duracion_evaluacion=timedelta(seconds=tiempo)
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
        puntaje_real = puntaje - (puntaje * Decimal('0.90'))
        stop_event.set()
        if not deteccion_finalizada.wait(timeout=60):
            return JsonResponse({}, status=204)

        global resultado_final
        if resultado_final and "somnolencias" in resultado_final:
            Reporte.objects.create(
                niño=niño,
                titulo = f"TDA, nivel {nivel}",
                puntaje=puntaje_real,
                somnolencias=resultado_final.get("somnolencias", 0),
                distracciones=resultado_final.get("distracciones", 0),
                tiempos_somnolencia=resultado_final.get("tiempos_somnolencia", []),
                tiempos_distraccion=resultado_final.get("tiempos_distraccion", []),
                duracion_evaluacion=timedelta(seconds=tiempo)
            )
            session_key = f"deteccion_iniciada_{nino_id}"
            request.session[session_key] = False
            request.session.modified = True

            resultado_final.clear()
            deteccion_finalizada.clear()

        return JsonResponse({'estado': 'ok'})

class juego_cartasView(TemplateView):
    template_name = 'cartas.html'
    def dispatch(self, request, *args, **kwargs):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return redirect('accounts:login')
        ultimo_reporte = Reporte.objects.order_by('-id').first()
        nuevo_id = ultimo_reporte.id + 1 if ultimo_reporte else 1
        session_key = f"deteccion_iniciada_{nino_id}"
        tiempo_key = f"tiempo_inicio_deteccion_{nino_id}"

        iniciado = request.session.get(session_key, False)
        tiempo_inicio_str = request.session.get(tiempo_key)


        if iniciado and tiempo_inicio_str:
            try:
                tiempo_inicio = datetime.fromisoformat(tiempo_inicio_str)
                if datetime.now() - tiempo_inicio > timedelta(minutes=2):

                    iniciado = False
                    request.session[session_key] = False
                    request.session.pop(tiempo_key, None)
            except Exception:
                iniciado = False
                request.session[session_key] = False
                request.session.pop(tiempo_key, None)

        if not iniciado:
            request.session[session_key] = True
            request.session[tiempo_key] = datetime.now().isoformat()
            request.session.modified = True

            def run_detection():
                gen_frames_background(nino_id,nuevo_id)

            t = Thread(target=run_detection)
            t.daemon = True
            t.start()

        return super().dispatch(request, *args, **kwargs)

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


