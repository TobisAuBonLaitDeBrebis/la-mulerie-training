from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm ,UserChangeForm
from django.contrib.auth.decorators import login_required

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'training\home.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Assure-toi d'avoir une url nommée 'profile'
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})