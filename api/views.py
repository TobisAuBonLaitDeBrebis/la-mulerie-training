from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics

from training.models import Horse
from .serializers import UserSerializer, HorseSerializer


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
