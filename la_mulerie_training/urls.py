from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('training.urls')),
    # API v1
    path('api/v1/', include('api.urls')),
    # Contrat OpenAPI machine-readable (aucune donnee utilisateur exposee).
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]

# Interface SwaggerUI : desactivee en production (API_SERVE_DOCS=False).
if getattr(settings, 'API_SERVE_DOCS', False):
    urlpatterns += [
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    ]
