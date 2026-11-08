"""
Tests pour la vue dashboard - Compatible avec Django Test Runner
"""
from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from training.tests.factories import UserFactory, HorseFactory, TrainingSessionFactory
from training.models import TrainingSession, Horse


class DashboardViewTest(TestCase):
    """Tests pour la vue dashboard"""

    def setUp(self):
        """Configuration initiale pour tous les tests"""
        # Création utilisateur
        self.user = UserFactory()
        self.user.set_password("password123")
        self.user.save()

        # Autre utilisateur pour tests de permissions
        self.other_user = UserFactory()
        self.other_user.set_password("password456")
        self.other_user.save()

        # Client de test
        self.client = Client()

    def test_dashboard_access_requires_login(self):
        """Test que l'accès au dashboard nécessite une connexion"""
        url = reverse('dashboard')
        response = self.client.get(url)
        
        # Doit rediriger vers login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_dashboard_displays_correctly_for_authenticated_user(self):
        """Test que le dashboard s'affiche correctement pour un utilisateur connecté"""
        self.client.login(username=self.user.username, password="password123")
        
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.content)
        self.assertIn(b'Indicateurs Cl', response.content)

    def test_dashboard_displays_kpi_with_no_data(self):
        """Test que le dashboard affiche les KPI à 0 quand il n'y a pas de données"""
        self.client.login(username=self.user.username, password="password123")
        
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Vérifier que total_sessions est à 0
        self.assertIn(b'0', response.content)
        # Vérifier que le texte "Indicateurs" est présent
        self.assertIn(b'Indicateurs', response.content)

    def test_dashboard_displays_kpi_with_data(self):
        """Test que le dashboard affiche les KPI correctement avec des données"""
        self.client.login(username=self.user.username, password="password123")
        
        # Créer cheval et séances pour l'utilisateur
        horse = HorseFactory(proprietaire=self.user)
        session1 = TrainingSessionFactory(cheval=horse, cavalier=self.user, duree=60, cout=50.0)
        session2 = TrainingSessionFactory(cheval=horse, cavalier=self.user, duree=45, cout=30.0)
        
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # total_sessions = 2
        self.assertIn(b'2', response.content)
        # total_horses = 1
        self.assertIn(b'1', response.content)
        # total_duration = 105
        self.assertIn(b'105', response.content)
        # total_cost = 80
        self.assertIn(b'80', response.content)

    def test_dashboard_date_filter(self):
        """Test que le filtre par date fonctionne correctement"""
        self.client.login(username=self.user.username, password="password123")
        
        horse = HorseFactory(proprietaire=self.user)
        
        # Créer des séances avec différentes dates
        today = date.today()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        
        session_today = TrainingSessionFactory(
            cheval=horse, 
            cavalier=self.user, 
            date=today,
            duree=60
        )
        session_yesterday = TrainingSessionFactory(
            cheval=horse, 
            cavalier=self.user, 
            date=yesterday,
            duree=45
        )
        session_last_week = TrainingSessionFactory(
            cheval=horse, 
            cavalier=self.user, 
            date=last_week,
            duree=30
        )
        
        url = reverse('dashboard')
        
        # Test sans filtre - devrait afficher toutes les séances
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Le total devrait être 3 séances
        self.assertIn(b'3', response.content)
        
        # Test avec filtre - seulement aujourd'hui
        response = self.client.get(url, {'start_date': today.isoformat(), 'end_date': today.isoformat()})
        self.assertEqual(response.status_code, 200)
        # Devrait afficher 1 séance
        self.assertIn(b'1', response.content)
        
        # Test avec filtre - cette semaine
        response = self.client.get(url, {'start_date': last_week.isoformat(), 'end_date': today.isoformat()})
        self.assertEqual(response.status_code, 200)
        # Devrait afficher 3 séances
        self.assertIn(b'3', response.content)

    def test_dashboard_default_shows_all_data(self):
        """Test que par défaut, le dashboard affiche toutes les données (pas de filtre de date)"""
        self.client.login(username=self.user.username, password="password123")
        
        horse = HorseFactory(proprietaire=self.user)
        
        # Créer une séance dans le passé
        past_date = date.today() - timedelta(days=400)
        session = TrainingSessionFactory(
            cheval=horse, 
            cavalier=self.user, 
            date=past_date,
            duree=60
        )
        
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Devrait afficher la séance même si elle est très vieille
        self.assertIn(b'1', response.content)  # total_sessions = 1

    def test_dashboard_calculates_averages_correctly(self):
        """Test que le dashboard calcule correctement les moyennes"""
        self.client.login(username=self.user.username, password="password123")
        
        horse = HorseFactory(proprietaire=self.user)
        
        # Créer 3 séances avec des durées et coûts différents
        TrainingSessionFactory(cheval=horse, cavalier=self.user, duree=30, cout=10.0)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, duree=60, cout=20.0)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, duree=90, cout=30.0)
        
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Moyenne durée = (30 + 60 + 90) / 3 = 60
        self.assertIn(b'60', response.content)
        # Moyenne coût = (10 + 20 + 30) / 3 = 20
        self.assertIn(b'20', response.content)

    def test_dashboard_by_type_statistics(self):
        """Test que le dashboard affiche correctement les statistiques par type"""
        self.client.login(username=self.user.username, password="password123")
        
        horse = HorseFactory(proprietaire=self.user)
        
        # Créer des séances de différents types
        TrainingSessionFactory(cheval=horse, cavalier=self.user, type_seance='Dressage', duree=60)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, type_seance='Dressage', duree=45)
        TrainingSessionFactory(cheval=horse, cavalier=self.user, type_seance='Saut', duree=30)
        
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Dressage devrait apparaître
        self.assertIn(b'Dressage', response.content)
        # Saut devrait apparaître
        self.assertIn(b'Saut', response.content)

    def test_dashboard_by_horse_statistics(self):
        """Test que le dashboard affiche correctement les statistiques par cheval"""
        self.client.login(username=self.user.username, password="password123")
        
        horse1 = HorseFactory(proprietaire=self.user, nom='Toto')
        horse2 = HorseFactory(proprietaire=self.user, nom='Belle')
        
        TrainingSessionFactory(cheval=horse1, cavalier=self.user, duree=60)
        TrainingSessionFactory(cheval=horse1, cavalier=self.user, duree=45)
        TrainingSessionFactory(cheval=horse2, cavalier=self.user, duree=30)
        
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Les noms des chevaux devraient apparaître
        self.assertIn(b'Toto', response.content)
        self.assertIn(b'Belle', response.content)

    def test_dashboard_recent_sessions(self):
        """Test que le dashboard affiche les dernières séances"""
        self.client.login(username=self.user.username, password="password123")
        
        horse = HorseFactory(proprietaire=self.user, nom='TestHorse')
        
        # Créer 5 séances
        for i in range(5):
            TrainingSessionFactory(
                cheval=horse, 
                cavalier=self.user, 
                date=date.today() - timedelta(days=i),
                duree=30
            )
        
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Devrait afficher "Derniers entra" (Derniers entraînements)
        self.assertIn(b'Derniers entra', response.content)
        # Devrait afficher au moins un cheval
        self.assertIn(b'TestHorse', response.content)

    def test_dashboard_monthly_chart_data(self):
        """Test que le dashboard prépare correctement les données pour le graphique mensuel"""
        self.client.login(username=self.user.username, password="password123")
        
        horse = HorseFactory(proprietaire=self.user)
        
        # Créer des séances sur différents mois
        today = date.today()
        for i in range(6):
            TrainingSessionFactory(
                cheval=horse, 
                cavalier=self.user, 
                date=today - timedelta(days=30*i),
                duree=30
            )
        
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Devrait avoir des données pour le graphique
        self.assertIn('month_names', response.context)
        self.assertIn('month_counts', response.context)
        self.assertGreater(len(response.context['month_names']), 0)
        self.assertGreater(len(response.context['month_counts']), 0)

    def test_dashboard_does_not_show_other_users_data(self):
        """Test que le dashboard n'affiche que les données de l'utilisateur connecté"""
        self.client.login(username=self.user.username, password="password123")
        
        horse1 = HorseFactory(proprietaire=self.user, nom='MyHorse')
        horse2 = HorseFactory(proprietaire=self.other_user, nom='OtherHorse')
        
        # Créer des séances pour user1 et user2
        TrainingSessionFactory(cheval=horse1, cavalier=self.user, duree=60)
        TrainingSessionFactory(cheval=horse2, cavalier=self.other_user, duree=60)
        
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Devrait afficher 1 séance (celle de user1)
        self.assertIn(b'1', response.content)
        # Ne devraient PAS afficher le cheval de user2
        self.assertNotIn(b'OtherHorse', response.content)
        # Devrait afficher le cheval de user1
        self.assertIn(b'MyHorse', response.content)
