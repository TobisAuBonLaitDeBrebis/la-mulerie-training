from django.db import models
from django.db.models.functions import ExtractMonth
from datetime import datetime

from training.models import Horse, TrainingSession

MONTH_NAMES = [
    'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre',
]


def build_dashboard_data(user, start_date=None, end_date=None):
    """
    Calcule les indicateurs du tableau de bord d'un utilisateur.

    Composant partagé entre la vue web et l'API mobile (lot 05) : toute
    évolution d'un indicateur doit se faire ici, pour que les deux
    interfaces affichent toujours les mêmes chiffres.

    - user : l'utilisateur authentifié (les données sont filtrées sur
      ses séances de cavalier et ses équidés).
    - start_date / end_date : bornes de filtre sur la date de séance
      (date ou chaîne ISO acceptée, comme un filtre ORM) ; None = tout.

    Retourne un dictionnaire plat dont les clefs correspondent au
    contexte historique du template `dashboard.html` :
    `{cheval__nom}` est conservé pour rester compatible avec le rendu web.
    """
    date_filter = {}
    if start_date:
        date_filter['date__gte'] = start_date
    if end_date:
        date_filter['date__lte'] = end_date

    sessions_qs = TrainingSession.objects.filter(cavalier=user, **date_filter)

    total_sessions = sessions_qs.count()
    total_horses = Horse.objects.filter(proprietaire=user).count()

    total_duration = sessions_qs.aggregate(
        total=models.Sum('duree')
    )['total'] or 0

    total_cost = sessions_qs.aggregate(
        total=models.Sum('cout')
    )['total'] or 0

    sessions_by_type = sessions_qs.values('type_seance').annotate(
        count=models.Count('id'),
        total_duration=models.Sum('duree')
    ).order_by('-count')

    recent_sessions = sessions_qs.order_by('-date')[:5]

    sessions_by_horse = sessions_qs.values('cheval__nom').annotate(
        count=models.Count('id'),
        total_duration=models.Sum('duree')
    ).order_by('-total_duration')

    month_range, sessions_by_month = _monthly_distribution(
        sessions_qs, start_date, end_date,
    )
    month_names = [MONTH_NAMES[m - 1] for m in month_range]

    month_counts = [0] * len(month_range)
    for item in sessions_by_month:
        month_index = item['month'] - month_range[0]
        if 0 <= month_index < len(month_range):
            month_counts[month_index] = item['count']

    avg_duration = round(total_duration / total_sessions, 1) if total_sessions > 0 else 0
    avg_cost = round(total_cost / total_sessions, 2) if total_sessions > 0 else 0
    sessions_per_horse = round(total_sessions / total_horses, 1) if total_horses > 0 else 0

    sessions_dates = [
        {
            "id": session.pk,
            "date": session.date.isoformat(),
            "activity": session.type_seance
        }
        for session in sessions_qs
    ]

    return {
        'total_sessions': total_sessions,
        'total_horses': total_horses,
        'total_duration': total_duration,
        'total_cost': total_cost,
        'sessions_by_type': sessions_by_type,
        'recent_sessions': recent_sessions,
        'sessions_by_horse': sessions_by_horse,
        'month_names': month_names,
        'month_counts': month_counts,
        'avg_duration': avg_duration,
        'avg_cost': avg_cost,
        'sessions_per_horse': sessions_per_horse,
        'sessions_dates': sessions_dates,
    }


def _monthly_distribution(sessions_qs, start_date, end_date):
    """
    Retourne la plage de mois affichée et les comptes par mois.

    Avec un filtre de date : la plage couvre les mois présents dans les
    données filtrées (1 à 12 si aucune donnée). Sans filtre : les 12 mois
    de l'année en cours.
    """
    if start_date or end_date:
        sessions_by_month = sessions_qs.annotate(
            month=ExtractMonth('date')
        ).values('month').annotate(
            count=models.Count('id')
        ).order_by('month')

        all_months_in_data = [item['month'] for item in sessions_by_month]
        if all_months_in_data:
            min_month = min(all_months_in_data)
            max_month = max(all_months_in_data)
            month_range = list(range(min_month, max_month + 1))
        else:
            month_range = list(range(1, 13))
        return month_range, sessions_by_month

    current_year = datetime.now().year
    sessions_by_month = sessions_qs.filter(date__year=current_year).annotate(
        month=ExtractMonth('date')
    ).values('month').annotate(
        count=models.Count('id')
    ).order_by('month')
    return list(range(1, 13)), sessions_by_month
