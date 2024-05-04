from django.db import models
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token

class Usuario(models.Model):
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    nombre_usuario = models.CharField(max_length=50, blank=True, null=True)
    apellido_usuario = models.CharField(max_length=50, blank=True, null=True)
    foto_usuario = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    localizacion_usuario = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True) 
    fecha_nacimiento = models.DateField(blank=True, null=True)
    SEXO_CHOICES = (
        ('H', 'Hombre'),
        ('M', 'Mujer'),
    )
    sexo_usuario = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True, null=True)
    token = models.CharField(max_length=40, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


class Grupo(models.Model):
    nombre_grupo = models.CharField(max_length=100)
    descripcion_grupo = models.TextField()
    foto_grupo = models.ImageField(upload_to='group_photos/', blank=True, null=True)

class UsuarioGrupo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)

class Evento(models.Model):
    usuario_anfitrion = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    titulo_evento = models.CharField(max_length=100)
    pago = models.BooleanField()
    limite_asistentes = models.IntegerField()
    descripcion_evento = models.TextField()
    localizacion_evento = models.CharField(max_length=255)
    localizacion_evento_string = models.CharField(max_length=200)
    foto_evento = models.ImageField(upload_to='event_photos/', blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

class UsuarioEvento(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)

