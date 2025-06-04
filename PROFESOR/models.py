from django.db import models
Jornadas_CHOICES=[('M','Matutina'),('V','Vespertina')]
SEX_CHOICES=[('M', 'Masculino'), ('F', 'Femenino')]
ESPECIALIDAD=[('P','psicopedagogo'),('T','Trastornos de la escritura'),('N','neuroeducación aplicada al TDAH')]
class Profesor(models.Model):
    nombres=models.CharField(max_length=100)
    apellidos=models.CharField(max_length=100)
    genero=models.CharField(max_length=1,choices=SEX_CHOICES)
    usuario=models.CharField(max_length=30)
    contraseña = models.CharField(max_length=64)
    fecha_nac=models.DateField()
    email=models.EmailField()
    especializacion = models.CharField(max_length=1,choices=ESPECIALIDAD)
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

class Curso(models.Model):
    nombre_curso=models.CharField(max_length=100)
    seccion=models.CharField(max_length=1,choices=Jornadas_CHOICES)
    descripcion=models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre_curso} - {self.get_seccion_display()}"