from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm
from django.contrib.auth.models import Group
from .models import CustomUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
# Create your views here.


class Inicio(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_doctor = False
        is_patient = False
   
        if self.request.user.groups.filter(name='doctor').exists():
            is_doctor = True
        elif self.request.user.groups.filter(name='patient').exists():
            is_patient = True

        context['is_doctor'] = is_doctor
        context['is_patient'] = is_patient

        return context



def perfilPaciente(request, username):
    user = CustomUser.objects.get(username=username)
    group_name = None
    if request.user.groups.exists():
        group_name = request.user.groups.first().name
    
    return render(request, 'perfil/perfilPaciente.html', {'user': user})

def perfilDoctor(request, username):
    user = CustomUser.objects.get(username=username)
    return render(request, 'perfil/perfilDoctor.html', {'user': user})

def salir(request):
    logout(request)
    return redirect('home')

# --------------------------- PACIENTES ---------------------------
#------Registrar Pacientes----

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        grupo = Group.objects.get(name="patient")

        if user_form.is_valid():
            user = user_form.save()
            user.groups.add(grupo)
            user.save()

            user = authenticate(
            username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password1'])
            login(request, user)
            return redirect('home')
        else:
           
            errors = user_form.errors
            return render(request, 'registration/register.html', {'form': user_form, 'errors': errors})
   
    else:
        user_form = UserRegistrationForm()

    return render(request, 'registration/register.html', {
        'user_form': user_form,
    })

# -----Listar Pacientes ----
class ListaPacientes(ListView):
    model= CustomUser
    template_name='paciente/ListarPaciente.html'
    context_object_name= 'Usuario'

    def get_queryset(self):
        return  CustomUser.objects.filter(groups__name='patient')
    
#-----EDITAR PACIENTE----
class EditarPaciente(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'telefono', 'email','direccion']  
    template_name = 'paciente/EditarPaciente.html' 
    success_url = reverse_lazy('ListarPaciente')   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
class EditarPacientePerfil(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'telefono', 'email','direccion']  
    template_name = 'perfil/EditarPacientePerfil.html'
    def get_success_url(self):
        return reverse_lazy('perfilPaciente', kwargs={'username': self.request.user.username})  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context
    
    #-----ELIMINAR PACIENTE----
class EliminarPaciente(DeleteView):
    model = CustomUser
    template_name = 'paciente/EliminarPaciente.html'  
    success_url = reverse_lazy('ListarPaciente')   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



# ---------------------------DOCTORES ---------------------------

#------Registar Doctores---
@login_required
def create_doctor(request):
        if request.method == 'POST':
            user_form = UserRegistrationForm(request.POST)
            grupo = Group.objects.get(name="doctor")

            if user_form.is_valid():
                user = user_form.save()
                user.groups.add(grupo)
                user.save()

                user = authenticate(
                username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password1'])
                return redirect('ListarDoctor')
            else:
           
                errors = user_form.errors
            return render(request, 'doctor/RegistroDoctor.html', {'form': user_form, 'errors': errors})
   
        else:
            user_form = UserRegistrationForm()

        return render(request, 'doctor/RegistroDoctor.html', {
            'user_form': user_form,
        })

# -----Listar Doctores ----
class ListaDoctores(ListView):
    model= CustomUser
    template_name='doctor/ListarDoctor.html'
    context_object_name= 'Usuario'

    def get_queryset(self):
        return  CustomUser.objects.filter(groups__name='doctor')
    


#-----EDITAR DOCTOR----
class EditarDoctorPerfil(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'telefono', 'email','direccion','ncolegiom']  
    template_name = 'perfil/EditarDoctorPerfil.html'
    def get_success_url(self):
        return reverse_lazy('perfilDoctor', kwargs={'username': self.request.user.username})  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context

class EditarDoctor(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'telefono', 'email','direccion','ncolegiom']  
    template_name = 'doctor/EditarDoctor.html' 
    success_url = reverse_lazy('ListarDoctor')   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    #-----ELIMINAR DOCTOR----
class EliminarDoctor(DeleteView):
    model = CustomUser
    template_name = 'doctor/EliminarDoctor.html'  
    success_url = reverse_lazy('ListarDoctor')   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
