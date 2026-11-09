"""
Tests de sécurité et d'intégrité métier — Lot 01
Vérifie les règles d'accès, les suppressions, et les contraintes de données.
"""
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from training.models import Horse, TrainingSession
from training.tests.factories import UserFactory, HorseFactory, TrainingSessionFactory
from datetime import date


class DeleteViewSecurityTest(TestCase):
    """Tests pour vérifier que les suppressions nécessitent POST et CSRF"""

    def setUp(self):
        self.user = UserFactory()
        self.user.set_password("password123")
        self.user.save()
        
        self.client = Client()
        self.client.login(username=self.user.username, password="password123")
        
        # Créer un cheval et une séance pour l'utilisateur
        self.horse = HorseFactory(proprietaire=self.user, nom="MonCheval")
        self.session = TrainingSessionFactory(
            cheval=self.horse,
            cavalier=self.user,
            type_seance="Dressage",
            duree=45
        )

    def test_horse_delete_requires_post(self):
        """Test que la suppression d'un cheval nécessite POST"""
        url = reverse('horse_delete', args=[self.horse.pk])
        
        # GET doit échouer (405 Method Not Allowed)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        
        # Vérifier que le cheval existe toujours
        self.assertTrue(Horse.objects.filter(pk=self.horse.pk).exists())

    def test_horse_delete_with_post(self):
        """Test que la suppression d'un cheval fonctionne avec POST"""
        url = reverse('horse_delete', args=[self.horse.pk])
        
        # POST doit fonctionner
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirection
        
        # Vérifier que le cheval a été supprimé
        self.assertFalse(Horse.objects.filter(pk=self.horse.pk).exists())

    def test_training_delete_requires_post(self):
        """Test que la suppression d'une séance nécessite POST"""
        url = reverse('training_delete', args=[self.session.pk])
        
        # GET doit échouer (405 Method Not Allowed)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        
        # Vérifier que la séance existe toujours
        self.assertTrue(TrainingSession.objects.filter(pk=self.session.pk).exists())

    def test_training_delete_with_post(self):
        """Test que la suppression d'une séance fonctionne avec POST"""
        url = reverse('training_delete', args=[self.session.pk])
        
        # POST doit fonctionner
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirection
        
        # Vérifier que la séance a été supprimée
        self.assertFalse(TrainingSession.objects.filter(pk=self.session.pk).exists())

    def test_cannot_delete_other_users_horse_via_get(self):
        """Test qu'un utilisateur ne peut pas supprimer le cheval d'un autre via GET"""
        other_user = UserFactory()
        other_user.set_password("password456")
        other_user.save()
        
        other_horse = HorseFactory(proprietaire=other_user, nom="SonCheval")
        
        url = reverse('horse_delete', args=[other_horse.pk])
        response = self.client.get(url)
        
        # Doit retourner 404 (objet non trouvé) ou 405 (méthode non autorisée)
        # Le plus probable est 404 car get_object_or_404 échoue
        self.assertIn(response.status_code, [404, 405])
        
        # Vérifier que le cheval existe toujours
        self.assertTrue(Horse.objects.filter(pk=other_horse.pk).exists())

    def test_cannot_delete_other_users_horse_via_post(self):
        """Test qu'un utilisateur ne peut pas supprimer le cheval d'un autre via POST"""
        other_user = UserFactory()
        other_user.set_password("password456")
        other_user.save()
        
        other_horse = HorseFactory(proprietaire=other_user, nom="SonCheval")
        
        url = reverse('horse_delete', args=[other_horse.pk])
        response = self.client.post(url)
        
        # Doit retourner 404 (objet non trouvé)
        self.assertEqual(response.status_code, 404)
        
        # Vérifier que le cheval existe toujours
        self.assertTrue(Horse.objects.filter(pk=other_horse.pk).exists())

    def test_cannot_delete_other_users_training_via_get(self):
        """Test qu'un utilisateur ne peut pas supprimer la séance d'un autre via GET"""
        other_user = UserFactory()
        other_user.set_password("password456")
        other_user.save()
        
        other_horse = HorseFactory(proprietaire=other_user, nom="SonCheval")
        other_session = TrainingSessionFactory(
            cheval=other_horse,
            cavalier=other_user,
            type_seance="Saut"
        )
        
        url = reverse('training_delete', args=[other_session.pk])
        response = self.client.get(url)
        
        # Doit retourner 404 ou 405
        self.assertIn(response.status_code, [404, 405])
        
        # Vérifier que la séance existe toujours
        self.assertTrue(TrainingSession.objects.filter(pk=other_session.pk).exists())

    def test_cannot_delete_other_users_training_via_post(self):
        """Test qu'un utilisateur ne peut pas supprimer la séance d'un autre via POST"""
        other_user = UserFactory()
        other_user.set_password("password456")
        other_user.save()
        
        other_horse = HorseFactory(proprietaire=other_user, nom="SonCheval")
        other_session = TrainingSessionFactory(
            cheval=other_horse,
            cavalier=other_user,
            type_seance="Saut"
        )
        
        url = reverse('training_delete', args=[other_session.pk])
        response = self.client.post(url)
        
        # Doit retourner 404 (objet non trouvé)
        self.assertEqual(response.status_code, 404)
        
        # Vérifier que la séance existe toujours
        self.assertTrue(TrainingSession.objects.filter(pk=other_session.pk).exists())


class ModelConstraintsTest(TestCase):
    """Tests pour vérifier les contraintes des modèles"""

    def setUp(self):
        self.user = UserFactory()
        self.user.set_password("password123")
        self.user.save()

    def test_duree_must_be_positive(self):
        """Test que la durée doit être positive (> 0)"""
        horse = HorseFactory(proprietaire=self.user)
        
        # Test avec durée = 0
        with self.assertRaises(Exception):
            TrainingSession.objects.create(
                cheval=horse,
                cavalier=self.user,
                duree=0,
                type_seance="Test",
                date=date.today()
            )
        
        # Test avec durée négative
        with self.assertRaises(Exception):
            TrainingSession.objects.create(
                cheval=horse,
                cavalier=self.user,
                duree=-10,
                type_seance="Test",
                date=date.today()
            )

    def test_cout_must_be_non_negative(self):
        """Test que le coût doit être non négatif (>= 0 ou NULL)"""
        horse = HorseFactory(proprietaire=self.user)
        
        # Test avec coût = 0 doit fonctionner
        session = TrainingSession(
            cheval=horse,
            cavalier=self.user,
            duree=60,
            type_seance="Test",
            date=date.today(),
            cout=0.0
        )
        session.save()
        self.assertEqual(session.cout, 0.0)
        session.delete()
        
        # Test avec coût négatif - doit échouer à cause de la contrainte
        # On utilise une session pour capturer l'exception
        session = TrainingSession(
            cheval=horse,
            cavalier=self.user,
            duree=60,
            type_seance="TestNegative",
            date=date.today(),
            cout=-10.0
        )
        # Le validateur MinValueValidator ou la contrainte devrait échouer
        try:
            session.full_clean()
            session.save()
            self.fail("Should have raised validation error for negative cout")
        except (django.core.exceptions.ValidationError, django.db.utils.IntegrityError):
            pass  # Expected

    def test_cout_can_be_null(self):
        """Test que le coût peut être NULL"""
        horse = HorseFactory(proprietaire=self.user)
        
        session = TrainingSession.objects.create(
            cheval=horse,
            cavalier=self.user,
            duree=60,
            type_seance="Test",
            date=date.today(),
            cout=None
        )
        self.assertIsNone(session.cout)
        session.delete()

    def test_proprietaire_required(self):
        """Test que le propriétaire est requis"""
        # Après migration, proprio ne doit plus être NULL
        with self.assertRaises(Exception):
            Horse.objects.create(
                nom="SansProprietaire",
                race="Test",
                birth_date=date.today(),
                proprietaire=None
            )

    def test_cavalier_required(self):
        """Test que le cavalier est requis"""
        horse = HorseFactory(proprietaire=self.user)
        
        # Après migration, cavalier ne doit plus être NULL
        with self.assertRaises(Exception):
            TrainingSession.objects.create(
                cheval=horse,
                cavalier=None,
                duree=60,
                type_seance="Test",
                date=date.today()
            )


class AccessControlTest(TestCase):
    """Tests pour vérifier le contrôle d'accès aux objets"""

    def setUp(self):
        self.user1 = UserFactory(username="user1")
        self.user1.set_password("password123")
        self.user1.save()
        
        self.user2 = UserFactory(username="user2")
        self.user2.set_password("password456")
        self.user2.save()
        
        self.client = Client()

    def test_user1_cannot_access_user2_horse_detail(self):
        """Test que user1 ne peut pas accéder au détail du cheval de user2"""
        horse2 = HorseFactory(proprietaire=self.user2, nom="ChevalUser2")
        
        self.client.login(username=self.user1.username, password="password123")
        url = reverse('horse_detail', args=[horse2.pk])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user1_cannot_access_user2_training_detail(self):
        """Test que user1 ne peut pas accéder au détail de la séance de user2"""
        horse2 = HorseFactory(proprietaire=self.user2, nom="ChevalUser2")
        session2 = TrainingSessionFactory(
            cheval=horse2,
            cavalier=self.user2,
            type_seance="Dressage"
        )
        
        self.client.login(username=self.user1.username, password="password123")
        url = reverse('training_detail', args=[session2.pk])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user1_cannot_edit_user2_horse(self):
        """Test que user1 ne peut pas modifier le cheval de user2"""
        horse2 = HorseFactory(proprietaire=self.user2, nom="ChevalUser2")
        
        self.client.login(username=self.user1.username, password="password123")
        url = reverse('horse_edit', args=[horse2.pk])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user1_cannot_edit_user2_training(self):
        """Test que user1 ne peut pas modifier la séance de user2"""
        horse2 = HorseFactory(proprietaire=self.user2, nom="ChevalUser2")
        session2 = TrainingSessionFactory(
            cheval=horse2,
            cavalier=self.user2,
            type_seance="Dressage"
        )
        
        self.client.login(username=self.user1.username, password="password123")
        url = reverse('training_edit', args=[session2.pk])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user1_can_access_own_horse(self):
        """Test que user1 peut accéder à son propre cheval"""
        horse1 = HorseFactory(proprietaire=self.user1, nom="MonCheval")
        
        self.client.login(username=self.user1.username, password="password123")
        url = reverse('horse_detail', args=[horse1.pk])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user1_can_access_own_training(self):
        """Test que user1 peut accéder à sa propre séance"""
        horse1 = HorseFactory(proprietaire=self.user1, nom="MonCheval")
        session1 = TrainingSessionFactory(
            cheval=horse1,
            cavalier=self.user1,
            type_seance="Dressage"
        )
        
        self.client.login(username=self.user1.username, password="password123")
        url = reverse('training_detail', args=[session1.pk])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_home_horses_only_shows_own_horses(self):
        """Test que home_horses n'affiche que les chevaux de l'utilisateur"""
        horse1 = HorseFactory(proprietaire=self.user1, nom="MonCheval")
        horse2 = HorseFactory(proprietaire=self.user2, nom="SonCheval")
        
        self.client.login(username=self.user1.username, password="password123")
        url = reverse('home_horses')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que seul le cheval de user1 est dans le contexte
        horses = response.context['horses']
        self.assertEqual(horses.count(), 1)
        self.assertEqual(horses.first().nom, "MonCheval")

    def test_home_training_only_shows_own_sessions(self):
        """Test que home_training n'affiche que les séances de l'utilisateur"""
        horse1 = HorseFactory(proprietaire=self.user1, nom="MonCheval")
        horse2 = HorseFactory(proprietaire=self.user2, nom="SonCheval")
        
        session1 = TrainingSessionFactory(
            cheval=horse1,
            cavalier=self.user1,
            type_seance="Dressage"
        )
        session2 = TrainingSessionFactory(
            cheval=horse2,
            cavalier=self.user2,
            type_seance="Saut"
        )
        
        self.client.login(username=self.user1.username, password="password123")
        url = reverse('home_training')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que seule la séance de user1 est dans le contexte
        sessions = response.context['sessions']
        self.assertEqual(sessions.count(), 1)
        self.assertEqual(sessions.first().type_seance, "Dressage")


class FormValidationTest(TestCase):
    """Tests pour vérifier la validation des formulaires"""

    def setUp(self):
        self.user = UserFactory()
        self.user.set_password("password123")
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username, password="password123")

    def test_training_form_rejects_zero_duree(self):
        """Test que le formulaire de séance rejette durée = 0"""
        horse = HorseFactory(proprietaire=self.user)
        
        url = reverse('training_add_global')
        data = {
            'cheval': horse.pk,
            'type_seance': 'Test',
            'duree': 0,
            'date': date.today().isoformat(),
            'notes': '',
            'cout': ''
        }
        
        response = self.client.post(url, data)
        # Doit retourner le formulaire avec des erreurs
        self.assertEqual(response.status_code, 200)
        self.assertIn('duree', response.context['form'].errors)

    def test_training_form_rejects_negative_cout(self):
        """Test que le formulaire de séance rejette coût négatif"""
        horse = HorseFactory(proprietaire=self.user)
        
        url = reverse('training_add_global')
        data = {
            'cheval': horse.pk,
            'type_seance': 'Test',
            'duree': 60,
            'date': date.today().isoformat(),
            'notes': '',
            'cout': -10.0
        }
        
        response = self.client.post(url, data)
        # Doit retourner le formulaire avec des erreurs
        self.assertEqual(response.status_code, 200)
        self.assertIn('cout', response.context['form'].errors)

    def test_training_form_accepts_valid_data(self):
        """Test que le formulaire de séance accepte des données valides"""
        horse = HorseFactory(proprietaire=self.user)
        
        url = reverse('training_add_global')
        data = {
            'cheval': horse.pk,
            'type_seance': 'Test',
            'duree': 60,
            'date': date.today().isoformat(),
            'notes': 'Test séance',
            'cout': 50.0
        }
        
        response = self.client.post(url, data)
        # Doit rediriger après succès
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la séance a été créée
        self.assertTrue(TrainingSession.objects.filter(type_seance='Test').exists())
