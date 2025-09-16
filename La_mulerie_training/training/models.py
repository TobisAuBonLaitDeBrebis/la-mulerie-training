from django.conf import settings
from django.db import models
import django.utils.timezone

# Create your models here.
class Horse(models.Model):
    nom = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chevaux',
        null=True,  # Pour migration initiale, à rendre obligatoire ensuite
        blank=True
    )

    def __str__(self):
        return self.nom

class TrainingSession(models.Model):
    cheval = models.ForeignKey('Horse', on_delete=models.CASCADE, related_name='trainings')
    cavalier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions',
        null=True,  # <-- Ajoute null=True
        blank=True  # <-- Ajoute blank=True pour l'admin
    )
    date = models.DateField(default=django.utils.timezone.now)
    type_seance = models.CharField(max_length=100)
    duree = models.PositiveIntegerField(help_text="Durée en minutes")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.cheval.nom} - {self.date} - {self.type_seance}"