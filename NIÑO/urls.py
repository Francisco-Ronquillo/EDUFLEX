from django.urls import path
from NIÑO.views import *
from . import views
app_name = 'niño'
urlpatterns = [
path('dashboarKid/',DashboardKid.as_view(),name='dashboardKid'),
path('video_feed/', views.video_feed, name='video_feed')

]