from rest_framework import serializers
from django.contrib.auth import get_user_model

from training.models import Horse, TrainingSession

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour les utilisateurs - expose uniquement les champs nécessaires au mobile.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id', 'username', 'is_active']


class HorseSerializer(serializers.ModelSerializer):
    """
    Serializer en lecture seule pour les equides - destine au mobile.
    Expose uniquement les champs necessaires aux ecrans mobiles.
    Le proprietaire n'est pas expose : la regle d'acces du lot 01 limite
    la lecture au proprietaire lui-meme.
    """
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Horse
        fields = ['id', 'nom', 'race', 'birth_date', 'age']
        read_only_fields = fields

class TrainingSessionSerializer(serializers.ModelSerializer):
    """
    Serializer de lecture et creation des seances pour le mobile.

    A la creation :
    - `cavalier` est toujours deflecte par le serveur (utilisateur authentifie),
      jamais lu depuis le payload ;
    - `cheval` est restreint aux equides de l'utilisateur : un equide
      inaccessible est traite comme inexistant (pas de fuite d'existence).

    Unites exposees : `duree` en minutes, `cout` en euros.
    """
    client_uuid = serializers.UUIDField(
        format='hex_verbose',
        help_text="UUID genere par le client avant l'envoi, conserve lors des retries.",
    )

    class Meta:
        model = TrainingSession
        fields = [
            'id', 'client_uuid', 'cheval',
            'date', 'type_seance', 'duree', 'cout', 'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if user is not None and user.is_authenticated:
            self.fields['cheval'].queryset = Horse.objects.filter(proprietaire=user)


def payload_matches(session, validated):
    """
    Indique si une seance existante correspond au payload rejoue
    (meme UUID client, meme contenu).
    """
    return (
        session.cheval_id == validated['cheval'].pk
        and session.date == validated['date']
        and session.type_seance == validated['type_seance']
        and session.duree == validated['duree']
        and session.cout == validated.get('cout')
        and (session.notes or None) == (validated.get('notes') or None)
    )


class DashboardFilterSerializer(serializers.Serializer):
    """Filtres de periode acceptes par GET /api/v1/dashboard/ (dates ISO)."""
    start_date = serializers.DateField(
        required=False, default=None,
        help_text="Borne de debut incluse de la periode (YYYY-MM-DD).",
    )
    end_date = serializers.DateField(
        required=False, default=None,
        help_text="Borne de fin incluse de la periode (YYYY-MM-DD).",
    )


class DashboardPeriodSerializer(serializers.Serializer):
    """Periode effectivement appliquee (null = toutes les donnees)."""
    start_date = serializers.DateField(allow_null=True)
    end_date = serializers.DateField(allow_null=True)


class DashboardTypeStatSerializer(serializers.Serializer):
    """Comptage de seances par type."""
    type_seance = serializers.CharField()
    count = serializers.IntegerField()
    total_duration = serializers.IntegerField(help_text="Duree cumulee en minutes.")


class DashboardHorseStatSerializer(serializers.Serializer):
    """Comptage de seances par equide (tri par duree cumulee decroissante)."""
    cheval = serializers.CharField(source='cheval__nom')
    count = serializers.IntegerField()
    total_duration = serializers.IntegerField(help_text="Duree cumulee en minutes.")


class DashboardRecentSessionSerializer(serializers.Serializer):
    """Resume d'une des 5 dernieres seances."""
    id = serializers.IntegerField()
    date = serializers.DateField()
    type_seance = serializers.CharField()
    cheval = serializers.CharField(source='cheval.nom')
    duree = serializers.IntegerField(help_text="Duree en minutes.")


class DashboardCalendarEntrySerializer(serializers.Serializer):
    """Entree du calendrier : une seance datee."""
    id = serializers.IntegerField()
    date = serializers.DateField(format='%Y-%m-%d')
    activity = serializers.CharField()


class DashboardSerializer(serializers.Serializer):
    """Indicateurs du tableau de bord mobile (memes calculs que le web)."""
    total_sessions = serializers.IntegerField()
    total_horses = serializers.IntegerField()
    total_duration = serializers.IntegerField(help_text="Duree cumulee en minutes.")
    total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False,
        help_text="Cout cumule en euros.",
    )
    avg_duration = serializers.FloatField(help_text="Duree moyenne en minutes (1 decimale).")
    avg_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False,
        help_text="Cout moyen en euros (2 decimales).",
    )
    sessions_per_horse = serializers.FloatField(
        help_text="Nombre moyen de seances par equide (1 decimale).",
    )
    sessions_by_type = DashboardTypeStatSerializer(many=True)
    sessions_by_horse = DashboardHorseStatSerializer(many=True)
    month_names = serializers.ListField(child=serializers.CharField())
    month_counts = serializers.ListField(child=serializers.IntegerField())
    recent_sessions = DashboardRecentSessionSerializer(many=True)
    sessions_dates = DashboardCalendarEntrySerializer(many=True)
    period = DashboardPeriodSerializer()


class ApiErrorSerializer(serializers.Serializer):
    """Enveloppe d'erreur standard produite par api/exceptions.py."""
    error = serializers.BooleanField()
    code = serializers.IntegerField()
    message = serializers.CharField()


class IdempotencyConflictSerializer(serializers.Serializer):
    """Reponse 409 : l'UUID client est deja associe a une seance differente."""
    detail = serializers.CharField()
    session_id = serializers.IntegerField()
