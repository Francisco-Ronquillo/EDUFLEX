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
from .models import ProgresoNiño, ProgresoCartas,ProgresoDiscalculia
from .models import PreferenciasUsuario
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



class DashboardKid(TemplateView):
    template_name = 'dashboardKid.html'

    def dispatch(self, request, *args, **kwargs):
        if 'nino_id' not in request.session:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def formatear_tiempo(td: timedelta) -> str:
        total_segundos = int(td.total_seconds())
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        segundos = total_segundos % 60

        partes = []
        if horas > 0:
            partes.append(f"{horas}h")
        if minutos > 0 or horas > 0:
            partes.append(f"{minutos}m")
        partes.append(f"{segundos}s")

        return " ".join(partes)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nino_id = self.request.session.get('nino_id')
        niño = Niño.objects.get(pk=nino_id)
        context['niño'] = niño

        total_niveles = 5

        # Obtener progreso según especialidad
        if niño.especialidad == 'T':
            progreso = ProgresoCartas.objects.filter(niño=niño).first()
        else:
            progreso = ProgresoNiño.objects.filter(niño=niño).first()

        nivel_desbloqueado = progreso.nivel_desbloqueado if progreso else 1

        # Obtener todos los reportes válidos con puntaje >= 70
        reportes_validos = Reporte.objects.filter(niño=niño, puntaje__gte=70)

        niveles_completados = set()
        records_dict = {}

        for rep in reportes_validos:
            try:
                nivel = int(rep.titulo.split()[-1])
            except:
                continue

            niveles_completados.add(nivel)

            if nivel not in records_dict:
                records_dict[nivel] = {
                    'nivel': nivel,
                    'puntaje': int(rep.puntaje),
                    'tiempo': self.formatear_tiempo(rep.duracion_evaluacion),
                    'duracion': rep.duracion_evaluacion
                }
            else:
                record_actual = records_dict[nivel]
                puntaje_actual = record_actual['puntaje']
                duracion_actual = record_actual['duracion']

                nuevo_puntaje = int(rep.puntaje)
                nueva_duracion = rep.duracion_evaluacion

                if (
                        nuevo_puntaje > puntaje_actual
                        or (nuevo_puntaje == puntaje_actual and nueva_duracion < duracion_actual)
                ):
                    records_dict[nivel] = {
                        'nivel': nivel,
                        'puntaje': nuevo_puntaje,
                        'tiempo': self.formatear_tiempo(nueva_duracion),
                        'duracion': nueva_duracion
                    }

        niveles_completados_count = len(niveles_completados)
        progreso_porcentaje = int((niveles_completados_count / total_niveles) * 100)

        # Convertir a lista ordenada
        records = sorted([
            {k: v for k, v in record.items() if k != 'duracion'}
            for record in records_dict.values()
        ], key=lambda x: x['nivel'])

        context.update({
            'niño': niño,  # ✅ Este es el cambio clave
            'progreso_completado': niveles_completados_count,
            'total_niveles': total_niveles,
            'progreso_porcentaje': progreso_porcentaje,
            'records': records,
            'niveles_completados': niveles_completados_count
        })

        return context


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

        session_key = f"deteccion_iniciada_{nino_id}"
        tiempo_key = f"tiempo_inicio_deteccion_{nino_id}"

        iniciado = request.session.get(session_key, False)
        tiempo_inicio_str = request.session.get(tiempo_key)

        # Si ya está iniciado y excedió 2 minutos → reiniciar
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

            # 🔵 CREAR REPORTE VACÍO
            niño = Niño.objects.get(pk=nino_id)
            nuevo_reporte = Reporte.objects.create(niño=niño)
            request.session['reporte_id'] = nuevo_reporte.id  # 🟢 Guardamos en sesión

            def run_detection():
                gen_frames_background(nino_id, nuevo_reporte.id)  # usamos ID real

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
            puntaje_real = Decimal(puntaje)

            niño = Niño.objects.get(pk=nino_id)
            progreso, _ = ProgresoNiño.objects.get_or_create(niño=niño)

            # Actualizar progreso
            if puntaje >= 70:
                if nivel + 1 > progreso.nivel_desbloqueado:
                    progreso.nivel_desbloqueado = nivel + 1

            progreso.puntaje_total += puntaje
            progreso.tiempo_total += tiempo
            progreso.save()

            # 🔵 Recuperar reporte ya creado
            reporte_id = request.session.get('reporte_id')
            if not reporte_id:
                return JsonResponse({}, status=400)

            stop_event.set()
            if not deteccion_finalizada.wait(timeout=60):
                return JsonResponse({}, status=204)

            global resultado_final
            if resultado_final and "somnolencias" in resultado_final:
                reporte = Reporte.objects.get(pk=reporte_id)
                reporte.titulo = f"Digrafia, nivel {nivel}"
                reporte.puntaje = puntaje_real
                reporte.somnolencias = resultado_final.get("somnolencias", 0)
                reporte.distracciones = resultado_final.get("distracciones", 0)
                reporte.tiempos_somnolencia = resultado_final.get("tiempos_somnolencia", [])
                reporte.tiempos_distraccion = resultado_final.get("tiempos_distraccion", [])
                reporte.frames_somnolencia = resultado_final.get("frames_somnolencia", [])
                reporte.frames_distraccion = resultado_final.get("frames_distraccion", [])
                reporte.duracion_evaluacion = timedelta(seconds=tiempo)
                reporte.save()

                # Limpiar sesión
                request.session[f"deteccion_iniciada_{nino_id}"] = False
                request.session.pop('reporte_id', None)
                request.session.modified = True

                resultado_final.clear()
                deteccion_finalizada.clear()

            return JsonResponse({}, status=204)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



@method_decorator(csrf_exempt, name='dispatch')
class GuardarProgresoCartasView(View):
    def post(self, request):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return JsonResponse({'error': 'No autenticado'}, status=403)

        try:
            nivel = int(request.POST.get('nivel', 0))
            puntaje = int(request.POST.get('puntaje', 0))
            tiempo = int(request.POST.get('tiempo', 0))
            puntaje_real = Decimal(puntaje)

            niño = Niño.objects.get(pk=nino_id)
            progreso, _ = ProgresoCartas.objects.get_or_create(niño=niño)

            if puntaje >= 70:
                if nivel + 1 > progreso.nivel_desbloqueado:
                    progreso.nivel_desbloqueado = nivel + 1

            progreso.puntaje_total += puntaje
            progreso.tiempo_total += tiempo
            progreso.save()

            # ✅ Obtener el ID del reporte previamente creado
            reporte_id = request.session.get('reporte_id')
            if not reporte_id:
                return JsonResponse({'error': 'ID de reporte no encontrado'}, status=400)

            stop_event.set()
            if not deteccion_finalizada.wait(timeout=60):
                return JsonResponse({}, status=204)

            global resultado_final
            if resultado_final and "somnolencias" in resultado_final:
                reporte = Reporte.objects.get(pk=reporte_id)
                reporte.titulo = f"TDA, nivel {nivel}"
                reporte.puntaje = puntaje_real
                reporte.somnolencias = resultado_final.get("somnolencias", 0)
                reporte.distracciones = resultado_final.get("distracciones", 0)
                reporte.tiempos_somnolencia = resultado_final.get("tiempos_somnolencia", [])
                reporte.tiempos_distraccion = resultado_final.get("tiempos_distraccion", [])
                reporte.frames_somnolencia = resultado_final.get("frames_somnolencia", [])
                reporte.frames_distraccion = resultado_final.get("frames_distraccion", [])
                reporte.duracion_evaluacion = timedelta(seconds=tiempo)
                reporte.save()

                request.session[f"deteccion_iniciada_{nino_id}"] = False
                request.session.pop('reporte_id', None)
                request.session.modified = True

                resultado_final.clear()
                deteccion_finalizada.clear()

            return JsonResponse({'estado': 'ok'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class juego_cartasView(TemplateView):
    template_name = 'cartas.html'

    def dispatch(self, request, *args, **kwargs):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return redirect('accounts:login')

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


            niño = Niño.objects.get(pk=nino_id)
            nuevo_reporte = Reporte.objects.create(niño=niño)
            request.session['reporte_id'] = nuevo_reporte.id

            def run_detection():
                gen_frames_background(nino_id, nuevo_reporte.id)

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


@method_decorator(csrf_exempt, name='dispatch')
class PreferenciasUsuarioView(View):

    def get(self, request):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return JsonResponse({'error': 'No autenticado'}, status=403)

        try:
            niño = Niño.objects.get(pk=nino_id)
            preferencias, _ = PreferenciasUsuario.objects.get_or_create(niño=niño)

            return JsonResponse({
                'sonido_activado': preferencias.sonido_activado,
                'texto_grande': preferencias.texto_grande
            })
        except Niño.DoesNotExist:
            return JsonResponse({'error': 'Niño no encontrado'}, status=404)

    def post(self, request):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return JsonResponse({'error': 'No autenticado'}, status=403)

        try:
            niño = Niño.objects.get(pk=nino_id)
            preferencias, _ = PreferenciasUsuario.objects.get_or_create(niño=niño)

            # Leer los datos del cuerpo de la petición
            sonido = request.POST.get('sonido_activado')
            texto = request.POST.get('texto_grande')

            if sonido is not None:
                preferencias.sonido_activado = sonido == "true"
            if texto is not None:
                preferencias.texto_grande = texto == "true"

            preferencias.save()

            return JsonResponse({'estado': 'ok'})
        except Niño.DoesNotExist:
            return JsonResponse({'error': 'Niño no encontrado'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class EditarPerfilView(View):
    def post(self, request):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return JsonResponse({'estado': 'error', 'mensaje': 'No autenticado'}, status=403)

        try:
            niño = Niño.objects.get(pk=nino_id)

            # === DATOS DEL FORMULARIO ===
            nuevo_usuario = request.POST.get("usuario", "").strip()
            nuevo_email = request.POST.get("email", "").strip()
            nuevos_nombres = request.POST.get("nombres", "").strip()
            nuevos_apellidos = request.POST.get("apellidos", "").strip()

            # === VALIDAR NOMBRE DE USUARIO DUPLICADO ===
            if nuevo_usuario:
                if Niño.objects.filter(usuario=nuevo_usuario).exclude(pk=niño.pk).exists():
                    return JsonResponse({
                        'estado': 'error',
                        'mensaje': 'Ese nombre de usuario ya está en uso. Intenta con otro.'
                    }, status=400)
                niño.usuario = nuevo_usuario

            # === VALIDAR EMAIL (FORMATO Y DUPLICADO) ===
            if nuevo_email:
                try:
                    validate_email(nuevo_email)
                except ValidationError:
                    return JsonResponse({
                        'estado': 'error',
                        'mensaje': 'El formato del correo electrónico no es válido.'
                    }, status=400)

                if Niño.objects.filter(email=nuevo_email).exclude(pk=niño.pk).exists():
                    return JsonResponse({
                        'estado': 'error',
                        'mensaje': 'Ese correo electrónico ya está en uso. Intenta con otro.'
                    }, status=400)
                niño.email = nuevo_email

            # === VALIDAR NOMBRES Y APELLIDOS DUPLICADOS ===
            if nuevos_nombres and nuevos_apellidos:
                if Niño.objects.filter(
                    nombres__iexact=nuevos_nombres,
                    apellidos__iexact=nuevos_apellidos
                ).exclude(pk=niño.pk).exists():
                    return JsonResponse({
                        'estado': 'error',
                        'mensaje': 'Ya existe un usuario con esos mismos nombres y apellidos.'
                    }, status=400)

                niño.nombres = nuevos_nombres
                niño.apellidos = nuevos_apellidos

            # === VALIDAR FOTO DE PERFIL ===
            if 'foto' in request.FILES:
                niño.foto_perfil = request.FILES['foto']

            niño.save()
            return JsonResponse({'estado': 'ok', 'mensaje': 'Perfil actualizado correctamente.'})

        except Niño.DoesNotExist:
            return JsonResponse({'estado': 'error', 'mensaje': 'Niño no encontrado'}, status=404)


class GuardarProgresoMultiplicacionView(View):
    def post(self, request):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return JsonResponse({'error': 'No autenticado'}, status=403)

        nivel = int(request.POST.get('nivel', 0))
        puntaje = int(request.POST.get('puntaje', 0))
        tiempo = int(request.POST.get('tiempo', 0))

        niño = Niño.objects.get(pk=nino_id)
        progreso, _ = ProgresoDiscalculia.objects.get_or_create(niño=niño)

        if puntaje >= 70:
            if nivel + 1 > progreso.nivel_desbloqueado:
                progreso.nivel_desbloqueado = nivel + 1

        progreso.puntaje_total += puntaje
        progreso.tiempo_total += tiempo
        progreso.save()

        # Opcional: generar reporte
        puntaje_real = Decimal(puntaje)
        stop_event.set()
        if not deteccion_finalizada.wait(timeout=60):
            return JsonResponse({}, status=204)

        global resultado_final
        if resultado_final and "somnolencias" in resultado_final:
            Reporte.objects.create(
                niño=niño,
                titulo=f"Discalculia, nivel {nivel}",
                puntaje=puntaje_real,
                somnolencias=resultado_final.get("somnolencias", 0),
                distracciones=resultado_final.get("distracciones", 0),
                tiempos_somnolencia=resultado_final.get("tiempos_somnolencia", []),
                tiempos_distraccion=resultado_final.get("tiempos_distraccion", []),
                frames_somnolencia=resultado_final.get("frames_somnolencia", []),
                frames_distraccion=resultado_final.get("frames_distraccion", []),
                duracion_evaluacion=timedelta(seconds=tiempo)
            )

            session_key = f"deteccion_iniciada_{nino_id}"
            request.session[session_key] = False
            request.session.modified = True

            resultado_final.clear()
            deteccion_finalizada.clear()

        return JsonResponse({'estado': 'ok'})


class JuegoMultiplicacionView(TemplateView):
    template_name = 'juego_multiplicaciones.html'  # o el nombre real

    def dispatch(self, request, *args, **kwargs):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return redirect('accounts:login')

        # Iniciar detección como en juego_cartas
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
                gen_frames_background(nino_id, nuevo_id)

            t = Thread(target=run_detection)
            t.daemon = True
            t.start()

        return super().dispatch(request, *args, **kwargs)

class NivelesDiscalculiaView(View):
    def get(self, request):
        nino_id = request.session.get('nino_id')
        if not nino_id:
            return redirect('accounts:login')

        niño = Niño.objects.get(pk=nino_id)
        progreso, _ = ProgresoDiscalculia.objects.get_or_create(niño=niño)

        return render(request, 'niveles_discalculia.html', {
            'nivel_desbloqueado': progreso.nivel_desbloqueado
        })
