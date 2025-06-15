from django.shortcuts import redirect, get_object_or_404,render
from django.views import View
from django.views.generic import TemplateView,CreateView,ListView
from django.urls import reverse_lazy
from django.contrib import messages
from PADRE.forms.addKid import CodigoNinoForm
from PROFESOR.models import  Profesor,Curso
from NIÑO.models import  Reporte,Niño
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