from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class MeViewTestCase(TestCase):
    """Tests pour l'endpoint /api/v1/me/"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
    def test_me_requires_authentication(self):
        """Test que /api/v1/me/ refuse un utilisateur non authentifié"""
        response = self.client.get(reverse('api:me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_me_returns_user_data(self):
        """Test que /api/v1/me/ retourne les données utilisateur correctes"""
        # Authentifier l'utilisateur
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(reverse('api:me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
        self.assertTrue(data['is_active'])
        
        # Vérifier que seuls les champs autorisés sont présents
        expected_keys = {'id', 'username', 'email', 'first_name', 'last_name', 'is_active'}
        self.assertEqual(set(data.keys()), expected_keys)


class JWTAuthTestCase(TestCase):
    """Tests pour l'authentification JWT"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='jwtuser',
            password='jwtpass123',
            email='jwt@example.com'
        )
        
    def test_token_obtain_with_valid_credentials(self):
        """Test l'obtention de token avec des identifiants valides"""
        response = self.client.post(
            reverse('api:token_obtain_pair'),
            {'username': 'jwtuser', 'password': 'jwtpass123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_token_obtain_with_invalid_credentials(self):
        """Test l'obtention de token avec des identifiants invalides"""
        response = self.client.post(
            reverse('api:token_obtain_pair'),
            {'username': 'jwtuser', 'password': 'wrongpassword'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_token_refresh(self):
        """Test le rafraîchissement du token"""
        # Obtenir un token
        token_response = self.client.post(
            reverse('api:token_obtain_pair'),
            {'username': 'jwtuser', 'password': 'jwtpass123'},
            format='json'
        )
        refresh_token = token_response.data['refresh']
        
        # Rafraîchir le token
        refresh_response = self.client.post(
            reverse('api:token_refresh'),
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
        
    def test_token_refresh_with_invalid_token(self):
        """Test le rafraîchissement avec un token invalide"""
        response = self.client.post(
            reverse('api:token_refresh'),
            {'refresh': 'invalid.token.here'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_me_with_jwt_authentication(self):
        """Test l'accès à /api/v1/me/ avec authentification JWT"""
        # Obtenir un token
        token_response = self.client.post(
            reverse('api:token_obtain_pair'),
            {'username': 'jwtuser', 'password': 'jwtpass123'},
            format='json'
        )
        access_token = token_response.data['access']
        
        # Accéder à /me/ avec le token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(reverse('api:me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'jwtuser')
