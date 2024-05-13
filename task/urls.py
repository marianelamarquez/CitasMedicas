from django.urls import path 
from django.contrib.auth.decorators import login_required
from task import views
from .views import Inicio
#from .views import ListaCitas,CrearCita, ModificarCita, EliminarCita

urlpatterns = [
    path('', Inicio.as_view(), name='home'),
    path('salir/', views.salir, name='salir'), 
    path('perfilPaciente/<str:username>/', login_required(views.perfilPaciente), name='perfilPaciente'),
    path('perfilDoctor/<str:username>/', login_required(views.perfilDoctor), name='perfilDoctor'),
      
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
    


    # URLS DE CITAS
    #path('crear/',login_required( CrearCita.as_view()), name='crear_cita'),
    #path('modificar/<int:pk>/',login_required( ModificarCita.as_view()), name='modificar_cita'),
    #path('eliminar/<int:pk>/',login_required( EliminarCita.as_view()), name='eliminar_cita'),
    #path('lista-citas/',login_required( ListaCitas.as_view()), name='lista_citas'),

    
]