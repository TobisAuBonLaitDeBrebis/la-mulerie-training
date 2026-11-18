from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .models import Horse, TrainingSession
from .forms import HorseForm, TrainingSessionForm
from .services import build_dashboard_data
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
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    data = build_dashboard_data(
        request.user,
        start_date=start_date_str,
        end_date=end_date_str,
    )

    # Le calendrier web consomme le JSON directement dans le template
    data['sessions_dates'] = json.dumps(data['sessions_dates'])

    # Passer les dates sélectionnées au template pour les afficher dans le datepicker
    data['start_date'] = start_date_str
    data['end_date'] = end_date_str

    return render(request, "training/dashboard.html", data)


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
    if request.method != 'POST':
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])
    horse = get_object_or_404(Horse, pk=pk, proprietaire=request.user)
    horse.delete()
    return redirect('home_horses')

@login_required
def training_delete(request, pk):
    if request.method != 'POST':
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])
    training = get_object_or_404(TrainingSession, pk=pk, cavalier=request.user)
    training.delete()
    return redirect('home_training')

@login_required
def training_detail(request, pk):
    training = get_object_or_404(TrainingSession, pk=pk, cavalier=request.user)
    return render(request, 'training/training_detail.html', {'training': training})