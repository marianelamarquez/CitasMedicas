import datetime
from django.utils import timezone
import json
import os
import shutil
from django.shortcuts import get_object_or_404, render, redirect  
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.contrib.auth import logout, login, authenticate,update_session_auth_hash
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from .forms import UserRegistrationForm,CitaForm, UploadFileForm
from django.contrib.auth.models import Group
from .models import CustomUser, Cita, DisponibilidadDoctor
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView,PasswordChangeDoneView
from xhtml2pdf import pisa




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
            is_admin = True

        context['is_admin'] = is_admin
        context['is_doctor'] = is_doctor
        context['is_patient'] = is_patient
      
        return context

def salir(request):
    logout(request)
    return redirect('home')

#CAMBIAR CONTRASENAS 
class ProfilePasswordChangeView(PasswordChangeView):
    template_name = 'perfil/change_password.html'
    success_url = reverse_lazy('change_password') 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = get_user_context(self.request) 
        context.update(user_context)
        context['password_changed'] = self.request.session.get('password_changed', False)
        return context

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        self.request.session['password_changed'] = True
        messages.success(self.request, 'Cambio de contraseña exitoso')
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, 'No se pudo cambiar la contraseña')
        return self.render_to_response(self.get_context_data(form=form))
    



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
            print(errors)
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
    paginate_by = 10  # Muestra 10 pacientes por página

    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()
    def get_queryset(self):
        return  CustomUser.objects.filter(groups__name='patient')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuarios_list = self.get_queryset()
        paginator = Paginator(usuarios_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context[self.context_object_name] = page_obj
        return context
#-----EDITAR PACIENTE----
#admin
class EditarPaciente(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'telefono', 'email','direccion']  
    template_name = 'paciente/EditarPaciente.html' 
    success_url = reverse_lazy('ListarPaciente')   
    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
   
class EditarPacientePerfil(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'telefono', 'email','direccion']  
    template_name = 'perfil/EditarPacientePerfil.html'
    def test_func(self):
        return self.request.user.groups.filter(name='patient').exists()
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
    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
#-----Perfil Paciente---
def perfilPaciente(request, username):
    if not request.user.groups.filter(name="patient").exists():
     return redirect("home")
    
    user = get_object_or_404(CustomUser, username=username)
    context = get_user_context(request)
    context['user'] = user

    return render(request, 'perfil/perfilPaciente.html', context)



# ---------------------------DOCTORES ---------------------------

#------Registar Doctores---
def create_doctor(request):
        if not request.user.groups.filter(name="admin").exists():
                return redirect("home") 
               
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
    context_object_name= 'usuario'
    paginate_by = 10  # Muestra 10 pacientes por página 

    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()

    def get_queryset(self):
        return  CustomUser.objects.filter(groups__name='doctor')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuarios_list = self.get_queryset()
        paginator = Paginator(usuarios_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context[self.context_object_name] = page_obj
        return context


#-----EDITAR DOCTOR----
class EditarDoctorPerfil(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'telefono', 'email','direccion','ncolegiom']  
    template_name = 'perfil/EditarDoctorPerfil.html'
    def test_func(self):
        return self.request.user.groups.filter(name='doctor').exists()
    def get_success_url(self):
        return reverse_lazy('perfilDoctor', kwargs={'username': self.request.user.username})  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        context.update(get_user_context(self.request)) 
        return context
   
#editar doc admin
class EditarDoctor(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'telefono', 'email','direccion','ncolegiom']  
    template_name = 'doctor/EditarDoctor.html' 
    success_url = reverse_lazy('ListarDoctor')   
    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    #-----ELIMINAR DOCTOR----
#-----ELIMINAR DOCTOR ----
class EliminarDoctor(DeleteView):
    model = CustomUser
    template_name = 'doctor/EliminarDoctor.html'  
    success_url = reverse_lazy('ListarDoctor')   
    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

#----Perfil Doctor---
def perfilDoctor(request, username):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home") 
    
    user = get_object_or_404(CustomUser, username=username)
    context = get_user_context(request)
    context['user'] = user
    return render(request, 'perfil/perfilDoctor.html', context)


# ---------------------------CALENDARIO ---------------------------

#---------------------DISPONIBILIDAD DEL DOCTOR------------------

def crear_disponibilidad(request):
    if request.method == "GET":
        # Verificar si el usuario pertenece al grupo 'doctor'
        if not request.user.groups.filter(name="doctor").exists():
            return redirect("home")

        # Obtener fechas con disponibilidad ya creada
        disponibilidades_existentes = DisponibilidadDoctor.objects.filter(doctor=request.user)
        fechas_existentes = [disp.fecha.strftime("%Y-%m-%d") for disp in disponibilidades_existentes]

        context = get_user_context(request)
        context["fechas_existentes"] = json.dumps(fechas_existentes)

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

        disponibilidades_existentes = DisponibilidadDoctor.objects.filter(
            doctor=request.user, fecha=fecha_obj)
        if disponibilidades_existentes:
            messages.error(request, "Ya existe una disponibilidad para esta fecha.")
            context = get_user_context(request)
            return render(request, "doctor/calendario/crear-disponibilidad.html", context)

        disponibilidad = DisponibilidadDoctor(
            doctor=request.user, fecha=fecha_obj, hora_inicio=hora_inicio_obj, hora_fin=hora_fin_obj)
        disponibilidad.save()

        messages.success(request, "Disponibilidad creada exitosamente.")
        return redirect('ver_disponibilidad')

    else:
        return HttpResponseBadRequest("Método no permitido.")

def ver_disponibilidad(request):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")
    
    hoy = timezone.now().date()
    disponibilidades_list = DisponibilidadDoctor.objects.filter(doctor=request.user, fecha__gte=hoy).order_by('-fecha')

    paginator = Paginator(disponibilidades_list, 10)  # Muestra 10 disponibilidades por página
    page_number = request.GET.get('page')
    disponibilidades = paginator.get_page(page_number)

    for disponibilidad in disponibilidades:
        # Calcular turnos disponibles
        hoy = datetime.date.today()
        hora_inicio = datetime.datetime.combine(hoy, disponibilidad.hora_inicio)
        hora_fin = datetime.datetime.combine(hoy, disponibilidad.hora_fin)

        diferencia_horas = hora_fin - hora_inicio
        cantidad_turnos = int(diferencia_horas.total_seconds() / 3600)  # Convertir a horas
        turnos_disponibles = []
        hora_inicio_turno = hora_inicio
        for i in range(cantidad_turnos):
            turno_str = hora_inicio_turno.strftime("%H:%M")
            turnos_disponibles.append(turno_str)
            hora_inicio_turno += datetime.timedelta(hours=1)

        disponibilidad.turnos_disponibles = turnos_disponibles
        disponibilidad.cantidad_turnos = cantidad_turnos

    context = get_user_context(request) 
    context["disponibilidades"] = disponibilidades

    return render(request, "doctor/calendario/ver_disponibilidad.html", context)

def eliminar_disponibilidad(request, pk):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")

    disponibilidad = get_object_or_404(DisponibilidadDoctor, pk=pk, doctor=request.user)

    if request.method == "GET":
        context = get_user_context(request)
        context["disponibilidad"] = disponibilidad
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
        return redirect("home")

    disponibilidad = get_object_or_404(DisponibilidadDoctor, pk=pk, doctor=request.user)

    if request.method == "GET":
        context = get_user_context(request)
        context["disponibilidad"] = disponibilidad
        return render(request, "doctor/calendario/modificar_disponibilidad.html", context)

    elif request.method == "POST":
        nueva_hora_inicio = request.POST.get("hora_inicio")
        nueva_hora_fin = request.POST.get("hora_fin")

        if not nueva_hora_inicio or not nueva_hora_fin:
            messages.error(request, "Debes ingresar todos los campos obligatorios.")
            context = get_user_context(request)
            context["disponibilidad"] = disponibilidad
            return render(request, "doctor/calendario/modificar_disponibilidad.html", context)

        try:
            nueva_hora_inicio_obj = datetime.datetime.strptime(nueva_hora_inicio, "%H:%M").time()
            nueva_hora_fin_obj = datetime.datetime.strptime(nueva_hora_fin, "%H:%M").time()
        except ValueError:
            messages.error(request, "Formato de hora no válido.")
            context = get_user_context(request)
            context["disponibilidad"] = disponibilidad
            return render(request, "doctor/calendario/modificar_disponibilidad.html", context)

        if nueva_hora_inicio_obj >= nueva_hora_fin_obj:
            messages.error(request, "La hora de inicio debe ser antes de la hora de fin.")
            context = get_user_context(request)
            context["disponibilidad"] = disponibilidad
            return render(request, "doctor/calendario/modificar_disponibilidad.html", context)

        disponibilidades_conflictivas = DisponibilidadDoctor.objects.filter(
            doctor=request.user,
            fecha=disponibilidad.fecha,
            hora_inicio__lte=nueva_hora_fin_obj,
            hora_fin__gte=nueva_hora_inicio_obj
        ).exclude(pk=disponibilidad.pk)

        if disponibilidades_conflictivas:
            messages.error(request, "La nueva disponibilidad se superpone con otras citas existentes.")
            context = get_user_context(request)
            context["disponibilidad"] = disponibilidad
            return render(request, "doctor/calendario/modificar_disponibilidad.html", context)

        disponibilidad.hora_inicio = nueva_hora_inicio_obj
        disponibilidad.hora_fin = nueva_hora_fin_obj
        disponibilidad.save()

        messages.success(request, "Disponibilidad modificada exitosamente.")
        return redirect("ver_disponibilidad")

    else:
        return HttpResponseBadRequest("Método no permitido.")

#----------------------------CITAS ----------------------------
#Vision de Paciente
def seleccionar_doctor(request):
    if not request.user.groups.filter(name="patient").exists():
        return redirect("home")

    doctores = CustomUser.objects.filter(groups__name='doctor')
    
    doctores_disponibles = []
    for doctor in doctores:
        citas_pendientes = Cita.objects.filter(paciente=request.user, doctor=doctor, atendida=False, falto=False)
        if not citas_pendientes.exists():
            doctores_disponibles.append(doctor)

    context = get_user_context(request)
    context["doctores"] = doctores_disponibles
    return render(request, "Citas/seleccionar_doctor.html", context)

def seleccionar_fecha(request, doctor_id):
    if not request.user.groups.filter(name="patient").exists():
        return redirect("home")

    doctor = get_object_or_404(CustomUser, id=doctor_id, groups__name='doctor')
    hoy = timezone.now().date()
    disponibilidades = DisponibilidadDoctor.objects.filter(doctor=doctor, fecha__gte=hoy)
   
   
    # Crear una lista de fechas disponibles en formato JSON
    fechas_disponibles = [disponibilidad.fecha.strftime("%Y-%m-%d") for disponibilidad in disponibilidades]

    context = get_user_context(request)
    context["disponibilidades"] = disponibilidades
    context["fechas_disponibles"] = json.dumps(fechas_disponibles)  # Convertir a JSON
    return render(request, "Citas/seleccionar_fecha.html", context)

def seleccionar_turno(request, disponibilidad_id):
    if not request.user.groups.filter(name="patient").exists():
        return redirect("home")

    disponibilidad = get_object_or_404(DisponibilidadDoctor, id=disponibilidad_id)
    turnos_reservados = Cita.objects.filter(disponibilidad=disponibilidad).values_list('hora_inicio', 'hora_fin')
    turnos_reservados = [(t[0].strftime("%H:%M:%S"), t[1].strftime("%H:%M:%S")) for t in turnos_reservados]

    turnos_disponibles = disponibilidad.obtener_turnos_disponibles()
    turnos_disponibles = [turno for turno in turnos_disponibles if (turno[0].strftime("%H:%M:%S"), turno[1].strftime("%H:%M:%S")) not in turnos_reservados]

    context = get_user_context(request)
    context["disponibilidad"] = disponibilidad
    context["turnos_disponibles"] = turnos_disponibles
    return render(request, "Citas/seleccionar_turno.html", context)

def agendar_cita(request, disponibilidad_id):
    if not request.user.groups.filter(name="patient").exists():
        return redirect("home")

    disponibilidad = get_object_or_404(DisponibilidadDoctor, id=disponibilidad_id)
    hoy = timezone.now().date()

    # Verifica que la fecha de la disponibilidad no haya pasado
    if disponibilidad.fecha < hoy:
        messages.error(request, "No puedes agendar una cita en una fecha pasada.")
        return redirect('seleccionar_doctor')

    turno = request.POST.get("turno")

    if turno:
        inicio, fin = turno.split('-')
        # Verificar si el turno ya está reservado
        if Cita.objects.filter(disponibilidad=disponibilidad, hora_inicio=inicio, hora_fin=fin).exists():
            messages.error(request, "Este turno ya ha sido reservado. Por favor, selecciona otro turno.")
            return redirect('seleccionar_turno', disponibilidad_id=disponibilidad.id)
        
        cita = Cita.objects.create(
            doctor=disponibilidad.doctor,
            paciente=request.user,
            fecha=disponibilidad.fecha,
            hora_inicio=inicio,
            hora_fin=fin,
            disponibilidad=disponibilidad
        )
        messages.success(request, "Cita agendada con éxito.")
        return redirect('detalle_cita', cita_id=cita.id)
    else:
        messages.error(request, "Debes seleccionar un turno válido.")
        return redirect('seleccionar_turno', disponibilidad_id=disponibilidad.id)

def detalle_cita(request, cita_id):
    if not request.user.groups.filter(name="patient").exists():
        return redirect("home")
    cita = get_object_or_404(Cita, id=cita_id)
    context = get_user_context(request)
    context["cita"] = cita
    return render(request, 'Citas/detalle_cita.html', context)

def mis_citas(request):
    if not request.user.groups.filter(name="patient").exists():
        return redirect("home")

    citas_pendientes = Cita.objects.filter(paciente=request.user, atendida=False, falto=False).order_by('fecha').select_related('doctor', 'disponibilidad')

    paginator = Paginator(citas_pendientes, 10)  # Muestra 10 disponibilidades por página
    page_number = request.GET.get('page')
    citas_pendientes = paginator.get_page(page_number)

    context = get_user_context(request)
    context["citas_pendientes"] = citas_pendientes
    return render(request, "Citas/mis_citas.html", context)

def eliminar_cita(request, cita_id):
    if not request.user.groups.filter(name="patient").exists():
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    
    if request.method == 'POST':
        cita.delete()
        messages.success(request, "Cita eliminada con éxito.")
        return redirect('mis_citas')
    
    context = get_user_context(request)
    context["cita"] = cita
    return render(request, 'Citas/eliminar_cita.html', context)

def citas_atendidas_paciente(request):
    if not request.user.groups.filter(name="patient").exists():
        return redirect("home")

    citas_atendidas = Cita.objects.filter(paciente=request.user, atendida=True)
    citas_perdidas = Cita.objects.filter(paciente=request.user, falto=True)
   
    citas = (citas_atendidas | citas_perdidas).order_by('-fecha')
    
    paginator = Paginator(citas, 10)  # Muestra 10 disponibilidades por página
    page_number = request.GET.get('page')
    citas = paginator.get_page(page_number)

    context = get_user_context(request)
    context["citas"] = citas
    return render(request, "Citas/consultas_paciente.html", context)

def detalle_cita_paciente(request, cita_id):
    if not request.user.groups.filter(name="patient").exists():
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    context = get_user_context(request)
    context["cita"] = cita
    return render(request, "Citas/detalle_cita_paciente.html", context)


#Vision de doctor

def citas_doctor(request):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")
    citas = Cita.objects.filter(doctor=request.user, atendida=False, falto=False).order_by('-fecha').select_related('paciente', 'disponibilidad')
    
    paginator = Paginator(citas, 10)  # Muestra 10 disponibilidades por página
    page_number = request.GET.get('page')
    citas = paginator.get_page(page_number)
    
    context = get_user_context(request)
    context["citas"] = citas
    return render(request, "Citas/citas_doctor.html", context)

def detalle_cita_doctor(request, cita_id):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, doctor=request.user)
    context = get_user_context(request)
    context["cita"] = cita
    context["informe"] = cita.informe
    context["recipe"] = cita.recipe
    context["indicaciones"] = cita.indicaciones

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            guardar_cambios(request, cita_id)
            return redirect('detalle_cita_doctor', cita_id=cita.id)

    return render(request, 'Citas/detalle_cita_doctor.html', context)

def guardar_cambios(request, cita_id):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, doctor=request.user)
    form = CitaForm(request.POST, instance=cita)

    if form.is_valid():
        form.save()
        messages.success(request, "Los cambios se han guardado correctamente.")
        return redirect('detalle_cita_doctor', cita_id=cita.id)

    messages.error(request, "Hubo un error al guardar los cambios.")
    return redirect('detalle_cita_doctor', cita_id=cita.id)

def atender_cita(request, cita_id):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, doctor=request.user)

    cita.atendida = True
    cita.save()

    messages.success(request, "Cita marcada como atendida con éxito.")
    return redirect('detalle_cita_doctor', cita_id=cita.id)

def eliminar_cita_doctor(request, cita_id):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, doctor=request.user)
    
    if request.method == 'POST':
        cita.delete()
        messages.success(request, "Cita eliminada con éxito.")
        return redirect('citas_doctor')
    
    context = get_user_context(request)
    context["cita"] = cita
    return render(request, 'Citas/eliminar_cita_doctor.html', context)

def perdio_cita(request, cita_id):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, doctor=request.user)

    cita.falto = True
    cita.save()

    messages.success(request, "Cita marcada perdida con éxito.")
    return redirect('detalle_cita_doctor', cita_id=cita.id)

#HISTORIA

def doctor_historial(request):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")

    citas_atendidas = Cita.objects.filter(doctor=request.user, atendida=True)
    citas_perdidas = Cita.objects.filter(doctor=request.user, falto=True)
    
    # Unir los queryset y ordenar por fecha
    citas = (citas_atendidas | citas_perdidas).order_by('-fecha')

    paginator = Paginator(citas, 10)  # Muestra 10 disponibilidades por página
    page_number = request.GET.get('page')
    citas = paginator.get_page(page_number)

    context = get_user_context(request)
    context["citas"] = citas
    return render(request, "Citas/doctor_historial.html", context)

def detalle_cita_doctor_historial(request, cita_id):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, doctor=request.user)
    context = get_user_context(request)
    context["cita"] = cita
    context["informe"] = cita.informe
    context["recipe"] = cita.recipe
    context["indicaciones"] = cita.indicaciones

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            guardar_cambios(request, cita_id)
            return redirect('detalle_cita_doctor_historial', cita_id=cita.id)

    return render(request, 'Citas/detalle_cita_doctor_historial.html', context)

def eliminar_cita_historial(request, cita_id):
    if not request.user.groups.filter(name="doctor").exists():
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, doctor=request.user)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, "Historial eliminado con éxito.")
        return redirect('doctor_historial')
    context = get_user_context(request)
    context["cita"] = cita
    return render(request, "Citas/eliminar_cita_historial.html", context)

#PDF PACIENTE
def generar_pdf_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    
    # Obtener el nombre del paciente
    nombre_paciente = cita.paciente.first_name + '_' + cita.paciente.last_name

    # Asegurarse de que el nombre no contiene espacios ni caracteres especiales
    nombre_paciente = nombre_paciente.replace(' ', '_').replace(',', '').replace(';', '').replace(':', '')

    html_string = render_to_string('Citas/pdf_cita.html', {'cita': cita})

    response = HttpResponse(content_type='application/pdf')
    view_inline = request.GET.get('view') == 'inline'
    if view_inline:
        response['Content-Disposition'] = f'inline; filename="cita_{nombre_paciente}_{cita_id}.pdf"'
    else:
        response['Content-Disposition'] = f'attachment; filename="cita_{nombre_paciente}_{cita_id}.pdf"'

    pisa_status = pisa.CreatePDF(html_string, dest=response)

    if pisa_status.err:
        return HttpResponse(f'Error al generar el PDF: {pisa_status.err}', status=500)

    return response

#PDF DOCTOR
def generar_pdf_cita_doctor(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, doctor=request.user)
    
    # Obtener el nombre del paciente
    nombre_paciente = cita.paciente.first_name + '_' + cita.paciente.last_name

    # Asegurarse de que el nombre no contiene espacios ni caracteres especiales
    nombre_paciente = nombre_paciente.replace(' ', '_').replace(',', '').replace(';', '').replace(':', '')

    html_string = render_to_string('Citas/pdf_cita_doctor.html', {'cita': cita})

    response = HttpResponse(content_type='application/pdf')
    view_inline = request.GET.get('view') == 'inline'
    if view_inline:
        response['Content-Disposition'] = f'inline; filename="cita_{nombre_paciente}_{cita_id}.pdf"'
    else:
        response['Content-Disposition'] = f'attachment; filename="cita_{nombre_paciente}_{cita_id}.pdf"'

    pisa_status = pisa.CreatePDF(html_string, dest=response)

    if pisa_status.err:
        return HttpResponse(f'Error al generar el PDF: {pisa_status.err}', status=500)

    return response


#RESPALDO Y RESTAURACION 

@staff_member_required
def admin_db_view(request):
    form = UploadFileForm()
    return render(request, 'adminBD.html', {'form': form})

@staff_member_required
def database_backup(request):
    db_path = settings.DATABASES['default']['NAME']
    backup_filename = f"backup_{timezone.now().strftime('%Y%m%d%H%M%S')}.sqlite3"
    backup_filepath = settings.MEDIA_ROOT / backup_filename

    # Asegurarse de que el directorio MEDIA_ROOT exista
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    try:
        shutil.copyfile(db_path, backup_filepath)
        with open(backup_filepath, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename={backup_filename}'
            return response
    except Exception as e:
        return HttpResponse(f"Error al generar el backup de la base de datos: {str(e)}", status=500)
    finally:
        if backup_filepath.exists():
            backup_filepath.unlink()

@staff_member_required
def database_restore(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            backup_file = request.FILES['file']
            db_path = settings.DATABASES['default']['NAME']
            temp_backup_path = settings.MEDIA_ROOT / 'temp_restore.sqlite3'

            try:
                with open(temp_backup_path, 'wb+') as destination:
                    for chunk in backup_file.chunks():
                        destination.write(chunk)
                shutil.copyfile(temp_backup_path, db_path)
                return HttpResponse("Base de datos restaurada exitosamente.")
            except Exception as e:
                return HttpResponse(f"Error al restaurar la base de datos: {str(e)}", status=500)
            finally:
                if temp_backup_path.exists():
                    temp_backup_path.unlink()
    else:
        form = UploadFileForm()
    return render(request, 'backup_restore.html', {'form': form})