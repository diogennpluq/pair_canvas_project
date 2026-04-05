from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileUpdateForm, CustomPasswordChangeForm
from .models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        # Обработка обновления профиля
        if 'email' in request.POST or 'avatar' in request.FILES:
            form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Профиль успешно обновлен!')
                return redirect('profile')
        # Обработка смены пароля
        elif 'old_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Чтобы не разлогинивало
                messages.success(request, 'Пароль успешно изменен!')
                return redirect('profile')
            else:
                messages.error(request, 'Ошибка при смене пароля. Проверьте данные.')
    else:
        form = ProfileUpdateForm(instance=request.user)

    password_form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/profile.html', {'form': form, 'password_form': password_form})