from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .models import Horse, TrainingSession
from .forms import HorseForm, TrainingSessionForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import json


# test commit
@login_required
def horse_detail(request, pk):
    horse = get_object_or_404(Horse, pk=pk ,proprietaire=request.user.pk)
    trainings = horse.trainings.all()
    return render(request, 'training/horse_detail.html', {'horse': horse, 'trainings': trainings})

@login_required
def horse_add(request):
    if request.method == 'POST':
        form = HorseForm(request.POST)
        if form.is_valid():
            horse = form.save(commit=False)
            horse.proprietaire = request.user
            horse.save()
            return redirect('home_horses')
    else:
        form = HorseForm()
    return render(request, 'training/horse_form.html', {'form': form})

@login_required
def horse_edit(request, pk):
    horse = get_object_or_404(Horse, pk=pk, proprietaire=request.user)
    if request.method == 'POST':
        form = HorseForm(request.POST, instance=horse)
        if form.is_valid():
            form.save()
            return redirect('horse_detail', pk=horse.pk)
    else:
        form = HorseForm(instance=horse)
    return render(request, 'training/horse_form.html', {'form': form, 'horse': horse})


@login_required
def dashboard(request):
    """Dashboard avec statistiques et analytiques"""
    from django.db.models.functions import ExtractMonth, ExtractYear
    from datetime import datetime
    
    # Récupérer les paramètres de filtre de date
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Par défaut : toutes les périodes (pas de filtre de date)
    # Si on veut afficher toutes les données, on ne passe pas de date_filter
    date_filter = {}
    if start_date_str:
        date_filter['date__gte'] = start_date_str
    if end_date_str:
        date_filter['date__lte'] = end_date_str
    
    # Définir le filtre de base (toutes les séances de l'utilisateur)
    base_filter = {'cavalier': request.user}
    
    # Appliquer le filtre de date
    date_filter = {}
    if start_date_str:
        date_filter['date__gte'] = start_date_str
    if end_date_str:
        date_filter['date__lte'] = end_date_str
    
    # Filtre complet pour les séances
    sessions_filter = {**base_filter, **date_filter}
    
    # Statistiques globales (filtrées)
    sessions_qs = TrainingSession.objects.filter(**sessions_filter)
    total_sessions = sessions_qs.count()
    total_horses = Horse.objects.filter(proprietaire=request.user).count()
    
    # Temps total d'entraînement (en minutes)
    total_duration = sessions_qs.aggregate(
        total=models.Sum('duree')
    )['total'] or 0
    
    # Coût total
    total_cost = sessions_qs.aggregate(
        total=models.Sum('cout')
    )['total'] or 0
    
    # Répartition par type de séance
    sessions_by_type = sessions_qs.values('type_seance').annotate(
        count=models.Count('id'),
        total_duration=models.Sum('duree')
    ).order_by('-count')
    
    # Dernières séances (5 dernières)
    recent_sessions = sessions_qs.order_by('-date')[:5]
    
    # Séances par cheval
    sessions_by_horse = sessions_qs.values('cheval__nom').annotate(
        count=models.Count('id'),
        total_duration=models.Sum('duree')
    ).order_by('-total_duration')
    
    # Séances par mois - utiliser l'année des données filtrées ou année en cours
    # Si des dates sont sélectionnées, on utilise les mois de ces dates
    # Sinon, on utilise l'année en cours
    if start_date_str or end_date_str:
        # Si on a un filtre de date, on extrait les mois des données filtrées
        sessions_by_month = sessions_qs.annotate(
            month=ExtractMonth('date')
        ).values('month').annotate(
            count=models.Count('id')
        ).order_by('month')
        
        # Déterminer la plage de mois à afficher
        all_months_in_data = [item['month'] for item in sessions_by_month]
        if all_months_in_data:
            min_month = min(all_months_in_data)
            max_month = max(all_months_in_data)
            # Créer la liste des mois à afficher (de min à max)
            month_range = list(range(min_month, max_month + 1))
        else:
            # Pas de données, on affiche tous les mois de l'année en cours
            month_range = list(range(1, 13))
            min_month = 1
            max_month = 12
    else:
        # Pas de filtre de date, on affiche l'année en cours
        current_year = datetime.now().year
        sessions_by_month = sessions_qs.filter(date__year=current_year).annotate(
            month=ExtractMonth('date')
        ).values('month').annotate(
            count=models.Count('id')
        ).order_by('month')
        month_range = list(range(1, 13))
    
    # Créer les noms de mois pour la plage sélectionnée
    month_names_full = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    month_names = [month_names_full[m-1] for m in month_range]
    
    # Préparer les counts pour chaque mois de la plage
    month_counts = [0] * len(month_range)
    for item in sessions_by_month:
        month_index = item['month'] - month_range[0]  # index relatif à la plage
        if 0 <= month_index < len(month_range):
            month_counts[month_index] = item['count']
    
    # Calculer les moyennes pour éviter d'utiliser le filtre 'div' dans le template
    avg_duration = round(total_duration / total_sessions, 1) if total_sessions > 0 else 0
    avg_cost = round(total_cost / total_sessions, 2) if total_sessions > 0 else 0
    sessions_per_horse = round(total_sessions / total_horses, 1) if total_horses > 0 else 0
    
    # Préparer sessions_dates pour le calendrier
    sessions_dates = [
        {
            "id": s.pk,
            "date": s.date.isoformat(),
            "activity": s.type_seance
        }
        for s in sessions_qs
    ]
    
    # Passer les dates sélectionnées au template pour les afficher dans le datepicker
    return render(request, "training/dashboard.html", {
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
        'start_date': start_date_str,
        'end_date': end_date_str,
        'sessions_dates': json.dumps(sessions_dates),
    })


@login_required
def home_training(request):
    sessions = TrainingSession.objects.filter(cavalier=request.user).order_by('-date')
    sessions_dates= [
        {
            "id": s.pk,
            "date": s.date.isoformat(),
            "activity": s.type_seance
        }
        for s in sessions
    ]

    return render(request, "training/home_training.html", {"sessions": sessions, "sessions_dates": json.dumps(sessions_dates)})

@login_required
def home_horses(request):
    horses = Horse.objects.filter(proprietaire=request.user)
    return render(request, "training/home_horses.html", {"horses": horses})



@login_required
def training_add(request, horse_pk=None):
    # On récupère TOUS les chevaux de l’utilisateur connecté
    user_horses = Horse.objects.filter(proprietaire=request.user)

    # Si un cheval est passé en paramètre → on vérifie qu’il appartient bien à l’utilisateur
    horse = None
    if horse_pk:
        horse = get_object_or_404(Horse, pk=horse_pk, proprietaire=request.user)

    if request.method == 'POST':
        form = TrainingSessionForm(request.POST)

        # On force le champ cheval à ne contenir que les chevaux du user
        form.fields['cheval'].queryset = user_horses

        if form.is_valid():
            training = form.save(commit=False)
            training.cavalier = request.user

            # Si un cheval précis est passé en URL, on l’impose
            if horse:
                training.cheval = horse

            training.save()
            return redirect('home_training')

    else:
        # Initialisation du formulaire : si un cheval est passé → pré-rempli
        initial = {'cheval': horse} if horse else {}
        
        # Prendre la date de l'URL si elle existe (ex: ?date=2025-12-25)
        date_from_url = request.GET.get('date')
        if date_from_url:
            initial['date'] = date_from_url
        
        form = TrainingSessionForm(initial=initial if initial else None)

        # Et dans tous les cas → on limite le champ aux chevaux du user
        form.fields['cheval'].queryset = user_horses

    return render(request, 'training/training_form.html', {
        'form': form,
        'horse': horse
    })


@login_required
def training_edit(request, pk):
    training = get_object_or_404(TrainingSession, pk=pk, cavalier=request.user)
    user_horses = Horse.objects.filter(proprietaire=request.user)

    if request.method == 'POST':
        form = TrainingSessionForm(request.POST, instance=training)
        form.fields['cheval'].queryset = user_horses
        if form.is_valid():
            training = form.save(commit=False)
            training.cavalier = request.user
            training.save()
            return redirect('home_training')
    else:
        form = TrainingSessionForm(instance=training)
        form.fields['cheval'].queryset = user_horses

    return render(request, 'training/training_form.html', {'form': form, 'training': training})

@login_required
def horse_delete(request, pk):
    horse = get_object_or_404(Horse, pk=pk, proprietaire=request.user)
    horse.delete()
    return redirect('home_horses')

@login_required
def training_delete(request, pk):
    training = get_object_or_404(TrainingSession, pk=pk, cavalier=request.user)
    training.delete()
    return redirect('home_training')

@login_required
def training_detail(request, pk):
    training = get_object_or_404(TrainingSession, pk=pk, cavalier=request.user)
    return render(request, 'training/training_detail.html', {'training': training})