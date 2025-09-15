from django.db import models

# Create your models here.
from django.db import models

class Horse(models.Model):
    nom = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    age = models.PositiveIntegerField()

    def __str__(self):
        return self.nom

class TrainingSession(models.Model):
    cheval = models.ForeignKey(Horse, on_delete=models.CASCADE, related_name='trainings')
    date = models.DateField()
    type_seance = models.CharField(max_length=100)
    duree = models.PositiveIntegerField(help_text="Durée en minutes")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.cheval.nom} - {self.date} - {self.type_seance}"