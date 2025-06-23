from django.shortcuts import redirect, get_object_or_404,render
from django.views import View
from django.views.generic import TemplateView,FormView,ListView
from django.urls import reverse_lazy
from django.contrib import messages
from PADRE.forms.addKid import CodigoNinoForm
from NIÑO.models import  Niño,Reporte
from PADRE.models import  Padre
from datetime import timedelta
import os,statistics
from django.db.models import Q
from django.conf import settings
class DashboardDad(TemplateView):
    template_name = 'dashboardDad.html'

    def dispatch(self, request, *args, **kwargs):
        if 'padre_id' not in request.session:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        padre_id = self.request.session.get('padre_id')
        padre = get_object_or_404(Padre, id=padre_id)

        # Obtener los 2 reportes más recientes de los niños del padre
        reportes_recientes = Reporte.objects.filter(niño__padre=padre).order_by('-fecha')[:2]

        context['padre'] = padre
        context['reportes_recientes'] = reportes_recientes
        return context


class reportKid(FormView, ListView):
    template_name = 'reportes_kid.html'
    model = Niño
    context_object_name = "niños"
    success_url = reverse_lazy('padre:reportKid')
    form_class = CodigoNinoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        padre_id = self.request.session.get('padre_id')
        if padre_id:
            niños = Niño.objects.filter(padre_id=padre_id)
            lista_con_reportes = []

            for niño in niños:
                reportes = niño.reportes.order_by('-fecha')

                for reporte in reportes:
                    total_segundos = int(reporte.duracion_evaluacion.total_seconds())
                    horas = total_segundos // 3600
                    minutos = (total_segundos % 3600) // 60
                    segundos = total_segundos % 60
                    reporte.duracion_evaluacion = f"{horas}:{minutos:02}:{segundos:02}"

                lista_con_reportes.append({
                    'niño': niño,
                    'reportes': reportes
                })

            context[self.context_object_name] = lista_con_reportes
        else:
            context[self.context_object_name] = []
        return context
    def form_valid(self, form):
        codigo = form.cleaned_data.get('codigo')
        try:
            nino = Niño.objects.get(codigo=codigo)
            if nino.padre is not None:
                messages.warning(self.request, "Este niño ya está asociado a otro padre.")
                return redirect(self.success_url)

            padre_id = self.request.session.get('padre_id')
            if padre_id:
                padre = Padre.objects.get(id=padre_id)
                nino.padre = padre
                nino.save()
                messages.success(self.request, "Niño agregado correctamente.")
            else:
                messages.error(self.request, "No se encontró el padre en sesión.")
        except Niño.DoesNotExist:
            messages.error(self.request, "Código inválido. Intenta nuevamente.")

        return redirect(self.success_url)

class DesvincularNinoView(View):
    def post(self, request, *args, **kwargs):
        nino_id = kwargs.get('pk')  # Asegúrate que lo pasas en la URL como <int:pk>
        padre_id = request.session.get('padre_id')

        if not padre_id:
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('padre:reportKid')

        nino = get_object_or_404(Niño, id=nino_id)

        if nino.padre_id != padre_id:
            messages.warning(request, "No puedes desvincular a este niño.")
        else:
            nino.padre = None
            nino.save()
            messages.success(request, "Niño desvinculado correctamente.")

        return redirect('padre:reportKid')

class reportTotal(ListView):
    template_name = 'report_total.html'
    model=Reporte
    context_object_name = 'reportes'
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        niño=Niño.objects.get(pk=pk)
        queryset=Reporte.objects.filter(niño=niño).order_by('-fecha')
        nivel =self.request.GET.get('nivel')
        fecha_i=self.request.GET.get('fecha_i')
        fecha_f=self.request.GET.get('fecha_f')

        if nivel:
            queryset = queryset.filter(titulo__icontains=f'nivel {nivel}')
        if fecha_i and fecha_f:
            queryset = queryset.filter(fecha__range=[fecha_i, fecha_f])
        elif fecha_i:
            queryset = queryset.filter(fecha__gte=fecha_i)
        elif fecha_f:
            queryset = queryset.filter(fecha__lte=fecha_f)

        for reporte in queryset:
            total_segundos = int(reporte.duracion_evaluacion.total_seconds())
            horas = total_segundos // 3600
            minutos = (total_segundos % 3600) // 60
            segundos = total_segundos % 60
            reporte.duracion_evaluacion = f"{horas}:{minutos:02}:{segundos:02}"

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        nino = Niño.objects.get(pk=pk)
        context['nino'] = nino
        context['nivel'] = self.request.GET.get('nivel', '')
        context['fecha_i'] = self.request.GET.get('fecha_i', '')
        context['fecha_f'] = self.request.GET.get('fecha_f', '')
        return context


class verReporte(TemplateView):
    template_name = 'verReporte.html'

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
        promedio_somnolencia = round(statistics.mean(reporte.tiempos_somnolencia),2) if reporte.tiempos_somnolencia else 0
        promedio_distraccion = round(statistics.mean(reporte.tiempos_distraccion),2) if reporte.tiempos_distraccion else 0
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



class estadisticasGenerales(TemplateView):
    template_name = "estadisticas_generales.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        nino = get_object_or_404(Niño, pk=pk)
        reportes = Reporte.objects.filter(niño=nino)

        # Filtros
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
        somnolencias_array = [r.somnolencias or 0 for r in reportes]
        cantidad_reportes = reportes.count()
        distracciones_array = [r.distracciones or 0 for r in reportes]
        puntajes = [
            {
                'fecha': r.fecha.strftime('%Y-%m-%d'),
                'puntaje': round(float(r.puntaje) / 10, 2) if r.puntaje is not None else 0
            }
            for r in reportes
        ]
        distracciones=[
            {
                'fecha': r.fecha.strftime('%Y-%m-%d'),
                'puntaje': round(float(r.puntaje) / 10, 2) if r.puntaje is not None else 0
            }
            for r in reportes
        ]
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

        context['puntajes'] = puntajes

        context['distracciones_array'] = distracciones_array
        context['grafico_data'] = {
            'distracciones': total_distracciones,
            'somnolencias': total_somnolencias,
        }

        return context


