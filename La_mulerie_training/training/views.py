from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Horse, TrainingSession
from .forms import HorseForm, TrainingSessionForm

def horse_list(request):
    horses = Horse.objects.all()
    return render(request, 'training/horse_list.html', {'horses': horses})

def horse_detail(request, pk):
    horse = get_object_or_404(Horse, pk=pk)
    trainings = horse.trainings.all()
    return render(request, 'training/horse_detail.html', {'horse': horse, 'trainings': trainings})

def horse_add(request):
    if request.method == 'POST':
        form = HorseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('horse_list')
    else:
        form = HorseForm()
    return render(request, 'training/horse_form.html', {'form': form})

def training_add(request, horse_pk):
    horse = get_object_or_404(Horse, pk=horse_pk)
    if request.method == 'POST':
        form = TrainingSessionForm(request.POST)
        if form.is_valid():
            training = form.save(commit=False)
            training.cheval = horse
            training.save()
            return redirect('horse_detail', pk=horse.pk)
    else:
        form = TrainingSessionForm()
    return render(request, 'training/training_form.html', {'form': form, 'horse': horse})