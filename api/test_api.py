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
from datetime import date

from training.tests.factories import HorseFactory, UserFactory


class HorseApiTestCase(TestCase):
    """Tests pour les endpoints /api/v1/horses/ (lecture seule)."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='horseowner',
            password='horsepass123',
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123',
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def test_list_requires_authentication(self):
        """Un utilisateur anonyme est refuse (401)."""
        HorseFactory(proprietaire=self.user)
        response = self.client.get(reverse('api:horse-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_returns_empty_list_when_no_horses(self):
        """Un utilisateur sans cheval obtient une liste vide."""
        self.authenticate()
        response = self.client.get(reverse('api:horse-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

    def test_list_returns_only_own_horses(self):
        """Un utilisateur ne voit pas les chevaux des autres utilisateurs."""
        own_horse = HorseFactory(nom='Morange', proprietaire=self.user)
        HorseFactory(nom='Etranger', proprietaire=self.other_user)

        self.authenticate()
        response = self.client.get(reverse('api:horse-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], own_horse.id)
        self.assertEqual(response.data['results'][0]['nom'], 'Morange')

    def test_list_returns_multiple_horses(self):
        """Tous les chevaux de l'utilisateur sont listes."""
        HorseFactory(proprietaire=self.user)
        HorseFactory(proprietaire=self.user)
        HorseFactory(proprietaire=self.other_user)

        self.authenticate()
        response = self.client.get(reverse('api:horse-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_list_pagination(self):
        """La pagination DRF renvoie 20 resultats par page."""
        HorseFactory.create_batch(25, proprietaire=self.user)

        self.authenticate()
        response = self.client.get(reverse('api:horse-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(len(response.data['results']), 20)
        self.assertIsNotNone(response.data['next'])

        page2 = self.client.get(response.data['next'])
        self.assertEqual(page2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page2.data['results']), 5)
        self.assertIsNone(page2.data['next'])

    def test_list_exposed_fields_exact(self):
        """Seuls les champs-prevus sont exposes, pas le proprietaire."""
        today = date.today()
        birth_date = today.replace(year=today.year - 5)
        HorseFactory(
            nom='Mule',
            race='Mulet',
            birth_date=birth_date,
            proprietaire=self.user,
        )

        self.authenticate()
        response = self.client.get(reverse('api:horse-list'))
        horse_data = response.data['results'][0]
        self.assertEqual(
            set(horse_data.keys()),
            {'id', 'nom', 'race', 'birth_date', 'age'},
        )
        self.assertEqual(horse_data['nom'], 'Mule')
        self.assertEqual(horse_data['race'], 'Mulet')
        self.assertEqual(horse_data['birth_date'], str(birth_date))
        self.assertEqual(horse_data['age'], 5)

    def test_detail_returns_horse(self):
        """Le detail d'un cheval de l'utilisateur est accessible."""
        horse = HorseFactory(nom='Morange', proprietaire=self.user)

        self.authenticate()
        response = self.client.get(reverse('api:horse-detail', args=[horse.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], horse.id)
        self.assertEqual(response.data['nom'], 'Morange')

    def test_detail_of_other_user_horse_returns_404(self):
        """Le detail d'un cheval non autorise renvoie 404 (existence non revelee)."""
        other_horse = HorseFactory(proprietaire=self.other_user)

        self.authenticate()
        response = self.client.get(reverse('api:horse-detail', args=[other_horse.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_of_nonexistent_horse_returns_404(self):
        """Un identifiant inexistant renvoie 404."""
        self.authenticate()
        response = self.client.get(reverse('api:horse-detail', args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_requires_authentication(self):
        """Le detail refuse un utilisateur anonyme."""
        horse = HorseFactory(proprietaire=self.user)
        response = self.client.get(reverse('api:horse-detail', args=[horse.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
