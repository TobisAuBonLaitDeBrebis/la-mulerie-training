from django.db import migrations, models
from django.conf import settings
import django.utils.timezone
from datetime import date

def fix_null_values(apps, schema_editor):
    """
    Corrige les valeurs NULL dans les champs proprietaire et cavalier.
    """
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Horse = apps.get_model('training', 'Horse')
    TrainingSession = apps.get_model('training', 'TrainingSession')
    
    # Créer un utilisateur par défaut si nécessaire
    default_user, created = User.objects.get_or_create(
        username='default_user',
        defaults={
            'email': 'default@example.com',
            'password': 'unusable_password',
            'is_active': False
        }
    )
    
    # Corriger les chevaux sans propriétaire
    horses_without_owner = Horse.objects.filter(proprietaire__isnull=True)
    for horse in horses_without_owner:
        horse.proprietaire = default_user
        horse.save()
    
    # Corriger les séances sans cavalier
    sessions_without_rider = TrainingSession.objects.filter(cavalier__isnull=True)
    for session in sessions_without_rider:
        session.cavalier = default_user
        session.save()
    
    # Corriger les séances avec duree = 0
    sessions_with_zero_duration = TrainingSession.objects.filter(duree=0)
    for session in sessions_with_zero_duration:
        session.duree = 1
        session.save()


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0005_remove_horse_age_horse_birth_date'),
    ]

    operations = [
        # Corriger les données existantes
        migrations.RunPython(fix_null_values, migrations.RunPython.noop),
        
        # Ajouter les contraintes et rendre les champs non-nullables
        migrations.AlterField(
            model_name='horse',
            name='proprietaire',
            field=models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
                related_name='chevaux',
                null=False,
                blank=False
            ),
        ),
        migrations.AlterField(
            model_name='trainingsession',
            name='cavalier',
            field=models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
                related_name='sessions',
                null=False,
                blank=False
            ),
        ),
        # Ajouter une contrainte explicite pour duree > 0
        migrations.RunSQL(
            "UPDATE training_trainingsession SET duree = 1 WHERE duree = 0;"
        ),
    ]
