from rest_framework import serializers
from django.contrib.auth import get_user_model

from training.models import Horse

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
