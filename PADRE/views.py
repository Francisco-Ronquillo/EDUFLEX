from django.shortcuts import redirect, get_object_or_404,render
from django.views import View
from django.views.generic import TemplateView,FormView,ListView
from django.urls import reverse_lazy
from django.contrib import messages
from PADRE.forms.addKid import CodigoNinoForm
from NIÑO.models import  Niño,Reporte
from PADRE.models import  Padre
import os
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
                reportes = niño.reportes.order_by('-fecha')[:5]

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
class reportTotal(TemplateView):
    template_name = 'report_total.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        nino = Niño.objects.get(pk=pk)
        reportes=Reporte.objects.filter(niño=nino).order_by('-fecha')
        for reporte in reportes:
            total_segundos = int(reporte.duracion_evaluacion.total_seconds())
            horas = total_segundos // 3600
            minutos = (total_segundos % 3600) // 60
            segundos = total_segundos % 60
            reporte.duracion_evaluacion = f"{horas}:{minutos:02}:{segundos:02}"
        context['nino'] = nino
        context['reportes'] =reportes
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

        # Emparejar imágenes con sus tiempos (mismo orden)
        pares_somnolencia = zip(frames_somnolencia, reporte.tiempos_somnolencia or [])
        pares_distraccion = zip(frames_distraccion, reporte.tiempos_distraccion or [])

        context['reporte'] = reporte
        context['pares_somnolencia'] = pares_somnolencia
        context['pares_distraccion'] = pares_distraccion
        return context