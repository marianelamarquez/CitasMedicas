import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser

#Tablas como de bdd


#-----USUARIO-----
class CustomUser(AbstractUser):
    ncolegiom = models.CharField(max_length=20, unique=True,blank=True, null=True )
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
    def obtener_turnos_disponibles(self):
        hoy = datetime.date.today()
        hora_inicio = datetime.datetime.combine(hoy, self.hora_inicio)
        hora_fin = datetime.datetime.combine(hoy, self.hora_fin)

        turnos_disponibles = []
        hora_inicio_turno = hora_inicio
        while hora_inicio_turno < hora_fin:
            hora_fin_turno = hora_inicio_turno + datetime.timedelta(hours=1)
            if hora_fin_turno > hora_fin:
                break
            turnos_disponibles.append(
                (hora_inicio_turno.time(), hora_fin_turno.time())
            )
            hora_inicio_turno = hora_fin_turno

        return turnos_disponibles
    
#--------CITA------
class Cita(models.Model):
    paciente = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='citas_programadas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    disponibilidad = models.ForeignKey(DisponibilidadDoctor, on_delete=models.CASCADE) 
