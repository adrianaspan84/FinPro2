from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm, ProfileEditForm

def index(request):
    return render(request, 'main/index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Neteisingi prisijungimo duomenys")

    return render(request, 'main/registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registracija sėkminga")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'main/registration/register.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'main/accounts/profile.html')


@login_required
def profile_edit_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilis atnaujintas")
            return redirect('profile')

    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'main/accounts/profile_edit.html', {'form': form})
