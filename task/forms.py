import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,DisponibilidadDoctor,Cita
from django.contrib.auth.forms import PasswordChangeForm


#REGISTRO USUARIO
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
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z]+$', first_name):
            raise forms.ValidationError("El nombre solo puede contener letras.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-Z]+$', last_name):
            raise forms.ValidationError("El apellido solo puede contener letras.")
        return last_name

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not re.match(r'^\d{11}$', telefono):
            raise forms.ValidationError("El número de teléfono debe contener exactamente 11 dígitos numéricos.")
        return telefono

#DISPONIBILIDAD DOCTOR
class DisponibilidadDoctorForm(forms.ModelForm):
    class Meta:
        model = DisponibilidadDoctor
        fields = ['fecha', 'hora_inicio', 'hora_fin']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha"].widget = forms.DateInput(format="%Y-%m-%d")
        self.fields["hora_inicio"].widget = forms.TimeInput(format="%H:%M")
        self.fields["hora_fin"].widget = forms.TimeInput(format="%H:%M")

#CITA
class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['informe', 'recipe', 'indicaciones']

#BDD
class UploadFileForm(forms.Form):
    file = forms.FileField()