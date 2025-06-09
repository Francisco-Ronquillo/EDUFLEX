from django.shortcuts import redirect, get_object_or_404,render
from django.views import View
from django.views.generic import TemplateView,CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from PADRE.forms.addKid import CodigoNinoForm
from PROFESOR.models import  Profesor,Curso
from PROFESOR.forms.curso import CursoForm

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

class CursoTeacher(TemplateView):
    template_name = 'tus_cursos.html'

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

class crearCurso(CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'crear_curso.html'
    success_url = reverse_lazy('profesor:tuscursos')
    def get_context_data(self, **kwargs):
        context = super(crearCurso, self).get_context_data(**kwargs)
        return  context

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al crear la curso. Revisa los campos.")
        return self.render_to_response(self.get_context_data(form=form))