from django.urls import path
from NIÑO.views import *
app_name = 'niño'
urlpatterns = [
path('dashboarKid/',DashboardKid.as_view(),name='dashboardKid')
]