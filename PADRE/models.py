from django.db import models
SEX_CHOICES=[('M', 'Masculino'), ('F', 'Femenino')]

class Padre(models.Model):
    nombres=models.CharField(max_length=100)
    apellidos=models.CharField(max_length=100)
    genero=models.CharField(max_length=1,choices=SEX_CHOICES)
    usuario=models.CharField(max_length=30)
    contraseña = models.CharField(max_length=64)
    fecha_nac=models.DateField()
    email=models.EmailField()

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"