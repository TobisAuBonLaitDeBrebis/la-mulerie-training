from django.shortcuts import render, redirect, get_object_or_404
from .models import Horse, TrainingSession
from .forms import HorseForm, TrainingSessionForm
from django.contrib.auth.decorators import login_required





@login_required
def horse_detail(request, pk):
    horse = get_object_or_404(Horse, pk=pk)
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
            return redirect('home')
    else:
        form = HorseForm()
    return render(request, 'training/horse_form.html', {'form': form})


@login_required
def home(request):
    horses = Horse.objects.filter(proprietaire=request.user)
    sessions = TrainingSession.objects.filter(cavalier=request.user).order_by('date')
    return render(request, "training/home.html", {"sessions": sessions , "horses": horses})

@login_required
def training_add(request, horse_pk=None):
    horse = None
    user_horses = Horse.objects.filter(proprietaire=request.user)
    if horse_pk:
        horse = get_object_or_404(Horse, pk=horse_pk, proprietaire=request.user)

    if request.method == 'POST':
        form = TrainingSessionForm(request.POST)
        # Filtre le champ cheval si pas de horse_pk
        if not horse:
            form.fields['cheval'].queryset = user_horses
        if form.is_valid():
            training = form.save(commit=False)
            if horse:
                training.cheval = horse
            else:
                training.cheval = form.cleaned_data['cheval']
            training.cavalier = request.user
            training.save()
            return redirect('home')
    else:
        form = TrainingSessionForm()
        if not horse:
            form.fields['cheval'].queryset = user_horses
    return render(request, 'training/training_form.html', {'form': form, 'horse': horse})

@login_required
def horse_delete(request, pk):
    horse = get_object_or_404(Horse, pk=pk, proprietaire=request.user)
    horse.delete()
    return redirect('home')

@login_required
def training_delete(request, pk):
    training = get_object_or_404(TrainingSession, pk=pk, cavalier=request.user)
    training.delete()
    return redirect('home')