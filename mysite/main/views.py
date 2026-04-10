from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _

from .forms import RegisterForm, ProfileEditForm
from .models import Profile

def index(request):
    return render(request, 'main/index.html')


def contact_view(request):
    return render(request, 'main/contact.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, _("Neteisingi prisijungimo duomenys"))

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
            messages.success(request, _("Registracija sėkminga"))
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'main/registration/register.html', {'form': form})


@login_required
def profile_view(request):
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Superuser should have admin role
    if request.user.is_superuser and profile.role != 'admin':
        profile.role = 'admin'
        profile.save()

    return render(request, 'main/accounts/profile.html', {'profile': profile})


@login_required
def profile_edit_view(request):
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profilis atnaujintas"))
            return redirect('profile')

    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    return render(request, 'main/accounts/profile_edit.html', {'form': form, 'profile': profile})
