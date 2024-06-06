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
            max_length = 20

            if len(username) > max_length:
                raise forms.ValidationError(f"El usuario solo puede contener un máximo de {max_length} caracteres.")


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
        max_length = 20

        if len(first_name) > max_length:
            raise forms.ValidationError(f"El nombre solo puede contener un máximo de {max_length} caracteres.")

        if not re.match(r'^[A-Za-zñÑ\s\-]+$', first_name):
            raise forms.ValidationError("El nombre solo puede contener letras y -")
        return first_name


    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        max_length = 20
        if len(last_name) > max_length:
            raise forms.ValidationError(f"El nombre solo puede contener un máximo de {max_length} caracteres.")

        if not re.match(r'^[A-Za-zñÑ\s\-]+$', last_name):
            raise forms.ValidationError("El apellido solo puede contener letras y -")
        return last_name

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not re.match(r'^\d{11}$', telefono):
            raise forms.ValidationError("El número de teléfono debe contener exactamente 11 dígitos numéricos.")
        return telefono

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')

        # Patrón de expresión regular para validar la dirección (incluyendo la ñ)
        patron_regex = r'^[A-Za-zñÑ0-9 -]+$'

        # Validación con la expresión regular
        if not re.match(patron_regex, direccion):
            raise forms.ValidationError("La dirección solo puede contener letras, números, guiones, espacios y la letra ñ.")

        return direccion

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