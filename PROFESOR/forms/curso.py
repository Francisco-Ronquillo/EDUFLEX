from django import forms
from PROFESOR.models import Curso

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre_curso', 'seccion', 'descripcion','periodo']
        widgets = {
            'nombre_curso': forms.TextInput(attrs={'placeholder': 'Ej.2B','id':'nombre_curso'}),
            'seccion': forms.Select(attrs={'placeholder': 'Ej. Matutina','id':'seccion'}),
            'descripcion': forms.Textarea(attrs={'placeholder': 'Descripción breve','id':'descripcion', 'rows': 3}),
            'periodo': forms.TextInput(attrs={'placeholder': 'ej. 2025-2026','id':'periodo'}),
        }