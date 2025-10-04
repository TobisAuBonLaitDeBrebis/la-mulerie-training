from django.test import TestCase
from django.urls import reverse
from datetime import date
from training.tests.factories import UserFactory, HorseFactory, TrainingSessionFactory
from training.models import Horse, TrainingSession  

class TrainingViewsTest(TestCase):

    def setUp(self):
        # Création des utilisateurs
        self.user = UserFactory()
        self.user.set_password("password123")
        self.user.save()

        self.other_user = UserFactory()
        self.other_user.set_password("password123")
        self.other_user.save()

        # Cheval appartenant à self.user
        self.horse = HorseFactory(proprietaire=self.user)

        # Séance associée à ce cheval et utilisateur
        self.session = TrainingSessionFactory(
            cheval=self.horse,
            cavalier=self.user,
            type_seance="Dressage",
            duree=45,
            date=date.today(),
            notes="Bonne séance"
        )

        # Connexion utilisateur pour les tests
        self.client.login(username=self.user.username, password="password123")

    def test_home_view(self):
        """
        python manage.py test training.tests.test_views.TrainingViewsTest.test_home_view
        """
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.horse.nom)
        self.assertContains(response, self.session.type_seance)

    def test_horse_detail_view(self):
        """
        python manage.py test training.tests.test_views.TrainingViewsTest.test_horse_detail_view
        """
        url = reverse("horse_detail", args=[self.horse.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.horse.nom)

    def test_horse_add_view(self):
        """
        python manage.py test training.tests.test_views.TrainingViewsTest.test_horse_add_view
        """
        url = reverse("horse_add")
        response = self.client.post(url, {"nom": "Tornado","race": "Pur-sang","age": 5})
   
        self.assertEqual(response.status_code, 302)  # redirection vers home
        self.assertTrue(Horse.objects.filter(nom="Tornado").exists())

    def test_training_add_view_with_horse_pk(self):
        """
        python manage.py test training.tests.test_views.TrainingViewsTest.test_training_add_view_with_horse_pk
        """
        url = reverse("training_add", args=[self.horse.pk])
        response = self.client.post(url, {
            "type_seance": "Obstacle",
            "duree": 30,
            "date": "2025-09-17",
            "notes": "Test saut",
            "cheval": self.horse.pk  # Ajout du cheval dans les données du formulaire
        })
 
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TrainingSession.objects.filter(type_seance="Obstacle").exists())

    def test_training_add_view_without_horse_pk(self):
        """
        python manage.py test training.tests.test_views.TrainingViewsTest.test_training_add_view_without_horse_pk
        """
        url = reverse("training_add_global")
        response = self.client.post(url, {
            "cheval": self.horse.pk,
            "type_seance": "Endurance",
            "duree": 60,
            "date": "2025-09-17",
            "notes": "Longue sortie"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TrainingSession.objects.filter(type_seance="Endurance").exists())

    def test_horse_delete_view(self):
        """
        python manage.py test training.tests.test_views.TrainingViewsTest.test_horse_delete_view
        """
        url = reverse("horse_delete", args=[self.horse.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Horse.objects.filter(pk=self.horse.pk).exists())

    def test_training_delete_view(self):
        """
        python manage.py test training.tests.test_views.TrainingViewsTest.test_training_delete_view
        """
        url = reverse("training_delete", args=[self.session.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TrainingSession.objects.filter(pk=self.session.pk).exists())

    def test_cannot_access_other_users_horse(self):
        """
        python manage.py test training.tests.test_views.TrainingViewsTest.test_cannot_access_other_users_horse
        """
        other_horse = HorseFactory(proprietaire=self.other_user)
        url = reverse("horse_detail", args=[other_horse.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_other_users_training(self):
        """
        python manage.py test training.tests.test_views.TrainingViewsTest.test_cannot_delete_other_users_training
        """
        other_horse = HorseFactory(proprietaire=self.other_user)
        other_training = TrainingSessionFactory(cheval=other_horse, cavalier=self.other_user)
        url = reverse("training_delete", args=[other_training.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
