from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,DisponibilidadDoctor, Appointment

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
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'start_time']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'datepicker'}),
            'start_time': forms.TimeInput(attrs={'class': 'timepicker'}),
        }
