from django import forms


class LoginPadreForm(forms.Form):
    usuario = forms.CharField(
        label='Usuario',
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Usuario del padre'})
    )
    contraseña = forms.CharField(
        label='Contraseña',
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
