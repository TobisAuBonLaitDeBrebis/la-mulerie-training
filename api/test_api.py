import contextlib
import uuid as uuid_module
from datetime import date, timedelta
from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from training.models import TrainingSession
from training.tests.factories import HorseFactory, TrainingSessionFactory, UserFactory
from api.serializers import TrainingSessionSerializer

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


def session_payload(horse, **overrides):
    """Payload de creation de seance, surchargable pour les conflits."""
    payload = {
        'client_uuid': str(uuid_module.uuid4()),
        'cheval': horse.id,
        'date': '2025-11-10',
        'type_seance': 'dressage',
        'duree': 45,
        'cout': '50.00',
        'notes': 'seance test',
    }
    payload.update(overrides)
    return payload


class TrainingSessionApiTestCase(TestCase):
    """Tests pour les endpoints /api/v1/sessions/ (lecture + creation)."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='rider', password='riderpass123',
        )
        self.other_user = User.objects.create_user(
            username='otherrider', password='otherpass123',
        )
        self.horse = HorseFactory(nom='Morange', proprietaire=self.user)
        self.other_horse = HorseFactory(nom='Etranger', proprietaire=self.other_user)

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    # ---------- Lecture ----------

    def test_list_requires_authentication(self):
        response = self.client.get(reverse('api:session-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_requires_authentication(self):
        session = TrainingSessionFactory(cheval=self.horse, cavalier=self.user)
        response = self.client.get(reverse('api:session-detail', args=[session.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_returns_only_own_sessions(self):
        own = TrainingSessionFactory(cheval=self.horse, cavalier=self.user)
        TrainingSessionFactory(cheval=self.other_horse, cavalier=self.other_user)

        self.authenticate()
        response = self.client.get(reverse('api:session-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], own.id)

    def test_detail_of_other_user_session_returns_404(self):
        session = TrainingSessionFactory(cheval=self.other_horse, cavalier=self.other_user)
        self.authenticate()
        response = self.client.get(reverse('api:session-detail', args=[session.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_of_own_session_returns_200(self):
        session = TrainingSessionFactory(cheval=self.horse, cavalier=self.user)
        self.authenticate()
        response = self.client.get(reverse('api:session-detail', args=[session.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cheval'], self.horse.id)
        self.assertEqual(response.data['type_seance'], session.type_seance)

    # ---------- Creation ----------

    def test_create_returns_201_with_data(self):
        self.authenticate()
        payload = session_payload(self.horse)
        response = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        session = TrainingSession.objects.get(client_uuid=payload['client_uuid'])
        self.assertEqual(session.cavalier, self.user)
        self.assertEqual(session.cheval, self.horse)
        self.assertEqual(session.type_seance, 'dressage')
        self.assertEqual(str(session.cout), '50.00')

    def test_create_ignores_cavalier_from_payload(self):
        """Le cavalier est deflecte par le serveur, jamais par le client."""
        self.authenticate()
        payload = session_payload(self.horse, cavalier=self.other_user.id)
        response = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        session = TrainingSession.objects.get(client_uuid=payload['client_uuid'])
        self.assertEqual(session.cavalier, self.user)

    def test_create_with_inaccessible_horse_refused(self):
        """Un equide appartenant a un autre utilisateur est refuse (400)."""
        self.authenticate()
        payload = session_payload(self.other_horse)
        response = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TrainingSession.objects.count(), 0)

    def test_create_with_nonexistent_horse_refused(self):
        self.authenticate()
        payload = session_payload(self.horse, cheval=9999)
        response = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_fields_returns_400_without_partial_session(self):
        self.authenticate()
        payload = session_payload(self.horse)
        del payload['type_seance']
        response = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TrainingSession.objects.count(), 0)

    def test_create_with_invalid_client_uuid_refused(self):
        self.authenticate()
        payload = session_payload(self.horse, client_uuid='not-a-uuid')
        response = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TrainingSession.objects.count(), 0)

    def test_create_missing_client_uuid_refused(self):
        """Sans UUID client, la creation n'est pas idempotente : elle est refusee."""
        self.authenticate()
        payload = session_payload(self.horse)
        del payload['client_uuid']
        response = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TrainingSession.objects.count(), 0)

    def test_create_requires_authentication(self):
        payload = session_payload(self.horse)
        response = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(TrainingSession.objects.count(), 0)

    # ---------- Idempotence ----------

    def test_replay_same_uuid_same_payload_returns_existing(self):
        payload = session_payload(self.horse)
        self.authenticate()
        first = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(second.data['id'], first.data['id'])
        self.assertEqual(TrainingSession.objects.count(), 1)

    def test_replay_same_uuid_different_payload_returns_409(self):
        payload = session_payload(self.horse)
        self.authenticate()
        first = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        conflicted = dict(payload, duree=90)
        second = self.client.post(reverse('api:session-list'), conflicted, format='json')
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)

        # La seance originale n'a pas ete ecrasee
        session = TrainingSession.objects.get(client_uuid=payload['client_uuid'])
        self.assertEqual(session.duree, 45)
        self.assertEqual(TrainingSession.objects.count(), 1)

    def test_same_uuid_from_another_user_is_isolated(self):
        """Le meme UUID utilise par un autre cavalier ne leak pas la seance d'autrui."""
        other_horse_own = HorseFactory(proprietaire=self.other_user)
        payload = session_payload(self.horse)
        self.authenticate()
        own_response = self.client.post(reverse('api:session-list'), payload, format='json')
        self.assertEqual(own_response.status_code, status.HTTP_201_CREATED)

        # Un autre utilisateur rejoue le meme UUID avec son propre cheval
        self.authenticate(self.other_user)
        other_payload = dict(
            session_payload(other_horse_own, client_uuid=payload['client_uuid']),
            notes='seance autre cavalier',
        )
        other_response = self.client.post(reverse('api:session-list'), other_payload, format='json')
        self.assertEqual(other_response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(other_response.data['id'], own_response.data['id'])
        self.assertEqual(other_response.data['client_uuid'], payload['client_uuid'])
        self.assertEqual(TrainingSession.objects.count(), 2)

    def test_web_sessions_without_uuid_remain_allowed(self):
        """Contrainte unique : plusieurs seances sans client_uuid (web) sont tolerees."""
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user)
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user)
        self.assertEqual(TrainingSession.objects.count(), 2)

    def test_unique_constraint_blocks_duplicate_key(self):
        """La contrainte en base protege la paire (cavalier, client_uuid)."""
        uuid_value = uuid_module.uuid4()
        TrainingSessionFactory(
            cheval=self.horse, cavalier=self.user, client_uuid=uuid_value,
        )
        with self.assertRaises(IntegrityError):
            TrainingSessionFactory(
                cheval=self.horse, cavalier=self.user, client_uuid=uuid_value,
            )


class TrainingSessionCollisionTestCase(TransactionTestCase):
    """
    Chemin de collision concurrente : la requete perdante recoit la seance
    qui a gagne la course (200) grace au rattrapage post-IntegrityError.
    TransactionTestCase pour que la creation "gagnante" soit reellement
    commitee avant le rollback de la requete perdante.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='racer', password='racerpass123')
        self.horse = HorseFactory(proprietaire=self.user)

    def _post_with_simulated_winner(self, payload, winner_type_seance):
        """
        Simule deux createurs concurrents : le gagnant commite la seance pour
        cette cle d'idempotence, puis l'INSERT du perdant echoue sur la
        contrainte unique. Le bloc atomic de la vue est neutralise pour que la
        creation du gagnant ne soit pas annulee par le rollback du perdant,
        comme ce serait le cas avec deux transactions separees.
        """
        def simulate_winning_racer(*args, **kwargs):
            TrainingSession.objects.create(
                cheval=self.horse,
                cavalier=self.user,
                client_uuid=payload['client_uuid'],
                date=payload['date'],
                type_seance=winner_type_seance,
                duree=payload['duree'],
                cout=payload.get('cout'),
                notes=payload.get('notes'),
            )
            raise IntegrityError('UNIQUE constraint failed: uniq_cavalier_client_uuid')

        with patch.object(TrainingSessionSerializer, 'save', side_effect=simulate_winning_racer), \
                patch('api.views.transaction.atomic', contextlib.nullcontext):
            return self.client.post(reverse('api:session-list'), payload, format='json')

    def test_collision_with_same_payload_returns_existing_session(self):
        self.client.force_authenticate(user=self.user)
        payload = session_payload(self.horse)
        response = self._post_with_simulated_winner(payload, payload['type_seance'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # exactement une seance pour cette cle, pas de doublon
        self.assertEqual(
            TrainingSession.objects.filter(client_uuid=payload['client_uuid']).count(),
            1,
        )

    def test_collision_with_different_payload_returns_409(self):
        self.client.force_authenticate(user=self.user)
        payload = session_payload(self.horse)
        response = self._post_with_simulated_winner(payload, 'autre')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # la seance gagnante n'a pas ete ecrasee
        session = TrainingSession.objects.get(client_uuid=payload['client_uuid'])
        self.assertEqual(session.type_seance, 'autre')


class TrainingSessionConcurrencyTestCase(TransactionTestCase):
    """
    Verification de la garantie de non-doublon sous creation concurrente.

    Un test threade reel n'est pas fiable sur SQLite en memoire partagee
    (erreur 'database table is locked' entre deux ecrivains). On verifie
    donc de facon deterministe que :
    - la contrainte unique (cavalier, client_uuid) est bien posee en base ;
    - le chemin post-IntegrityError (Classe TrainingSessionCollisionTestCase)
      renvoie la seance gagnante sans doublon.
    """

    def test_two_creations_same_key_use_single_row(self):
        user = UserFactory(username='concurrent')
        horse = HorseFactory(proprietaire=user)
        key = uuid_module.uuid4()
        payload = dict(
            session_payload(horse, client_uuid=str(key)),
            type_seance='dressage',
        )
        serializer = TrainingSessionSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save(cavalier=user)

        with self.assertRaises(IntegrityError):
            TrainingSession.objects.create(
                cheval=horse,
                cavalier=user,
                client_uuid=key,
                date=payload['date'],
                type_seance=payload['type_seance'],
                duree=payload['duree'],
            )

        self.assertEqual(
            TrainingSession.objects.filter(client_uuid=key).count(),
            1,
        )


class DashboardApiTestCase(TestCase):
    """Tests pour GET /api/v1/dashboard/."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='dashuser', password='dashpass123',
        )
        self.other_user = User.objects.create_user(
            username='otherdash', password='otherdash123',
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def test_requires_authentication(self):
        response = self.client.get(reverse('api:dashboard'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_expected_indicators(self):
        horse = HorseFactory(proprietaire=self.user, nom='Morange')
        TrainingSessionFactory(cheval=horse, cavalier=self.user, duree=30, cout='10.00')
        TrainingSessionFactory(cheval=horse, cavalier=self.user, duree=60, cout='20.00')

        self.authenticate()
        response = self.client.get(reverse('api:dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['total_sessions'], 2)
        self.assertEqual(response.data['total_horses'], 1)
        self.assertEqual(response.data['total_duration'], 90)
        self.assertEqual(float(response.data['total_cost']), 30.0)
        self.assertEqual(response.data['avg_duration'], 45.0)
        self.assertEqual(float(response.data['avg_cost']), 15.0)
        self.assertEqual(response.data['sessions_per_horse'], 2.0)

    def test_isolation_between_users(self):
        other_horse = HorseFactory(proprietaire=self.other_user, nom='ChevalAutre')
        TrainingSessionFactory(cheval=other_horse, cavalier=self.other_user, duree=999)
        horse = HorseFactory(proprietaire=self.user)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, duree=10)

        self.authenticate()
        response = self.client.get(reverse('api:dashboard'))

        self.assertEqual(response.data['total_sessions'], 1)
        self.assertEqual(response.data['total_duration'], 10)

        # les equides comptes sont ceux du cavalier authentifie
        names = [s['cheval'] for s in response.data['sessions_by_horse']]
        self.assertNotIn('ChevalAutre', names)

    def test_period_filter_changes_totals_and_is_reported(self):
        horse = HorseFactory(proprietaire=self.user)
        today = date.today()
        TrainingSessionFactory(cheval=horse, cavalier=self.user, date=today, duree=60)
        TrainingSessionFactory(
            cheval=horse, cavalier=self.user,
            date=today - timedelta(days=60), duree=40,
        )

        self.authenticate()
        start = (today - timedelta(days=7)).isoformat()
        end = today.isoformat()
        response = self.client.get(
            reverse('api:dashboard'),
            {'start_date': start, 'end_date': end},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_sessions'], 1)
        self.assertEqual(response.data['period'], {'start_date': start, 'end_date': end})

    def test_period_boundaries_are_inclusive(self):
        horse = HorseFactory(proprietaire=self.user)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, date=date(2025, 1, 10), duree=10)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, date=date(2025, 1, 20), duree=20)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, date=date(2025, 1, 9), duree=1)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, date=date(2025, 1, 21), duree=1)

        self.authenticate()
        response = self.client.get(
            reverse('api:dashboard'),
            {'start_date': '2025-01-10', 'end_date': '2025-01-20'},
        )
        self.assertEqual(response.data['total_sessions'], 2)
        self.assertEqual(response.data['total_duration'], 30)

    def test_invalid_period_returns_400(self):
        self.authenticate()
        response = self.client.get(reverse('api:dashboard'), {'start_date': '10-01-2025'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recent_sessions_and_shape(self):
        horse = HorseFactory(proprietaire=self.user, nom='Morange')
        for i in range(7):
            TrainingSessionFactory(
                cheval=horse, cavalier=self.user,
                date=date.today() - timedelta(days=i), duree=10 + i,
            )

        self.authenticate()
        response = self.client.get(reverse('api:dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recent = response.data['recent_sessions']
        self.assertEqual(len(recent), 5)
        first = recent[0]
        self.assertEqual(
            set(first.keys()),
            {'id', 'date', 'type_seance', 'cheval', 'duree'},
        )
        self.assertEqual(set(response.data.keys()), {
            'total_sessions', 'total_horses', 'total_duration', 'total_cost',
            'avg_duration', 'avg_cost', 'sessions_per_horse',
            'sessions_by_type', 'sessions_by_horse', 'month_names',
            'month_counts', 'recent_sessions', 'sessions_dates', 'period',
        })

    def test_sessions_by_type_shape(self):
        horse = HorseFactory(proprietaire=self.user)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, type_seance='Dressage', duree=60)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, type_seance='Dressage', duree=45)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, type_seance='Saut', duree=30)

        self.authenticate()
        response = self.client.get(reverse('api:dashboard'))

        self.assertEqual(response.data['sessions_by_type'], [
            {'type_seance': 'Dressage', 'count': 2, 'total_duration': 105},
            {'type_seance': 'Saut', 'count': 1, 'total_duration': 30},
        ])
