
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
urlpatterns = [
    path('',include('accounts.urls',namespace='accounts')),
    path('',include('PADRE.urls',namespace='padre')),
    path('',include('PROFESOR.urls',namespace='profesor')),
    path('',include('NIÑO.urls',namespace='niño')),
    path('admin/', admin.site.urls)
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
