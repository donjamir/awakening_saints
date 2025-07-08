from django import forms
from .models import *
from django.contrib.auth.forms import (AuthenticationForm)


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        help_text='Required',
        error_messages={'required': 'Please enter a valid email address'},
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )

class RegistartionForm(forms.ModelForm):
    first_name = forms.CharField(label='First name', min_length=2, max_length=50, help_text='Required')
    last_name = forms.CharField(label='last name', min_length=2, max_length=50, help_text='Required')
    email = forms.EmailField(max_length=100, help_text='Required', error_messages={'required':'Please enter a valid email address'})
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
  
    class Meta:
      model = UserBase
      fields = ('first_name','last_name', 'email',)

    
    # form validations
    def clean_names(self):
       first_name = self.cleaned_data['first_name'].title()
       last_name = self.cleaned_data['last_name'].title()
       re = UserBase.objects.filter(first_name=first_name, last_name=last_name)
       if re.count():
          raise forms.ValidationError("Name already exits")
       return f'{first_name} {last_name}'
    
    def clean_password2(self):
       cd = self.cleaned_data
       if cd['password'] != cd['password2']:
          raise forms.ValidationError('Passwords do not match.')
       return cd['password2']
    
    def clean_email(self):
       email = self.cleaned_data['email']
       if UserBase.objects.filter(email=email).exists():
          raise forms.ValidationError(
             'Email address already taken')
       return email
    
    # form stylings
    def __init__(self,*args, **kwargs):
      super().__init__(*args, **kwargs)
      self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First name'})
      self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last name'})
      self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email address'})
      self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
      self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})



























