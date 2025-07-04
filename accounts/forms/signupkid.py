
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
    foto_perfil = forms.ImageField(
        required=False,
        label='Foto de perfil',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )
    class Meta:
        model = Niño
        fields = ['nombres', 'apellidos', 'genero', 'usuario', 'contraseña', 'fecha_nac', 'email', 'especialidad','foto_perfil']

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

    def clean_foto_perfil(self):
        foto = self.cleaned_data.get('foto_perfil')
        if foto:
            if foto.size > 5 * 1024 * 1024:
                raise forms.ValidationError('La imagen es demasiado grande. Máximo 5MB.')

            allowed_types = ['image/jpeg','image/jpg', 'image/png']
            if foto.content_type not in allowed_types:
                raise forms.ValidationError('Formato no soportado. Use JPG, PNG o GIF.')
        return foto

    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres')
        if not nombres:
            raise forms.ValidationError("Este campo es obligatorio.")
        if not nombres.replace(' ', '').isalpha():
            raise forms.ValidationError("El nombre solo debe contener letras y espacios.")
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if not apellidos:
            raise forms.ValidationError("Este campo es obligatorio.")
        if not apellidos.replace(' ', '').isalpha():
            raise forms.ValidationError("El apellido solo debe contener letras y espacios.")
        return apellidos