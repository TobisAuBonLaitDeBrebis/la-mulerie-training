from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import CheckConstraint, Q, F
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
        related_name='chevaux'
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
        related_name='sessions'
    )
    date = models.DateField(default=django.utils.timezone.now)
    type_seance = models.CharField(max_length=100)
    duree = models.PositiveIntegerField(
        help_text="Durée en minutes",
        validators=[MinValueValidator(1)]
    )
    notes = models.TextField(blank=True, null=True)
    cout = models.DecimalField(
        max_digits=7, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        help_text="Coût de l'entraînement en euros",
        validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(cout__isnull=True) | Q(cout__gte=0),
                name='cout_non_negatif'
            ),
            CheckConstraint(
                check=Q(duree__gte=1),
                name='duree_positive'
            ),
        ]

    def __str__(self):
        return f"{self.cheval.nom} - {self.date} - {self.type_seance}"