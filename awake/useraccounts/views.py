from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import *
from .token import *
from django.contrib import messages
from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .models import *

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import *
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.urls import reverse_lazy

from ecomapp.models import *









# Create this form if it doesn't exist yet

def account_login(request):
    if request.user.is_authenticated:
        return redirect('sales:books')  # already logged in

    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('sales:books')
                else:
                    messages.error(request, 'Account not activated. Please check your email.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        login_form = UserLoginForm()
        
    return render(request, 'users/useraccounts/registration/login.html', {'form': login_form})


# def account_login(request):
#     if request.user.is_authenticated:
#         # print("Already logged in:", request.user)
#         return redirect('sales:books')

#     if request.method == 'POST':
#         print("POST DATA:", request.POST)
#         login_form = UserLoginForm(request.POST)
#         if login_form.is_valid():
#             # print("Form is valid")
#             email = login_form.cleaned_data['email']
#             password = login_form.cleaned_data['password']
#             user = authenticate(request, email=email, password=password)
#             # print("Authenticated user:", user)
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     print("User logged in successfully")
#                     return redirect('sales:books')
#                 else:
#                     print("User not active")
#                     messages.error(request, 'Account not activated.')
#             else:
#                 print("Invalid credentials")
#                 messages.error(request, 'Invalid email or password.')
#         else:
#             print("Form invalid:", login_form.errors)
#     else:
#         login_form = UserLoginForm()

#     return render(request, 'users/useraccounts/registration/login.html', {'form': login_form})



@login_required
def dashboard(request):
    
    user_email = request.user.email
    orders = BookOrder.objects.filter(email=user_email).order_by('-created')
    
    stats = {
        'pending': orders.filter(status='pending').count(),
        'ready': orders.filter(status='ready').count(),
        'collected': orders.filter(status='collected').count(),
        'cancelled': orders.filter(status='cancelled').count(),
    }
    
    context = {
        'orders': orders,
        'stats':stats
    }
    return render(request, 'users/useraccounts/users/dashboard.html', context)



def account_reg(request):
    if request.user.is_authenticated:
        return redirect('sales:books')
    
    if request.method == 'POST':
        registerForm = RegistartionForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password'])
            user.is_active = False  # Account is inactive until email verification
            user.save()

            # Generate activation link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = f"{request.scheme}://{request.get_host()}/accounts/activate/{uid}/{token}/"

            # Render template that triggers EmailJS from frontend
            return render(request, 'users/useraccounts/registration/send_email.html', {
                'user': user,
                'activation_link': activation_link
            })
    else:
        registerForm = RegistartionForm()
    
    return render(request, 'users/useraccounts/registration/register.html', {'form': registerForm})



def account_activate(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = UserBase.objects.get(pk=uid)
    except():
        pass
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('accounts:dashboard')
    else:
        return render(request, 'users/useraccounts/registration/account_activation_invalid.html')

def logout_view(request):
    logout(request)
    return redirect('sales:books')

def login_p(request):
    return render(request, 'users/useraccounts/registration/login.html')