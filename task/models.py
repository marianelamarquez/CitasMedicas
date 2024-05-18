from django.db import models
from django.contrib.auth.models import User, AbstractUser

#Tablas como de bdd


#-----USUARIO-----
class CustomUser(AbstractUser):
    ncolegiom = models.CharField(max_length=20, unique=True, blank=True)
    telefono = models.CharField(max_length=25)
    direccion = models.CharField(max_length=255)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_users',  # Custom name for the reverse relation
        blank=True,
        help_text='The groups this user belongs to. A user can belong to multiple groups.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_users',  # Custom name for the reverse relation
        blank=True,
        help_text='Specific permissions for this user.'
    )

#-----DISPONIBILIDAD DE DOCTOR-----
class DisponibilidadDoctor(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()





#--------CITA------
class Appointment(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_appointments')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
