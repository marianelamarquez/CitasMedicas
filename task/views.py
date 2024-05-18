import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout, login, authenticate
from .forms import UserRegistrationForm, DisponibilidadDoctorForm ,AppointmentForm
from django.contrib.auth.models import Group
from .models import CustomUser, Appointment, DisponibilidadDoctor
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseBadRequest, HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages

#Para saber que tipo de usuario es y enviar a las vistas
def get_user_context(request):
    context = {
        'is_doctor': False,
        'is_patient': False,
        'is_admin': False,
    }

    if request.user.groups.filter(name='doctor').exists():
        context['is_doctor'] = True
    elif request.user.groups.filter(name='patient').exists():
        context['is_patient'] = True
    elif request.user.groups.filter(name='admin').exists():
        context['is_admin'] = True

    return context


class Inicio(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_doctor = False
        is_patient = False
        is_admin= False

        if self.request.user.groups.filter(name='doctor').exists():
            is_doctor = True
        elif self.request.user.groups.filter(name='patient').exists():
            is_patient = True
        elif self.request.user.groups.filter(name='admin').exists():
            is_patient = True

        context['is_admin'] = is_admin
        context['is_doctor'] = is_doctor
        context['is_patient'] = is_patient

        return context

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
        context.update(get_user_context(self.request)) 
        return context
    
#-----ELIMINAR PACIENTE----
class EliminarPaciente(DeleteView):
    model = CustomUser
    template_name = 'paciente/EliminarPaciente.html'  
    success_url = reverse_lazy('ListarPaciente')   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
#-----Perfil Paciente---
def perfilPaciente(request, username):
    user = get_object_or_404(CustomUser, username=username)
    context = get_user_context(request)
    context['user'] = user

    return render(request, 'perfil/perfilPaciente.html', context)



# ---------------------------DOCTORES ---------------------------

#------Registar Doctores---
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
        context.update(get_user_context(self.request)) 
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
#-----ELIMINAR DOCTOR ----
class EliminarDoctor(DeleteView):
    model = CustomUser
    template_name = 'doctor/EliminarDoctor.html'  
    success_url = reverse_lazy('ListarDoctor')   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
#----Perfil Doctor---
def perfilDoctor(request, username):
    user = get_object_or_404(CustomUser, username=username)
    context = get_user_context(request)
    context['user'] = user
    return render(request, 'perfil/perfilDoctor.html', context)


# ---------------------------CALENDARIO ---------------------------

#------DISPONIBILIDAD DEL DOCTOR---

def crear_disponibilidad(request):
    if request.method == "GET":
        # Verificar si el usuario pertenece al grupo 'doctor'
        if not request.user.groups.filter(name="doctor").exists():
            messages.error(request, "No tienes permisos para crear disponibilidad.")
            return redirect("home")

        context = get_user_context(request) 
        return render(request, "doctor/calendario/crear-disponibilidad.html", context)

    elif request.method == "POST":
        fecha = request.POST.get("fecha")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")

        if not fecha or not hora_inicio or not hora_fin:
            messages.error(request, "Debes ingresar todos los campos obligatorios.")
            context = get_user_context(request)  
            return render(request, "doctor/calendario/crear-disponibilidad.html", context)

        try:
            # Convertir strings a objetos Date y Time
            fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
            hora_inicio_obj = datetime.datetime.strptime(hora_inicio, "%H:%M").time()
            hora_fin_obj = datetime.datetime.strptime(hora_fin, "%H:%M").time()
        except ValueError:
            messages.error(request, "Formato de fecha u hora no válido.")
            context = get_user_context(request)
            return render(request, "doctor/calendario/crear-disponibilidad.html", context)

        if hora_inicio_obj >= hora_fin_obj:
            messages.error(request, "La hora de inicio debe ser antes de la hora de fin.")
            context = get_user_context(request) 
            return render(request, "doctor/calendario/crear-disponibilidad.html", context)

        # Validación para evitar duplicados:
        disponibilidades_existentes = DisponibilidadDoctor.objects.filter(
            doctor=request.user, fecha=fecha_obj, hora_inicio=hora_inicio_obj
        )

        if disponibilidades_existentes:
            messages.error(request, "Ya existe una disponibilidad para esta fecha y hora.")
            context = get_user_context(request)
            return render(request, "doctor/calendario/crear-disponibilidad.html", context)

        disponibilidad = DisponibilidadDoctor(
            doctor=request.user, fecha=fecha_obj, hora_inicio=hora_inicio_obj, hora_fin=hora_fin_obj
        )
        disponibilidad.save()

        messages.success(request, "Disponibilidad creada exitosamente.")
        return redirect('ver_disponibilidad')

    else:
        return HttpResponseBadRequest("Método no permitido.")  

def ver_disponibilidad(request):
    if not request.user.groups.filter(name="doctor").exists():
        messages.error(request, "No tienes permisos para ver tu disponibilidad.")
        return redirect("home")

    disponibilidades = DisponibilidadDoctor.objects.filter(doctor=request.user)
    context = get_user_context(request) 
    context["disponibilidades"] = disponibilidades

    return render(request, "doctor/calendario/ver_disponibilidad.html", context)

def eliminar_disponibilidad(request, pk):
    if not request.user.groups.filter(name="doctor").exists():
        messages.error(request, "No tienes permisos para eliminar disponibilidad.")
        return redirect("home")

    disponibilidad = get_object_or_404(DisponibilidadDoctor, pk=pk, doctor=request.user)

    if request.method == "GET":
        context = get_user_context(request)  # Obtén el contexto adicional
        context["disponibilidades"] = disponibilidad
        return render(request, "doctor/calendario/eliminar_disponibilidad.html", context)

    elif request.method == "POST":
        if request.POST.get("confirmar") == "eliminar":
            disponibilidad.delete()
            messages.success(request, "Disponibilidad eliminada exitosamente.")
            return redirect("ver_disponibilidad")
        else:
            messages.error(request, "La operación no se ha completado.")
            return redirect("ver_disponibilidad")

    else:
        return HttpResponseBadRequest("Método no permitido.")
    
def modificar_disponibilidad(request, pk):
    if not request.user.groups.filter(name="doctor").exists():
        messages.error(request, "No tienes permisos para modificar disponibilidad.")
        return redirect("home")

    disponibilidad = get_object_or_404(DisponibilidadDoctor, pk=pk, doctor=request.user)

    if request.method == "GET":
        context = get_user_context(request)  # Obtén el contexto adicional
        context["disponibilidades"] = disponibilidad
        return render(request, "doctor/calendario/modificar_disponibilidad.html", context)

    elif request.method == "POST":
        nueva_fecha = request.POST.get("fecha")
        nueva_hora_inicio = request.POST.get("hora_inicio")
        nueva_hora_fin = request.POST.get("hora_fin")

        if not nueva_fecha or not nueva_hora_inicio or not nueva_hora_fin:
            messages.error(request, "Debes ingresar todos los campos obligatorios.")
            context = get_user_context(request)
            return render(request, "doctor/calendario/modificar_disponibilidad.html", context)

        try:
            # Convertir strings a objetos Date y Time
            nueva_fecha_obj = datetime.datetime.strptime(nueva_fecha, "%Y-%m-%d").date()
            nueva_hora_inicio_obj = datetime.datetime.strptime(nueva_hora_inicio, "%H:%M").time()
            nueva_hora_fin_obj = datetime.datetime.strptime(nueva_hora_fin, "%H:%M").time()
        except ValueError:
            messages.error(request, "Formato de fecha u hora no válido.")
            context = get_user_context(request)
            return render(request, "doctor/calendario/modificar_disponibilidad.html", context)

        if nueva_hora_inicio_obj >= nueva_hora_fin_obj:
            messages.error(request, "La hora de inicio debe ser antes de la hora de fin.")
            context = get_user_context(request)
            return render(request, "doctor/calendario/modificar_disponibilidad.html", context)

        # Validación para evitar conflictos con otras citas existentes:
        disponibilidades_conflictivas = DisponibilidadDoctor.objects.filter(
            doctor=request.user,
            fecha=nueva_fecha_obj,
            hora_inicio__lte=nueva_hora_fin_obj,
            hora_fin__gte=nueva_hora_inicio_obj
        ).exclude(pk=disponibilidad.pk)

        if disponibilidades_conflictivas:
            messages.error(request, "La nueva disponibilidad se superpone con otras citas existentes.")
            return render(request, "doctor/calendario/modificar_disponibilidad.html", context={})

        disponibilidad.fecha = nueva_fecha_obj
        disponibilidad.hora_inicio = nueva_hora_inicio_obj
        disponibilidad.hora_fin = nueva_hora_fin_obj
        disponibilidad.save()

        messages.success(request, "Disponibilidad modificada exitosamente.")
        return redirect("ver_disponibilidad")

    else:
        return HttpResponseBadRequest("Método no permitido.")


#------CITAS -----

def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # Guardar la cita del paciente
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            messages.success(request, '¡La cita se ha creado correctamente!')
            return redirect('home')  # Redireccionar a una vista de éxito
        else:
            messages.error(request, '¡Hubo un error al crear la cita!')
    else:
        form = AppointmentForm()
    
    # Si la solicitud es POST pero el formulario no es válido, se renderiza la misma plantilla con el formulario que contiene los errores de validación
    return render(request, 'Citas/crear_cita.html', {'form': form})