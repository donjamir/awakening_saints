from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import *
from .token import *
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













#login view
class LoginView(View):
    template_name = 'users/useraccounts/registration/login.html'
    success_url = reverse_lazy('dashboard')  # Change to where you want to redirect after login

    def get(self, request):
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


@login_required
def dashboard(request):
    return render(request, 'users/useraccounts/users/dashboard.html')

def account_reg(request):
    if request.user.is_authenticated:
        return redirect('sales:home')
    
    if request.method == 'POST':
        registerForm = RegistartionForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password'])
            user.is_active = False # this is going to be included in the email activation
            user.save()

            #setup email
            current_site = get_current_site(request)
            subject = 'Activate your account'
            message = render_to_string('users/useraccounts/registration/account_activation_email.html', {
                'user':user,
                'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return HttpResponse('You have been registered successfully and activation was sent to your email.')
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
    return redirect('sales:homeone')

def login_p(request):
    return render(request, 'users/useraccounts/registration/login.html')