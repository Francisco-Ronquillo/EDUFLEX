import hashlib,datetime
import random , string
from NIÑO.models import *
def generar_codigo_unico(longitud=8):
    while True:
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=longitud))
        if not Niño.objects.filter(codigo=codigo).exists():
            return codigo
def cifrar_contraseña(contraseña):
    return hashlib.sha256(contraseña.encode()).hexdigest()

def calcular_edad(fecha_nac):
    hoy = datetime.date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))