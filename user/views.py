# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm
from .models import User
from django.contrib import messages

# ===== Registro de usuário =====
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
        else:
            # Mostra os erros do form usando messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'user/register.html', {'form': form})

# ===== Login =====
def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('menu')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'user/login.html', {'form': form})

# ===== Logout =====
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

# ===== Listar usuários =====
@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'user/user_list.html', {'users': users})

# ===== Editar usuário =====
@login_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'user/user_edit.html', {'form': form})

def profile(request):
    return render(request, 'user/profile.html')

# ===== Deletar usuário =====
@login_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'user/user_delete.html', {'user': user})
