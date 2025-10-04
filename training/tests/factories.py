import factory
from training.models import Horse, TrainingSession
from django.contrib.auth.models import User
import datetime

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")

class HorseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Horse

    nom = factory.Faker('first_name')
    race = factory.Faker('word')
    birth_date = factory.Faker('date_of_birth')

    @factory.post_generation
    def set_age(obj, create, extracted, **kwargs):
        if extracted:
            # calculer birth_date à partir de l’âge voulu
            today = datetime.date.today()
            obj.birth_date = today.replace(year=today.year - extracted)
            if create:
                obj.save()



class TrainingSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TrainingSession

    cheval = factory.SubFactory(HorseFactory)
    date = factory.Faker('date_this_year')
    type_seance = factory.Faker('word')
    duree = factory.Faker('pyint', min_value=10, max_value=180)
    notes = factory.Faker('sentence')