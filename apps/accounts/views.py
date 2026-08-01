from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to IntelliHub AI, {user.username}! Your account was created successfully.")
            return redirect('dashboard:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_banned:
                messages.error(request, "Your account has been suspended by an Administrator.")
                return redirect('accounts:login')
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
    else:
        form = UserLoginForm(request=request)
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')

@login_required
def profile_view(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
    else:
        p_form = ProfileUpdateForm(instance=user_profile)
        
    context = {
        'p_form': p_form,
        'dataset_count': request.user.datasets.count() if hasattr(request.user, 'datasets') else 0,
        'model_count': request.user.ml_models.count() if hasattr(request.user, 'ml_models') else 0,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
