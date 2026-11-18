"""
DRF settings for la_mulerie_training project.
Central configuration for Django REST Framework and JWT authentication.
"""

from datetime import timedelta

# DRF Default settings
REST_FRAMEWORK = {
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    
    # Permission
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # Throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    
    # Error handling
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
}

# JWT Settings - Base configuration
# SIGNING_KEY and SECRET_KEY must be set in the main settings file
SIMPLE_JWT = {
    # Token life times
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    
    # Token rotation
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    
    # Token type claims
    'ALGORITHM': 'HS256',
    # SIGNING_KEY will be set in dev.py/prod.py to settings.SECRET_KEY
    'VERIFYING_KEY': None,
    
    # Audience and issuer
    'AUDIENCE': None,
    'ISSUER': None,
    
    # Token headers
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    # User identifier
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    # Token cookie settings
    'AUTH_COOKIE': None,
    'AUTH_COOKIE_DOMAIN': None,
    'AUTH_COOKIE_PATH': '/',
    'AUTH_COOKIE_SAMESITE': 'Lax',
    
    # Auth token classes
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}
