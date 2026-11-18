"""
Tests unitaires du service build_dashboard_data (lot 05).

Les calculs du service alimentent la vue web et l'API mobile : ces tests
verrouillent les valeurs exactes avant toute exposition.
"""
from datetime import date, timedelta

from django.test import TestCase

from training.services import build_dashboard_data
from training.tests.factories import HorseFactory, TrainingSessionFactory, UserFactory


class BuildDashboardDataTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.horse = HorseFactory(proprietaire=self.user, nom='Morange')

    def test_empty_data_returns_zeroes(self):
        data = build_dashboard_data(self.user)

        self.assertEqual(data['total_sessions'], 0)
        self.assertEqual(data['total_horses'], 1)  # le cheval du setUp
        self.assertEqual(data['total_duration'], 0)
        self.assertEqual(data['total_cost'], 0)
        self.assertEqual(data['avg_duration'], 0)
        self.assertEqual(data['avg_cost'], 0)
        self.assertEqual(data['sessions_per_horse'], 0.0)
        self.assertEqual(data['month_counts'], [0] * 12)

    def test_global_totals_and_averages(self):
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, duree=30, cout='10.00')
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, duree=60, cout='20.50')
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, duree=90, cout='30.00')

        data = build_dashboard_data(self.user)

        self.assertEqual(data['total_sessions'], 3)
        self.assertEqual(data['total_horses'], 1)
        self.assertEqual(data['total_duration'], 180)
        self.assertEqual(float(data['total_cost']), 60.5)
        self.assertEqual(data['avg_duration'], 60.0)
        self.assertEqual(float(data['avg_cost']), 20.17)  # arrondi au centime
        self.assertEqual(data['sessions_per_horse'], 3.0)

    def test_averages_are_zero_without_sessions(self):
        HorseFactory(proprietaire=self.user, nom='Belle')

        data = build_dashboard_data(self.user)

        self.assertEqual(data['total_horses'], 2)
        self.assertEqual(data['avg_duration'], 0)
        self.assertEqual(data['avg_cost'], 0)
        self.assertEqual(data['sessions_per_horse'], 0.0)

    def test_isolation_between_users(self):
        other_horse = HorseFactory(proprietaire=self.other_user, nom='ChevalAutre')
        TrainingSessionFactory(cheval=other_horse, cavalier=self.other_user, duree=999)

        data = build_dashboard_data(self.user)

        self.assertEqual(data['total_sessions'], 0)
        self.assertEqual(
            [item['count'] for item in data['sessions_by_horse']],
            [],
        )

    def test_sessions_counted_by_cavalier_not_ownership(self):
        """Le service compte les séances du cavalier, même sur un cheval d'autrui."""
        # le cavalier self.user monte le cheval de l'autre utilisateur
        TrainingSessionFactory(
            cheval=self.horse, cavalier=self.other_user, duree=20,
        )

        data = build_dashboard_data(self.other_user)

        self.assertEqual(data['total_sessions'], 1)

    def test_sessions_by_type(self):
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, type_seance='Dressage', duree=60)
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, type_seance='Dressage', duree=45)
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, type_seance='Saut', duree=30)

        data = build_dashboard_data(self.user)

        by_type = list(data['sessions_by_type'])
        self.assertEqual(
            [(item['type_seance'], item['count'], item['total_duration']) for item in by_type],
            [
                ('Dressage', 2, 105),
                ('Saut', 1, 30),
            ],
        )

    def test_sessions_by_horse(self):
        horse2 = HorseFactory(proprietaire=self.user, nom='Belle')
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, duree=60)
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, duree=45)
        TrainingSessionFactory(cheval=horse2, cavalier=self.user, duree=30)

        data = build_dashboard_data(self.user)

        by_horse = list(data['sessions_by_horse'])
        # tri par durée totale décroissante
        self.assertEqual(
            [(item['cheval__nom'], item['count'], item['total_duration']) for item in by_horse],
            [
                ('Morange', 2, 105),
                ('Belle', 1, 30),
            ],
        )

    def test_date_filter_limits_totals(self):
        today = date.today()
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, date=today, duree=60)
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, date=today - timedelta(days=30), duree=40)

        data = build_dashboard_data(self.user, start_date=today - timedelta(days=7))

        self.assertEqual(data['total_sessions'], 1)
        self.assertEqual(data['total_duration'], 60)
        # total_horses n'est pas affecte par le filtre de periode
        self.assertEqual(data['total_horses'], 1)

    def test_date_filter_boundaries_are_inclusive(self):
        start = date(2025, 1, 10)
        end = date(2025, 1, 20)
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, date=start, duree=10)
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, date=end, duree=20)
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, date=date(2025, 1, 9), duree=1)
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, date=date(2025, 1, 21), duree=1)

        data = build_dashboard_data(self.user, start_date=start, end_date=end)

        self.assertEqual(data['total_sessions'], 2)
        self.assertEqual(data['total_duration'], 30)

    def test_string_dates_are_accepted_like_the_web_view(self):
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, date=date(2025, 1, 15), duree=30)

        data = build_dashboard_data(self.user, start_date='2025-01-01', end_date='2025-01-31')

        self.assertEqual(data['total_sessions'], 1)

    def test_month_counts_without_filter_covers_current_year(self):
        current_year = date.today().year
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, date=date(current_year, 3, 10), duree=30)
        # une seance de l'annee passee ne doit pas apparaitre sans filtre
        TrainingSessionFactory(
            cheval=self.horse, cavalier=self.user,
            date=date(current_year - 1, 3, 10), duree=30,
        )

        data = build_dashboard_data(self.user)

        self.assertEqual(len(data['month_counts']), 12)
        self.assertEqual(data['month_counts'][2], 1)  # Mars

    def test_month_range_with_filter_follows_data(self):
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, date=date(2025, 2, 1), duree=30)
        TrainingSessionFactory(cheval=self.horse, cavalier=self.user, date=date(2025, 4, 1), duree=30)

        data = build_dashboard_data(self.user, start_date='2025-01-01', end_date='2025-12-31')

        self.assertEqual(data['month_names'], ['Février', 'Mars', 'Avril'])
        self.assertEqual(data['month_counts'], [1, 0, 1])

    def test_month_range_with_filter_but_no_data_is_full_year(self):
        data = build_dashboard_data(self.user, start_date='2030-01-01', end_date='2030-12-31')

        self.assertEqual(len(data['month_counts']), 12)
        self.assertEqual(len(data['month_names']), 12)

    def test_recent_sessions_limit_five(self):
        horse = HorseFactory(proprietaire=self.user)
        for i in range(7):
            TrainingSessionFactory(
                cheval=horse,
                cavalier=self.user,
                date=date.today() - timedelta(days=i),
                duree=10 + i,
            )

        data = build_dashboard_data(self.user)

        self.assertEqual(len(list(data['recent_sessions'])), 5)
        # les 5 plus recentes d'abord
        dates = [s.date for s in data['recent_sessions']]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_sessions_dates_shape(self):
        TrainingSessionFactory(
            cheval=self.horse, cavalier=self.user,
            date=date(2025, 1, 15), type_seance='Dressage', duree=30,
        )

        data = build_dashboard_data(self.user)

        self.assertEqual(data['sessions_dates'], [
            {
                'id': self.horse.trainings.first().id,
                'date': '2025-01-15',
                'activity': 'Dressage',
            },
        ])
