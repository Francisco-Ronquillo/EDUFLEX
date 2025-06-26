import datetime
from EDUFLEX.utils import calcular_edad
from django import forms

import PADRE
from PADRE.models import Padre
class PadreForm(forms.ModelForm):
    confirmar_contraseña = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña', 'id': 'confirmar_contraseña'})
    )

    class Meta:
        model = Padre
        fields = ['nombres', 'apellidos', 'genero', 'usuario', 'contraseña', 'fecha_nac', 'email',]

        widgets = {
            'nombres': forms.TextInput(attrs={'placeholder': 'Ingresar nombres', 'id': 'nombres'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Ingresar apellidos', 'id': 'apellidos'}),
            'genero': forms.Select(attrs={'id': 'genero'}),
            'usuario': forms.TextInput(attrs={'placeholder': 'Ingresar usuario', 'id': 'usuario'}),
            'contraseña': forms.PasswordInput(attrs={'placeholder': 'Ingresar contraseña', 'id': 'contraseña'}),
            'fecha_nac': forms.DateInput(attrs={'type': 'date', 'id': 'fecha_nac'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ingresar correo', 'id': 'email'}),
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
            if edad < 18:
                raise forms.ValidationError('La edad mínima es de 18 años.')

        return fecha

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if Padre.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")

        return email
    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if Padre.objects.filter(usuario=usuario).exists():
            raise forms.ValidationError("Este usario ya existe.")
        return usuario