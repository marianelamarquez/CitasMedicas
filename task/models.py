from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.
#tablas como de bdd

class CustomUser(AbstractUser):
    ncolegiom = models.CharField(max_length=20, unique=True, blank=True)
    telefono = models.CharField(max_length=25,default='00000000000')
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


