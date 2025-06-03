
from django import forms
from NIÑO.models import Niño

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
