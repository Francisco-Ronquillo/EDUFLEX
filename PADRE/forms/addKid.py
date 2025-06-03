from django import forms

class CodigoNinoForm(forms.Form):
    codigo = forms.CharField(label="Código del niño", max_length=100)
