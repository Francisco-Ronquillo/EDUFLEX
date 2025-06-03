from django.shortcuts import redirect, get_object_or_404,render
from django.views import View
from django.views.generic import TemplateView,FormView,ListView
from django.urls import reverse_lazy
from django.contrib import messages
from PADRE.forms.addKid import CodigoNinoForm
from PROFESOR.models import  Profesor


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
        context['profesor'] = profesor
        return context