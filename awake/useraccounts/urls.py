from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import (UserLoginForm)
from .  import views

app_name = 'accounts'


urlpatterns = [
    path('login/', views.account_login, name ='login'),
    path("logout/", views.logout_view, name="logout"),


    path('registration/', views.account_reg, name='registration'),
    path('activate/<slug:uidb64>/<slug:token>/', views.account_activate, name='activate'),
    path('dashboard/', views.dashboard, name='dashboard')
]