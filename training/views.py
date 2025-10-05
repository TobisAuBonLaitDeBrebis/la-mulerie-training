from django.shortcuts import render, redirect, get_object_or_404
from .models import Horse, TrainingSession
from .forms import HorseForm, TrainingSessionForm
from django.contrib.auth.decorators import login_required




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
def home_training(request):
    sessions = TrainingSession.objects.filter(cavalier=request.user).order_by('date')
    return render(request, "training/home_training.html", {"sessions": sessions})

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
        initial = {'cheval': horse} if horse else None
        form = TrainingSessionForm(initial=initial)

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