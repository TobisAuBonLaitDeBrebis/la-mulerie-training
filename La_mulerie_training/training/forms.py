from django import forms
from .models import Horse, TrainingSession

class HorseForm(forms.ModelForm):
    class Meta:
        model = Horse
        fields = ['nom', 'race', 'age']

class TrainingSessionForm(forms.ModelForm):
                
    class Meta:
        model = TrainingSession
        fields = ['date', 'type_seance', 'duree', 'notes', 'cheval','cout']  # Ne pas inclure 'cheval' ni 'cavalier'