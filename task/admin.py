from django.contrib import admin
from .models import CustomUser
# Register your models here.


# Registra el modelo en el sitio de administración

admin.site.register(CustomUser)
