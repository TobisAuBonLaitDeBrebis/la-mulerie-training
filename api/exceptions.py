from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Gestionnaire d'exceptions personnalisé pour DRF.
    Ne divulgue pas les détails internes en production.
    """
    # Appeler le gestionnaire par défaut pour obtenir la réponse standard
    response = exception_handler(exc, context)
    
    if response is not None:
        # Personnaliser la réponse d'erreur
        error_data = {
            'error': True,
            'code': response.status_code,
            'message': str(exc) if response.status_code != status.HTTP_401_UNAUTHORIZED else 'Non autorisé',
        }
        
        # En mode debug, on peut ajouter plus de détails
        import django.conf
        if django.conf.settings.DEBUG:
            error_data['debug'] = str(exc)
        
        # Ne pas exposer les détails des erreurs de validation en production
        if not django.conf.settings.DEBUG and response.status_code == status.HTTP_400_BAD_REQUEST:
            error_data['message'] = 'Requête invalide'
        
        response.data = error_data
    
    return response
