
from django import forms
from NIÑO.models import Niño
import datetime
import re
from EDUFLEX.utils import *


class NiñoForm(forms.ModelForm):
    confirmar_contraseña = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña', 'id': 'confirmar_contraseña'})
    )

    class Meta:
        model = Niño
        fields = ['nombres', 'apellidos', 'genero', 'usuario', 'contraseña', 'fecha_nac', 'email', 'especialidad']

        widgets = {
            'nombres': forms.TextInput(attrs={'placeholder': 'Ingresar nombres', 'id': 'nombres'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Ingresar apellidos', 'id': 'apellidos'}),
            'genero': forms.Select(attrs={'id': 'genero'}),
            'usuario': forms.TextInput(attrs={'placeholder': 'Ingresar usuario', 'id': 'usuario'}),
            'contraseña': forms.PasswordInput(attrs={'placeholder': 'Ingresar contraseña', 'id': 'contraseña'}),
            'fecha_nac': forms.DateInput(attrs={'type': 'date', 'id': 'fecha_nac'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ingresar correo', 'id': 'email'}),
            'especialidad': forms.Select(attrs={'id': 'especialidad'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get('contraseña')
        confirmar = cleaned_data.get('confirmar_contraseña')

        if contraseña and confirmar and contraseña != confirmar:
            self.add_error('confirmar_contraseña', 'Las contraseñas no coinciden.')
    def clean_fecha_nac(self):
        fecha = self.cleaned_data.get('fecha_nac')
        if fecha:
            if fecha > datetime.date.today():
                raise forms.ValidationError('La fecha de nacimiento no puede ser en el futuro.')

            edad = calcular_edad(fecha)
            if edad < 4:
                raise forms.ValidationError('La edad mínima es de 4 años.')

        return fecha

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if Niño.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")

        return email
    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if Niño.objects.filter(usuario=usuario).exists():
            raise forms.ValidationError("Este usario ya existe.")
        return usuario

    def clean_contraseña(self):
        contraseña = self.cleaned_data.get('contraseña')

        if len(contraseña) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'\d', contraseña):
            raise forms.ValidationError("La contraseña debe contener al menos un número.")

        return contraseña