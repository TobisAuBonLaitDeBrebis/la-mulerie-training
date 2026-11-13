from django.db import models
from django.conf import settings


class BlacklistedToken(models.Model):
    """
    Modèle pour stocker les tokens JWT blacklistés.
    Utilisé par SimpleJWT pour la révocation des tokens.
    """
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Token blacklisté'
        verbose_name_plural = 'Tokens blacklistés'
    
    def __str__(self):
        return f"Blacklisted token: {self.token[:20]}..."
