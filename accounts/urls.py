
from django.urls import path
from accounts.views import *
app_name = 'accounts'
urlpatterns = [
path('',HomePageView.as_view(),name='home'),
path('login/',LoginView.as_view(),name='login'),
path('logout/',LogoutView.as_view(),name='logout'),
path('rol/',RolView.as_view(),name='rol'),
path('signupkid/',SignupKidView.as_view(),name='signupkid'),
path('signupdad/',SignupDadView.as_view(),name='signupdad'),
path('recuperar/<str:rol>/', EnviarCodigoView.as_view(), name='recover_password'),
path('verificar/', VerificarCodigoView.as_view(), name='verificar_codigo'),
path('cambiar/', CambiarContraseñaConCodigoView.as_view(), name='cambiar_contraseña')
]