from django import forms
from PROFESOR.models import Curso

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre_curso', 'seccion', 'descripcion']
        widgets = {
            'nombre_curso': forms.TextInput(attrs={'placeholder': 'Ej.2B'}),
            'seccion': forms.Select(attrs={'placeholder': 'Ej. Matutina'}),
            'descripcion': forms.Textarea(attrs={'placeholder': 'Descripción breve', 'rows': 3}),
        }