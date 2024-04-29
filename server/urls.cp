"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as apiviews
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password,check_password
from django.http import JsonResponse, HttpResponse
from data.models import *
from datetime import datetime
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.contrib.staticfiles.templatetags.staticfiles import static
import uuid,secrets,json


@api_view(['GET'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_init(request):
    return JsonResponse({
        "usuari":request.user.username,
        "mensaje": "GRANDE JEFE"
        })


@api_view(['POST'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_register(request):
    if request.method == 'POST':
        data = request.data
        email = data.get('email', None)
        apellido = data.get('surname', None)
        nombre_usuario = data.get('name', None)
        passUser = data.get('password', None)
        fecha_nacimiento = data.get('date_born', None)
        sexo_usuario = data.get('sex', None)
        token = secrets.token_hex(16)

        if Usuario.objects.filter(email=email).exists():
            return JsonResponse({"error": "El correo electrónico ya está registrado"}, status=404)


        if email is None or nombre_usuario is None or apellido is None or nombre_usuario is None or passUser is None or sexo_usuario is None or fecha_nacimiento is None:
            return JsonResponse({"error": "Faltan datos requeridos"}, status=400)






        nuevo_usuario = Usuario(
            email=email,
            nombre_usuario=nombre_usuario,
            apellido_usuario=apellido,
            password = passUser,
	    fecha_nacimiento=datetime.strptime(fecha_nacimiento, '%Y-%m-%d'),
            sexo_usuario=sexo_usuario,
            token=token
        )

        nuevo_usuario.save()

        return JsonResponse({

                'email': nuevo_usuario.email,
                'nombre_usuario': nuevo_usuario.nombre_usuario,
                'apellido_usuario': nuevo_usuario.apellido_usuario,
                'fecha_nacimiento': nuevo_usuario.fecha_nacimiento,
                'sexo_usuario': nuevo_usuario.sexo_usuario,
                'token': nuevo_usuario.token,
                'tipo':'registro'
            
        }, status=201)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)



@api_view(['POST'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_login(request):
    if request.method == 'POST':
        data = request.data
        user = data.get('user', None)
        passUser = data.get('password', None)


        if user is None or  passUser is None:
            return JsonResponse({"error": "Faltan datos requeridos"}, status=400)

        usuario = get_object_or_404(Usuario, email=user)

        if not check_password(passUser, usuario.password):
            return JsonResponse({"error": "Usuario o contraseña incorrectos"}, status=404)

        return JsonResponse({
            "mensaje": "Usuario logeado  exitosamente",
	    "token": usuario.token
        })
    else:
        return JsonResponse({"error": "M  todo no permitido"}, status=405)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def token_user(request):
	if request.method == 'POST':
		data = request.data
		token_data = data.get('token', None)
		if token_data is None:
			return JsonResponse({"error": "Token invalido"}, status=400)
		usuario = get_object_or_404(Usuario, token=token_data)
		return HttpResponse(json.dumps(usuario.__dict__), content_type="application/json")
	else:
		return JsonResponse({"error": "M  todo no permitido"}, status=405)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def inicialize_events_page(request):
	if request.method == 'POST':
		data = request.data
		token_data = data.get('token', None)
		if token_data is None:
			 return JsonResponse({"error": "Token invalido"}, status=400)
		usuario = get_object_or_404(Usuario, token=token_data)
		eventos_creados = Evento.objects.filter(id_anfitrion__usuario=usuario).order_by('-fecha')
		eventos_json = serialize('json', eventos_creados)
		return JsonResponse(eventos_json, safe=False)

	else:
		 return JsonResponse({"error": "M  todo no permitido"}, status=405)



@api_view(['POST'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def create_new_event(request):
	if request.method == 'POST':
		data = request.data
		token_data = data.get('token', None)
		if token_data is None:
			return JsonResponse({"error": "Token invalido"}, status=400)
		usuario = get_object_or_404(Usuario, token=token_data)
		foto = request.FILES.get('foto')
		nuevo_evento = Evento(
			id_anfitrion=Anfitrion.objects.get(usuario=usuario),
			pago=data.get('pago', False),
			limite_asistentes=data.get('limite_asistentes', 0),
			descripcion_evento=data.get('descripcion_evento', ''),
			localizacion_evento=data.get('localizacion_evento', ''),
			foto_evento=foto,
			fecha=data.get('fecha', None)
			)
		nuevo_evento.save()


		UsuarioEvento.objects.create(usuario=usuario, evento=nuevo_evento)

		return JsonResponse({"mensaje": "Evento creado exitosamente"}, status=201)

	else:
		return JsonResponse({"error": "M  todo no permitido"}, status=405)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', apiviews.obtain_auth_token),
    path('', include('data.urls')),
    path('api/', api_init),
    path('login/', api_login),
    path('register/',api_register),
    path('creation_events_page/',inicialize_events_page),
    path('create_new_event/',create_new_event)
]

