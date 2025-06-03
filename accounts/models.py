from django.db import models
from django.utils import timezone
import datetime

class CodigoRecuperacion(models.Model):
    email = models.EmailField()
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)

    def expirado(self):
        return timezone.now() > self.creado_en + datetime.timedelta(minutes=10)