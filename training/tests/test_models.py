from django.test import TestCase
from .factories import HorseFactory, TrainingSessionFactory

class HorseModelTest(TestCase):
    def test_create_horse(self):
        horse = HorseFactory()
        self.assertIsNotNone(horse.pk)
        self.assertTrue(horse.nom)
        self.assertTrue(horse.race)
        self.assertTrue(horse.age > 0)

class TrainingSessionModelTest(TestCase):
    def test_create_training_session(self):
        session = TrainingSessionFactory()
        self.assertIsNotNone(session.pk)
        self.assertIsNotNone(session.cheval)
        self.assertTrue(session.type_seance)
        self.assertTrue(session.duree > 0)
        self.assertTrue(isinstance(session.notes, str))