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
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.serializers import serialize
import uuid,secrets,json,os




@api_view(['POST'])
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
def inicialize_events_page(request):
	if request.method == 'POST':
		data = request.data
		token_data = data.get('token', None)
		if token_data is None:
			 return JsonResponse({"error": "Token invalido"}, status=400)
		usuario = get_object_or_404(Usuario, token=token_data)
		eventos_creados = Evento.objects.filter(usuario_anfitrion=usuario).order_by('-fecha')
		eventos_json = serialize('json', eventos_creados)
		return JsonResponse(eventos_json, safe=False)

	else:
		 return JsonResponse({"error": "M  todo no permitido"}, status=405)


def show_photo(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    photo_path = os.path.join(settings.MEDIA_ROOT, str(evento.foto_evento))
    
    
    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo_file:
            return HttpResponse(photo_file.read(), content_type='image/jpeg')
    else:
        return HttpResponse(status=404)

@api_view(['POST'])
def create_new_event(request):
	if request.method == 'POST':
		data = request.data
		token_data = data.get('token', None)
		if token_data is None:
			return JsonResponse({"error": "Token invalido"}, status=400)
		usuario = get_object_or_404(Usuario, token=token_data)
		foto = request.FILES.get('foto')
		nuevo_evento = Evento(
			usuario_anfitrion= usuario,
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

def get_default_photo(request):
    
    image_path = os.path.join(settings.MEDIA_ROOT, 'event_photos', 'nophoto.jpg')
    
    if os.path.exists(image_path):
        with open(image_path, 'rb') as image_file:
            return HttpResponse(image_file.read(), content_type='image/jpeg')
    else:
        return HttpResponse(status=404)

@api_view(['POST'])
def get_user_data(request):
    if request.method == 'POST':
		data = request.data
		token_data = data.get('token', None)
		if token_data is None:
			return JsonResponse({"error": "Token invalido"}, status=400)
		usuario = get_object_or_404(Usuario, token=token_data)
		return JsonResponse({
            "email":usuario.email,
            "telefono":usuario.telefono,
            "nombre_usuario":usuario.nombre_usuario,
            "apellido_usuario":usuario.apellido_usuario,
            "fecha_nacimiento":usuario.fecha_nacimiento
        })

		return JsonResponse({"mensaje": "Evento creado exitosamente"}, status=201)

	else:
		return JsonResponse({"error": "M  todo no permitido"}, status=405)