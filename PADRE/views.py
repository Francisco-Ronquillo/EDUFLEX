from django.shortcuts import redirect, get_object_or_404,render
from django.views import View
from django.views.generic import TemplateView,FormView,ListView
from django.urls import reverse_lazy
from django.contrib import messages
from PADRE.forms.addKid import CodigoNinoForm
from NIÑO.models import  Niño,Reporte
from PADRE.models import  Padre

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


class reportKid(FormView,ListView):
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
                lista_con_reportes.append({
                    'niño': niño,
                    'reportes': niño.reportes.all()
                })

            context['niños'] = lista_con_reportes
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