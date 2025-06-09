from django.urls import path
from PROFESOR.views import *
app_name = 'profesor'
urlpatterns = [
path('dashboardTeacher/',DashboardTeacher.as_view(),name='dashboardTeacher'),
path('tuscursos/',CursoTeacher.as_view(),name='tuscursos'),
path('crearCurso/',crearCurso.as_view(),name='crearCurso'),
]