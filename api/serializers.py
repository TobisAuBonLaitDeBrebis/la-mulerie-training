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
