from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

app_name = 'api'

# Router pour les vues basées sur ViewSet (si besoin plus tard)
router = DefaultRouter()

urlpatterns = [
    # Endpoints JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Endpoint me
    path('me/', views.MeView.as_view(), name='me'),

    # Endpoints chevaux (lecture seule)
    path('horses/', views.HorseListView.as_view(), name='horse-list'),
    path('horses/<int:pk>/', views.HorseDetailView.as_view(), name='horse-detail'),
]
