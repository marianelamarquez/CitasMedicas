from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser 


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model= CustomUser
        fields= ['username','first_name','last_name','email','password1','password2','telefono','direccion','ncolegiom']
    def clean_username(self):
            username = self.cleaned_data['username']
            if CustomUser.objects.filter(username=username).exists():
                raise forms.ValidationError("Este nombre de usuario ya está en uso. Por favor, elige otro.")
            return username

    def clean_email(self):
            email = self.cleaned_data['email']
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("Este correo electrónico ya está en uso. Por favor, utiliza otro.")
            return email
