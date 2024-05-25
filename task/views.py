import datetime
import json
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth import logout, login, authenticate,update_session_auth_hash
from .forms import UserRegistrationForm
from django.contrib.auth.models import Group
from .models import CustomUser, Cita, DisponibilidadDoctor
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView,PasswordChangeDoneView



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

#CAMBIAR CONTRASENAS 
class ProfilePasswordChangeView( PasswordChangeView):
    template_name = 'perfil/change_password.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = get_user_context(self.request)
        context.update(user_context)
        context['password_changed'] = self.request.session.get('password_changed', False)
        return context
    
    def form_valid(self, form) :
        messages.success(self.request,'Cambio de contraseña exitoso')
        update_session_auth_hash(self.request, form.user)
        self.request.session['password_changed']= True
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'No se pudo cambiar la contraseña')
        return render(self.request, self.template_name, {'form': form})
    

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    success_url = reverse_lazy('home') 
        



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

#---------------------DISPONIBILIDAD DEL DOCTOR------------------

def crear_disponibilidad(request):
    if request.method == "GET":
        # Verificar si el usuario pertenece al grupo 'doctor'
        if not request.user.groups.filter(name="doctor").exists():
            messages.error(request, "No tienes permisos para crear disponibilidad.")
            return redirect("home")

        # Obtener fechas con disponibilidad ya creada
        disponibilidades_existentes = DisponibilidadDoctor.objects.filter(doctor=request.user)
        fechas_existentes = [disp.fecha.strftime("%Y-%m-%d") for disp in disponibilidades_existentes]

        context = get_user_context(request)
        context["fechas_existentes"] = json.dumps(fechas_existentes)  # Convertir a JSON

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
            doctor=request.user, fecha=fecha_obj
        )

        if disponibilidades_existentes:
            messages.error(request, "Ya existe una disponibilidad para esta fecha.")
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

    disponibilidades_list = DisponibilidadDoctor.objects.filter(doctor=request.user).order_by('fecha')

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
        messages.error(request, "No tienes permisos para eliminar disponibilidad.")
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
        messages.error(request, "No tienes permisos para modificar disponibilidad.")
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
        messages.error(request, "Solo los pacientes pueden acceder a esta página.")
        return redirect("home")

    doctores = CustomUser.objects.filter(groups__name='doctor')
    context = get_user_context(request)
    context["doctores"] = doctores
    return render(request, "Citas/seleccionar_doctor.html", context)

def seleccionar_fecha(request, doctor_id):
    if not request.user.groups.filter(name="patient").exists():
        messages.error(request, "Solo los pacientes pueden acceder a esta página.")
        return redirect("home")

    doctor = get_object_or_404(CustomUser, id=doctor_id, groups__name='doctor')
    disponibilidades = DisponibilidadDoctor.objects.filter(doctor=doctor)
    context = get_user_context(request)
    context["disponibilidades"] = disponibilidades
    return render(request, "Citas/seleccionar_fecha.html", context)

def seleccionar_turno(request, disponibilidad_id):
    if not request.user.groups.filter(name="patient").exists():
        messages.error(request, "Solo los pacientes pueden acceder a esta página.")
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
        messages.error(request, "Solo los pacientes pueden acceder a esta página.")
        return redirect("home")

    disponibilidad = get_object_or_404(DisponibilidadDoctor, id=disponibilidad_id)
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
    cita = get_object_or_404(Cita, id=cita_id)

    # Renderizar la plantilla con los detalles de la cita

    context = get_user_context(request)
    context["cita"] = cita
    return render(request, 'Citas/detalle_cita.html', context)

def mis_citas(request):
    if not request.user.groups.filter(name="patient").exists():
        messages.error(request, "Solo los pacientes pueden acceder a esta página.")
        return redirect("home")

    citas = Cita.objects.filter(paciente=request.user).select_related('doctor', 'disponibilidad')
    context = get_user_context(request)
    context["citas"] = citas
    return render(request, "Citas/mis_citas.html", context)

def eliminar_cita(request, cita_id):
    if not request.user.groups.filter(name="patient").exists():
        messages.error(request, "Solo los pacientes pueden acceder a esta página.")
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    
    if request.method == 'POST':
        cita.delete()
        messages.success(request, "Cita eliminada con éxito.")
        return redirect('mis_citas')
    
    context = get_user_context(request)
    context["cita"] = cita
    return render(request, 'Citas/eliminar_cita.html', context)

#Vision de doctor

def citas_doctor(request):
    if not request.user.groups.filter(name="doctor").exists():
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect("home")

    citas = Cita.objects.filter(doctor=request.user).select_related('paciente', 'disponibilidad')
    context = get_user_context(request)
    context["citas"] = citas
    return render(request, "Citas/citas_doctor.html", context)

def detalle_cita_doctor(request, cita_id):
    if not request.user.groups.filter(name="doctor").exists():
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, doctor=request.user)
    context = get_user_context(request)
    context["cita"] = cita
    return render(request, 'Citas/detalle_cita_doctor.html', context)

def eliminar_cita_doctor(request, cita_id):
    if not request.user.groups.filter(name="doctor").exists():
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, doctor=request.user)
    
    if request.method == 'POST':
        cita.delete()
        messages.success(request, "Cita eliminada con éxito.")
        return redirect('citas_doctor')
    
    context = get_user_context(request)
    context["cita"] = cita
    return render(request, 'Citas/eliminar_cita_doctor.html', context)
