from django.urls import path 
from django.contrib.auth.decorators import login_required
from task import views
from .views import Inicio
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', Inicio.as_view(), name='home'),
    path('salir/', views.salir, name='salir'), 
    path('perfilPaciente/<str:username>/', login_required(views.perfilPaciente), name='perfilPaciente'),
    path('perfilDoctor/<str:username>/', login_required(views.perfilDoctor), name='perfilDoctor'),
    
    #URLS CAMBIAR CONTRASEñA
    path('change_password/', login_required(views.ProfilePasswordChangeView.as_view()), name='change_password'),
  
    #URLS DE DOCTOR
    path('RegistroDoctor/',login_required(views.create_doctor),name='RegistroDoctor'),
    path('ListarDoctor/', login_required(views.ListaDoctores.as_view()) , name='ListarDoctor'),
    path('EditarDoctor/<int:pk>/',login_required( views.EditarDoctor.as_view()), name='EditarDoctor'),
    path('EliminarDoctor/<int:pk>/', login_required(views.EliminarDoctor.as_view()), name='EliminarDoctor'),
    path('EditarDoctorPerfil/<int:pk>/', login_required(views.EditarDoctorPerfil.as_view()), name='EditarDoctorPerfil'),
    
    #URLS DE PACIETE

    path('register/', views.register , name='register'),
    path('ListarPaciente/', login_required(views.ListaPacientes.as_view()) , name='ListarPaciente'),
    path('EliminarPaciente/<int:pk>/', login_required(views.EliminarPaciente.as_view()), name='EliminarPaciente'),
    path('EditarPaciente/<int:pk>/', login_required(views.EditarPaciente.as_view()), name='EditarPaciente'),
    path('EditarPacientePerfil/<int:pk>/', login_required(views.EditarPacientePerfil.as_view()), name='EditarPacientePerfil'),
    
    #URLS DE DISPONIBILIDAD DEL DOCTOR
    path('crear-disponibilidad/', login_required(views.crear_disponibilidad), name='crear-disponibilidad'),
    path('ver-disponibilidad/', login_required(views.ver_disponibilidad), name='ver_disponibilidad'),
    path("eliminar-disponibilidad/<int:pk>/", login_required(views.eliminar_disponibilidad), name="eliminar_disponibilidad"),
    path("modificar-disponibilidad<int:pk>/", login_required(views.modificar_disponibilidad), name="modificar_disponibilidad"),

    #URLS DE CITAS   
    #Paciente
    path('seleccionar-doctor/', views.seleccionar_doctor, name='seleccionar_doctor'),
    path('seleccionar-fecha/<int:doctor_id>/', views.seleccionar_fecha, name='seleccionar_fecha'),
    path('seleccionar-turno/<int:disponibilidad_id>/', login_required( views.seleccionar_turno), name='seleccionar_turno'),
    path('agendar-cita/<int:disponibilidad_id>/', login_required( views.agendar_cita), name='agendar_cita'),
    path('detalle-cita/<int:cita_id>/', login_required( views.detalle_cita), name='detalle_cita'),
    path('mis_citas/', login_required(views.mis_citas), name='mis_citas'),
    path('eliminar_cita/<int:cita_id>/',  login_required(views.eliminar_cita), name='eliminar_cita'),
    
    #Consultas
    path('consultas-paciente/', login_required(views.citas_atendidas_paciente), name='consultas_paciente'),
    path('detalle-cita-paciente/<int:cita_id>/', login_required(views.detalle_cita_paciente), name='detalle_cita_paciente'),
  
    #Doctor
    path('doctor/citas/',  login_required(views.citas_doctor), name='citas_doctor'),
    path('doctor/cita/<int:cita_id>/',  login_required(views.detalle_cita_doctor), name='detalle_cita_doctor'),
    path('doctor/eliminar_cita/<int:cita_id>/', login_required(views.eliminar_cita_doctor), name='eliminar_cita_doctor'),
    path('cita/<int:cita_id>/atender/',  login_required(views.atender_cita), name='atender_cita'),
    
    #Historial
    path('doctor/historial',  login_required(views.doctor_historial), name='doctor_historial'),
    path('doctor/cita/historial/<int:cita_id>/',  login_required(views.detalle_cita_doctor_historial), name='detalle_cita_doctor_historial'),
    path('eliminar-cita-historial/<int:cita_id>/', login_required(views.eliminar_cita_historial), name='eliminar_cita_historial'),
    
]