from django.urls import path
from PROFESOR.views import *
app_name = 'profesor'
urlpatterns = [
path('dashboardTeacher/',DashboardTeacher.as_view(),name='dashboardTeacher'),
path('tuscursos/',CursoTeacher.as_view(),name='tuscursos'),
path('curso/<int:curso_id>/',PresentarCursoTeacher.as_view(),name='curso'),
path('estudiante/<int:curso_id>/<int:niño_id>/reportes/', reportEstudiante.as_view(), name='estudiante'),
path('verReportStudent/<int:pk>/', verReportStudent.as_view(), name='verReportStudent'),
]