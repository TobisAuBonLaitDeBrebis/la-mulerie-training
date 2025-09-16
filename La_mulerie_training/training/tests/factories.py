import factory
from training.models import Horse, TrainingSession

class HorseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Horse

    nom = factory.Faker('first_name')
    race = factory.Faker('word')
    age = factory.Faker('pyint', min_value=1, max_value=30)

class TrainingSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TrainingSession

    cheval = factory.SubFactory(HorseFactory)
    date = factory.Faker('date_this_year')
    type_seance = factory.Faker('word')
    duree = factory.Faker('pyint', min_value=10, max_value=180)
    notes = factory.Faker('sentence')