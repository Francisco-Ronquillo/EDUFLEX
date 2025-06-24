from django.shortcuts import redirect, get_object_or_404,render
from django.views.generic import TemplateView,CreateView,ListView

from PROFESOR.models import  Profesor,Curso
from NIÑO.models import  Reporte,Niño
import  os,statistics
from datetime import timedelta
from django.conf import settings
class DashboardTeacher(TemplateView):
    template_name = 'dashboardTeacher.html'

    def dispatch(self, request, *args, **kwargs):
        if 'profesor_id' not in request.session:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profesor_id = self.request.session.get('profesor_id')
        profesor = get_object_or_404(Profesor, id=profesor_id)
        cursos=Curso.objects.filter(profesor=profesor_id)
        context['cursos'] = cursos
        context['profesor'] = profesor
        return context

class CursoTeacher(TemplateView):
    template_name = 'tus_cursos.html'

    def dispatch(self, request, *args, **kwargs):
        if 'profesor_id' not in request.session:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profesor_id = self.request.session.get('profesor_id')
        curso_profesor=Curso.objects.filter(profesor=profesor_id)
        context['cursos'] = curso_profesor
        return context

class PresentarCursoTeacher(TemplateView):
    template_name = 'curso_estudiante.html'
    def dispatch(self, request, *args, **kwargs):
        if 'profesor_id' not in request.session:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk=self.kwargs.get('curso_id')
        curso=Curso.objects.get(pk=pk)
        context['curso'] = curso
        context['niños'] =curso.niños.all()
        return context

class reportEstudiante(TemplateView):
    template_name = 'reporte_niño.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        niño_id = self.kwargs.get('niño_id')
        curso_id = self.kwargs.get('curso_id')
        curso=Curso.objects.get(pk=curso_id)
        nino = Niño.objects.get(pk=niño_id)
        context['nino'] = nino
        context['curso'] = curso
        context['reportes'] = Reporte.objects.filter(niño=nino,fecha__range=(curso.fecha_inicio, curso.fecha_final)).order_by('-fecha')
        return context


class verReportStudent(TemplateView):
        template_name = 'verReportStudent.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            pk = self.kwargs.get('pk')
            reporte = Reporte.objects.get(pk=pk)
            nino_id = reporte.niño.id

            base_dir = os.path.join('capturas', str(nino_id), str(pk))
            media_dir = os.path.join(settings.MEDIA_ROOT, base_dir)

            frames_somnolencia = []
            frames_distraccion = []

            if os.path.exists(media_dir):
                for nombre in os.listdir(media_dir):
                    if nombre.startswith('somnolencia'):
                        frames_somnolencia.append(f"{base_dir}/{nombre}")
                    elif nombre.startswith('distraccion'):
                        frames_distraccion.append(f"{base_dir}/{nombre}")

            pares_somnolencia = zip(frames_somnolencia, reporte.tiempos_somnolencia or [])
            pares_distraccion = zip(frames_distraccion, reporte.tiempos_distraccion or [])
            promedio_somnolencia = round(statistics.mean(reporte.tiempos_somnolencia),
                                         2) if reporte.tiempos_somnolencia else 0
            promedio_distraccion = round(statistics.mean(reporte.tiempos_distraccion),
                                         2) if reporte.tiempos_distraccion else 0
            total_somnolencia = sum(reporte.tiempos_somnolencia or [])
            total_distraccion = sum(reporte.tiempos_distraccion or [])
            tiempo_concentracion = (
                    reporte.duracion_evaluacion
                    - timedelta(seconds=total_somnolencia)
                    - timedelta(seconds=total_distraccion)
            )
            context['reporte'] = reporte
            context['pares_somnolencia'] = list(pares_somnolencia)
            context['pares_distraccion'] = list(pares_distraccion)
            context['promedio_somnolencia'] = promedio_somnolencia
            context['promedio_distraccion'] = promedio_distraccion
            context['total_somnolencia'] = total_somnolencia
            context['total_distraccion'] = total_distraccion
            context['tiempo_concentracion'] = tiempo_concentracion
            context['grafico_data'] = {
                'distracciones': reporte.distracciones or 0,
                'somnolencias': reporte.somnolencias or 0,
                'tiempos_somnolencia': reporte.tiempos_somnolencia or [],
                'tiempos_distraccion': reporte.tiempos_distraccion or [],
            }

            return context


class Estadisticas_niño(TemplateView):
    template_name = "estadisticas_generales_niño.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        niño_id = self.kwargs.get('niño_id')
        curso_id = self.kwargs.get('curso_id')
        nino = get_object_or_404(Niño, pk=niño_id)
        reportes = Reporte.objects.filter(niño=nino)
        curso=get_object_or_404(Curso, pk=curso_id)
        nivel = self.request.GET.get('nivel')
        fecha_i = self.request.GET.get('fecha_i')
        fecha_f = self.request.GET.get('fecha_f')

        if nivel:
            reportes = reportes.filter(titulo__icontains=f'nivel {nivel}')
        if fecha_i and fecha_f:
            reportes = reportes.filter(fecha__range=[fecha_i, fecha_f])
        elif fecha_i:
            reportes = reportes.filter(fecha__gte=fecha_i)
        elif fecha_f:
            reportes = reportes.filter(fecha__lte=fecha_f)

        total_distracciones = sum(r.distracciones or 0 for r in reportes)
        total_somnolencias = sum(r.somnolencias or 0 for r in reportes)
        cantidad_reportes = reportes.count()
        puntajes = [
            {
                'fecha': r.fecha.strftime('%Y-%m-%d'),
                'puntaje': round(float(r.puntaje) / 10, 2) if r.puntaje is not None else 0
            }
            for r in reportes
        ]
        distracciones = [
            {
                'fecha': r.fecha.strftime('%Y-%m-%d'),
                'distracciones': int(r.distracciones) if r.distracciones is not None else 0
            }
            for r in reportes
        ]
        somnolencias = [
            {
                'fecha': r.fecha.strftime('%Y-%m-%d'),
                'somnolencias': int(r.somnolencias) if r.somnolencias is not None else 0
            }
            for r in reportes
        ]
        tiempos_distraccion_sumados = [
            {
                'fecha': r.fecha.strftime('%Y-%m-%d'),
                'tiempo_total_distraccion': float(sum(r.tiempos_distraccion or []))
            }
            for r in reportes
        ]
        tiempos_somnolencia_sumados = [
            {
                'fecha': r.fecha.strftime('%Y-%m-%d'),
                'tiempo_total_somnolencia': float(sum(r.tiempos_somnolencia or []))
            }
            for r in reportes
        ]
        tiempos = [r['tiempo_total_distraccion'] for r in tiempos_distraccion_sumados]
        promedio_tiempo_distraccion = round(statistics.mean(tiempos), 2) if tiempos else 0
        tiempos_som = [r['tiempo_total_somnolencia'] for r in tiempos_somnolencia_sumados]
        promedio_tiempo_somnolencia = round(statistics.mean(tiempos_som), 2) if tiempos_som else 0
        solo_puntajes = [p['puntaje'] for p in puntajes]
        promedio_puntaje = round(statistics.mean(solo_puntajes), 2) if solo_puntajes else 0
        promedio_distracciones = round(total_distracciones / cantidad_reportes, 2) if cantidad_reportes > 0 else 0
        promedio_somnolencias = round(total_somnolencias / cantidad_reportes, 2) if cantidad_reportes > 0 else 0
        context['nino'] = nino
        context['reportes'] = reportes
        context['total_distracciones'] = total_distracciones
        context['total_somnolencias'] = total_somnolencias
        context['nivel'] = nivel or ''
        context['fecha_i'] = fecha_i or ''
        context['fecha_f'] = fecha_f or ''
        context['promedio_distracciones'] = promedio_distracciones
        context['promedio_somnolencias'] = promedio_somnolencias
        context['promedio_puntaje'] = promedio_puntaje
        context['distracciones'] = distracciones
        context['somnolencias'] = somnolencias
        context['puntajes'] = puntajes
        context['tiempos_distraccion_sumados'] = tiempos_distraccion_sumados
        context['tiempos_somnolencia_sumados'] = tiempos_somnolencia_sumados
        context['promedio_tiempo_distraccion'] = promedio_tiempo_distraccion
        context['promedio_tiempo_somnolencia'] = promedio_tiempo_somnolencia
        context['nino']= nino
        context['curso'] = curso
        context['graficodis_som'] = {
            'distracciones': total_distracciones,
            'somnolencias': total_somnolencias,
        }
        return context

class Estadisticas_curso(TemplateView):
    template_name = "estadisticas_generales_curso.html"