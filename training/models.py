from django.conf import settings
from django.db import models
import django.utils.timezone
from datetime import date

# Create your models here.
class Horse(models.Model):
    nom = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    birth_date = models.DateField(default=django.utils.timezone.now)
    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chevaux',
        null=True,  # Pour migration initiale, à rendre obligatoire ensuite
        blank=True
    )

    def __str__(self):
        return self.nom
    @property
    def age(self):
        """Calcule l'âge en années à partir de la date de naissance."""
        if self.birth_date:
            today = date.today()
            return (
                today.year - self.birth_date.year
                - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            )
        return None
    
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
    cout = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, help_text="Coût de l'entraînement en euros")


    def __str__(self):
        return f"{self.cheval.nom} - {self.date} - {self.type_seance}"