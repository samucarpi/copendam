from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re


@csrf_protect
def auth_view(request):
    """
    Handle both login and register forms on the same page
    """
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if already logged in
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'login':
            return handle_login(request)
        elif form_type == 'register':
            return handle_register(request)
    
    return render(request, 'auth/auth.html')


def handle_login(request):
    """
    Handle user login
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    if not username or not password:
        messages.error(request, 'Username e password sono obbligatori.')
        return render(request, 'auth/auth.html')
    
    # Try to authenticate with username first
    user = authenticate(request, username=username, password=password)
    
    # If that fails, try to authenticate with email
    if user is None:
        try:
            user_obj = User.objects.get(email=username)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    
    if user is not None:
        if user.is_active:
            login(request, user)
            messages.success(request, f'Benvenuto, {user.username}!')
            return redirect('dashboard')  # Redirect to dashboard after successful login
        else:
            messages.error(request, 'Il tuo account è stato disattivato.')
    else:
        messages.error(request, 'Username/email o password non corretti.')
    
    return render(request, 'auth/auth.html')


def handle_register(request):
    """
    Handle user registration
    """
    username = request.POST.get('username')
    email = request.POST.get('email')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    
    register_errors = []
    
    # Validation
    if not all([username, email, password1, password2]):
        register_errors.append('Tutti i campi sono obbligatori.')
    
    if password1 != password2:
        register_errors.append('Le password non corrispondono.')
    
    if len(password1) < 8:
        register_errors.append('La password deve essere di almeno 8 caratteri.')
    
    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        register_errors.append('Inserisci un indirizzo email valido.')
    
    # Validate username (alphanumeric + underscore, 3-30 chars)
    if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
        register_errors.append('Username deve contenere solo lettere, numeri e underscore (3-30 caratteri).')
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        register_errors.append('Username già in uso.')
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        register_errors.append('Email già registrata.')
    
    if register_errors:
        return render(request, 'auth/auth.html', {
            'register_errors': register_errors,
            'form_data': {
                'username': username,
                'email': email
            }
        })
    
    # Create user
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        # Auto-login after registration
        login(request, user)
        messages.success(request, f'Registrazione completata! Benvenuto, {username}!')
        return redirect('dashboard')  # Redirect to dashboard after successful registration
        
    except Exception as e:
        register_errors.append('Errore durante la registrazione. Riprova.')
        return render(request, 'auth/auth.html', {
            'register_errors': register_errors
        })


def logout_view(request):
    """
    Handle user logout
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, f'Arrivederci, {username}!')

    return redirect('auth') 