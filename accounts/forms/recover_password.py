from django import forms
class SolicitarCodigoForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico", widget=forms.EmailInput(attrs={
        'placeholder': 'Ingresa correo',
        'class': 'input',
    }))


class VerificarCodigoForm(forms.Form):
    codigo = forms.CharField(max_length=6, label="Código de verificación", widget=forms.TextInput(attrs={
        'placeholder': 'Ingresar código',
        'class': 'input',
    }))


class NuevaContraseñaForm(forms.Form):
    nueva = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingresar contraseña',
        'class': 'input',
    }))
    confirmar = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirmar contraseña',
        'class': 'input',
    }))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('nueva') != cleaned.get('confirmar'):
            raise forms.ValidationError("Las contraseñas no coinciden.")
