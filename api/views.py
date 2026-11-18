from django.db import IntegrityError, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics

from training.models import Horse, TrainingSession
from .serializers import UserSerializer, HorseSerializer, TrainingSessionSerializer, payload_matches


class MeView(APIView):
    """
    Endpoint /api/v1/me/ - Retourne les informations de profil de l'utilisateur authentifié.
    Seuls les champs nécessaires au mobile sont exposés.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HorseListView(generics.ListAPIView):
    """
    Endpoint /api/v1/horses/ - Liste des equides accessibles a l'utilisateur authentifie.

    La regle d'acces du lot 01 est appliquee au niveau queryset : un
    utilisateur ne peut voir que les equides dont il est proprietaire.
    """
    serializer_class = HorseSerializer

    def get_queryset(self):
        return Horse.objects.filter(proprietaire=self.request.user).order_by('id')


class HorseDetailView(generics.RetrieveAPIView):
    """
    Endpoint /api/v1/horses/{id}/ - Detail d'un equide accessible.

    Le queryset filtre sur le proprietaire : un equide inaccessible
    renvoie 404 sans reveler son existence.
    """
    serializer_class = HorseSerializer

    def get_queryset(self):
        return Horse.objects.filter(proprietaire=self.request.user)


class TrainingSessionListView(generics.ListCreateAPIView):
    """
    Endpoints /api/v1/sessions/ - Liste et creation des seances.

    Lecture : seules les seances du cavalier authentifie sont visibles
    (regle appliquee au niveau queryset, comme pour les vues web).

    Creation : identifiée par le couple (cavalier, client_uuid) ;
    le cavalier est deflecte par le serveur a partir de l'utilisateur
    authentifie. Le rejeu du meme UUID est gere de maniere idempotente :
    - meme contenu : la seance existante est renvoyee (200) ;
    - contenu different : conflit explicite (409) ;
    - collision concurrente : protegee par la contrainte unique en base.
    """
    serializer_class = TrainingSessionSerializer

    def get_queryset(self):
        return (
            TrainingSession.objects
            .filter(cavalier=self.request.user)
            .select_related('cheval')
            .order_by('id')
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        client_uuid = validated['client_uuid']

        replay = TrainingSession.objects.filter(
            cavalier=request.user, client_uuid=client_uuid,
        ).first()
        if replay is not None:
            return self._idempotent_response(replay, validated)

        creation_data = {}
        try:
            with transaction.atomic():
                # cavalier derive du serveur ; jamais du payload.
                session = serializer.save(cavalier=request.user)
                creation_data = self.get_serializer(session).data
        except IntegrityError:
            # Collision concurrente : la contrainte unique en base garantit
            # qu'une seule seance existe pour ce couple (cavalier, client_uuid).
            replay = TrainingSession.objects.filter(
                cavalier=request.user, client_uuid=client_uuid,
            ).first()
            if replay is None:
                raise
            return self._idempotent_response(replay, validated)

        return Response(creation_data, status=status.HTTP_201_CREATED)

    def _idempotent_response(self, session, validated):
        """Reponse de rejeu : succes si le contenu correspond, conflit sinon."""
        if payload_matches(session, validated):
            data = self.get_serializer(session).data
            return Response(data, status=status.HTTP_200_OK)
        return Response(
            {
                'detail': (
                    "Cette cle d'idempotence (client_uuid) est deja associee "
                    "a une seance differente."
                ),
                'session_id': session.id,
            },
            status=status.HTTP_409_CONFLICT,
        )


class TrainingSessionDetailView(generics.RetrieveAPIView):
    """
    Endpoint /api/v1/sessions/{id}/ - Detail d'une seance du cavalier.

    Le queryset filtre sur le cavalier : une seance d'un autre utilisateur
    renvoie 404 sans reveler son existence.
    """
    serializer_class = TrainingSessionSerializer

    def get_queryset(self):
        return (
            TrainingSession.objects
            .filter(cavalier=self.request.user)
            .select_related('cheval')
        )
