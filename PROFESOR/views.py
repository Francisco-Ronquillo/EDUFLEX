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

class Estadisticas_curso(TemplateView):
    template_name = "estadisticas_generales_curso.html"