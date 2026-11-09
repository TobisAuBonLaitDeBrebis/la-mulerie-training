# Generated manually for Lot 01 - Integrite et securite metier
# Fix data integrity issues, add constraints, and make fields required

from django.conf import settings
from django.db import migrations, models
import django.core.validators


def fix_invalid_duree(apps, schema_editor):
    """Fix sessions with duree <= 0 by setting to 1"""
    TrainingSession = apps.get_model('training', 'TrainingSession')
    
    # Find sessions with duree <= 0
    invalid_sessions = TrainingSession.objects.filter(duree__lte=0)
    count = invalid_sessions.count()
    if count > 0:
        print(f"Fixing {count} session(s) with invalid duree (<= 0)")
        invalid_sessions.update(duree=1)


def fix_negative_cout(apps, schema_editor):
    """Fix sessions with cout < 0 by setting to NULL"""
    TrainingSession = apps.get_model('training', 'TrainingSession')
    
    # Find sessions with cout < 0
    invalid_sessions = TrainingSession.objects.filter(cout__lt=0)
    count = invalid_sessions.count()
    if count > 0:
        print(f"Fixing {count} session(s) with negative cout")
        invalid_sessions.update(cout=None)


def assign_orphan_horse_to_admin(apps, schema_editor):
    """
    Assign the horse with NULL proprietaire to the first user (admin).
    """
    Horse = apps.get_model('training', 'Horse')
    User = apps.get_model('auth', 'User')
    
    # Get the first user (should be admin)
    first_user = User.objects.order_by('pk').first()
    
    if first_user:
        # Find horses with NULL proprietaire
        orphan_horses = Horse.objects.filter(proprietaire__isnull=True)
        count = orphan_horses.count()
        if count > 0:
            print(f"Assigning {count} orphan horse(s) to user {first_user.username} (id={first_user.pk})")
            orphan_horses.update(proprietaire=first_user)


def assign_orphan_sessions_to_riders(apps, schema_editor):
    """
    Assign sessions with NULL cavalier to the horse's proprietaire.
    If horse has no proprietaire, assign to first user.
    """
    TrainingSession = apps.get_model('training', 'TrainingSession')
    User = apps.get_model('auth', 'User')
    
    first_user = User.objects.order_by('pk').first()
    
    if first_user:
        # Find sessions with NULL cavalier
        orphan_sessions = TrainingSession.objects.filter(cavalier__isnull=True)
        count = orphan_sessions.count()
        if count > 0:
            print(f"Found {count} session(s) with NULL cavalier, assigning...")
            for session in orphan_sessions:
                # Try to assign to horse's proprietaire
                if session.cheval_id and session.cheval.proprietaire_id:
                    session.cavalier_id = session.cheval.proprietaire_id
                else:
                    # Fallback to first user
                    session.cavalier_id = first_user.pk
                session.save(update_fields=['cavalier'])


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0005_remove_horse_age_horse_birth_date'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Step 1: Fix invalid duree values
        migrations.RunPython(
            fix_invalid_duree,
            reverse_code=migrations.RunPython.noop
        ),
        # Step 2: Fix negative cout values
        migrations.RunPython(
            fix_negative_cout,
            reverse_code=migrations.RunPython.noop
        ),
        # Step 3: Assign orphan horses to admin
        migrations.RunPython(
            assign_orphan_horse_to_admin,
            reverse_code=migrations.RunPython.noop
        ),
        # Step 4: Assign orphan sessions to riders
        migrations.RunPython(
            assign_orphan_sessions_to_riders,
            reverse_code=migrations.RunPython.noop
        ),
        # Step 5: Add validators to fields
        migrations.AlterField(
            model_name='trainingsession',
            name='cout',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text="Coût de l'entraînement en euros",
                max_digits=7, 
                null=True,
                validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        migrations.AlterField(
            model_name='trainingsession',
            name='duree',
            field=models.PositiveIntegerField(
                help_text='Durée en minutes',
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        # Step 6: Add database constraints
        migrations.AddConstraint(
            model_name='trainingsession',
            constraint=models.CheckConstraint(
                condition=models.Q(('cout__isnull', True), ('cout__gte', 0), _connector='OR'),
                name='cout_non_negatif'
            ),
        ),
        migrations.AddConstraint(
            model_name='trainingsession',
            constraint=models.CheckConstraint(
                condition=models.Q(('duree__gte', 1)),
                name='duree_positive'
            ),
        ),
        # Step 7: Make proprietaire non-nullable
        migrations.AlterField(
            model_name='horse',
            name='proprietaire',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='chevaux',
                to=settings.AUTH_USER_MODEL,
                null=False,
                blank=False,
            ),
        ),
        # Step 8: Make cavalier non-nullable
        migrations.AlterField(
            model_name='trainingsession',
            name='cavalier',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='sessions',
                to=settings.AUTH_USER_MODEL,
                null=False,
                blank=False,
            ),
        ),
    ]
