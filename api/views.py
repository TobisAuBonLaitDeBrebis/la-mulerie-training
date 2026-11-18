from django.db import IntegrityError, transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics

from training.models import Horse, TrainingSession
from training.services import build_dashboard_data
from .serializers import (
    ApiErrorSerializer,
    DashboardFilterSerializer,
    DashboardSerializer,
    HorseSerializer,
    IdempotencyConflictSerializer,
    TrainingSessionSerializer,
    UserSerializer,
    payload_matches,
)

ERROR_RESPONSES = {
    '400': OpenApiResponse(ApiErrorSerializer, description='Requete invalide.'),
    '401': OpenApiResponse(ApiErrorSerializer, description='Authentification requise.'),
    '404': OpenApiResponse(ApiErrorSerializer, description='Ressource inexistante ou non autorisee.'),
}


class MeView(APIView):
    """
    Endpoint /api/v1/me/ - Retourne les informations de profil de l'utilisateur authentifié.
    Seuls les champs nécessaires au mobile sont exposés.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer, **ERROR_RESPONSES})
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

    @extend_schema(responses={200: HorseSerializer(many=True), **ERROR_RESPONSES})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Horse.objects.filter(proprietaire=self.request.user).order_by('id')


class HorseDetailView(generics.RetrieveAPIView):
    """
    Endpoint /api/v1/horses/{id}/ - Detail d'un equide accessible.

    Le queryset filtre sur le proprietaire : un equide inaccessible
    renvoie 404 sans reveler son existence.
    """
    serializer_class = HorseSerializer

    @extend_schema(responses={200: HorseSerializer, **ERROR_RESPONSES})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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

    @extend_schema(
        operation_id='listSessions',
        summary='Liste des seances du cavalier authentifie',
        responses={
            200: OpenApiResponse(TrainingSessionSerializer(many=True), description='Liste paginee (20 par page).'),
            **ERROR_RESPONSES,
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        operation_id='createSession',
        summary='Creation idempotente d une seance',
        description=(
            'Creation validee par le serveur. Le cavalier est derive de '
            'l utilisateur authentifie ; le cheval doit appartenir a l utilisateur.\n\n'
            '`client_uuid` (obligatoire) est genere par le mobile avant l envoi et '
            'conserve a l identique lors des retries :\n'
            '- 201 : premiere creation pour ce couple (cavalier, client_uuid) ;\n'
            '- 200 : rejeu du meme UUID avec le meme contenu, la seance existante '
            'est renvoyee sans doublon ;\n'
            '- 409 : meme UUID avec un contenu different, la seance existante n est '
            'pas ecrasee ;\n'
            '- 400 : validation refusee, aucune seance partielle.\n\n'
            'La contrainte unique (cavalier, client_uuid) en base garantit '
            'l absence de doublon en cas de collisions concurrentes.'
        ),
        responses={
            201: OpenApiResponse(TrainingSessionSerializer, description='Seance creee.'),
            200: OpenApiResponse(TrainingSessionSerializer, description='Rejeu idempotent : seance existante renvoyee.'),
            409: OpenApiResponse(IdempotencyConflictSerializer, description='Conflit : UUID client deja utilise avec un contenu different.'),
            **ERROR_RESPONSES,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

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

    @extend_schema(responses={200: TrainingSessionSerializer, **ERROR_RESPONSES})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            TrainingSession.objects
            .filter(cavalier=self.request.user)
            .select_related('cheval')
        )


class DashboardView(APIView):
    """
    Endpoint /api/v1/dashboard/ - Indicateurs du tableau de bord mobile.

    Reutilise exactement les calculs du tableau de bord web
    (training.services.build_dashboard_data). Filtres de periode inclusifs :
    ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """
    @extend_schema(
        parameters=[
            OpenApiParameter('start_date', OpenApiTypes.DATE, description='Borne de debut incluse (YYYY-MM-DD).'),
            OpenApiParameter('end_date', OpenApiTypes.DATE, description='Borne de fin incluse (YYYY-MM-DD).'),
        ],
        responses={200: DashboardSerializer, **ERROR_RESPONSES},
    )
    def get(self, request, *args, **kwargs):
        filter_serializer = DashboardFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        start_date = filter_serializer.validated_data.get('start_date')
        end_date = filter_serializer.validated_data.get('end_date')

        data = build_dashboard_data(request.user, start_date=start_date, end_date=end_date)
        data['period'] = {'start_date': start_date, 'end_date': end_date}

        output_serializer = DashboardSerializer(data)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
