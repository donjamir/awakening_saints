from django.contrib.auth.models import (AbstractBaseUser,BaseUserManager,PermissionsMixin)
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.mail import send_mail


class CustomAccountManager(BaseUserManager):
    ## Create a superuser ##
    def create_superuser(self, email, first_name, last_name, password, **other_fields): 
        
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, first_name, last_name, password, **other_fields) 

    ## create a new user ##
    def create_user(self, email, first_name, last_name, password, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, 
                          last_name=last_name, **other_fields)
        user.set_password(password)
        user.save()
        return user

class UserBase(AbstractBaseUser, PermissionsMixin):

################################ Custom Fields  #######################################
    email = models.EmailField(_('email address'), unique = True)
    last_name = models.CharField(max_length = 150, unique=True)
    first_name = models.CharField(max_length = 150, blank=True)
    
    # Delivery Details
    country = CountryField()
    phone_number = models.CharField(max_length=15, blank=True)
    postCode = models.CharField(max_length=12, blank=True)
    address_line_1 = models.CharField(max_length=150, blank=True)
    address_line_2 = models.CharField(max_length=150, blank=True)
    town_city = models.CharField(max_length=150, blank=True)

    # user_status
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

################################ Custom Fields  #######################################
    objects = CustomAccountManager()

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['first_name', 'last_name'] 

    class Meta:
        verbose_name = "Authapps"  
        verbose_name_plural = "Authapps"

    # send an email to the user
    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
        
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def __str__(self):
        return self.get_full_name() or self.email

    
    
