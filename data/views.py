from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as apiviews
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password,check_password
from django.http import JsonResponse, HttpResponse
from data.models import *
from datetime import datetime
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.utils import timezone
from django.db.models import Count, Q, F, OuterRef, Subquery
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
        results = []
        for evento in eventos_creados:
            results.append({'id': evento.pk, 'titulo_evento': evento.titulo_evento,
                            'pago':evento.pago, 'limite_asistentes':evento.limite_asistentes,
                            'descripcion_evento':evento.descripcion_evento, 'localizacion_evento_string':evento.localizacion_evento_string,
                            'fecha':evento.fecha
                            })
        return JsonResponse(results, safe=False)

    else:
        return JsonResponse({"error": "M  todo no permitido"}, status=405)

@csrf_exempt
def show_photo(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    
    # Construye la ruta completa de la foto
    photo_path = os.path.join(settings.MEDIA_ROOT, str(evento.foto_evento))
    print("photo_path: ",photo_path)
    
    # Verifica si la ruta es un archivo y no un directorio
    if os.path.isfile(photo_path):
        # Si la ruta es un archivo, lee el archivo de la foto y devuelve la respuesta
        with open(photo_path, 'rb') as photo_file:
            return HttpResponse(photo_file.read(), content_type='image/jpeg')
    else:
        # Si la ruta es un directorio o el archivo no existe, devuelve una imagen predeterminada o un código de estado 404
        default_image_path = os.path.join(settings.MEDIA_ROOT, 'event_photos', 'nophoto.jpg')
        if os.path.exists(default_image_path):
            with open(default_image_path, 'rb') as image_file:
                return HttpResponse(image_file.read(), content_type='image/jpeg')
        else:
            # Si no hay imagen predeterminada, devuelve un JSON con un mensaje de error
            return JsonResponse({'error': 'Foto no encontrada'}, status=404)

@csrf_exempt   
def show_photo_user(request, user_id):
    usuario = get_object_or_404(Usuario, pk=user_id)
    photo_path = os.path.join(settings.MEDIA_ROOT, str(usuario.foto_usuario))
    
    
    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo_file:
            return HttpResponse(photo_file.read(), content_type='image/jpeg')
    else:
        image_path = os.path.join(settings.MEDIA_ROOT, 'user_photos', 'no-photo-profile.png')
    
        if os.path.exists(image_path):
            with open(image_path, 'rb') as image_file:
                return HttpResponse(image_file.read(), content_type='image/jpeg')
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
            localizacion_evento_string=data.get('localizacion_evento_string', ''), 
            titulo_evento=data.get('titulo_evento',''),
			foto_evento=foto,
			fecha=data.get('fecha', None)
			)
		nuevo_evento.save()


		UsuarioEvento.objects.create(usuario=usuario, evento=nuevo_evento)

		return JsonResponse({"mensaje": "Evento creado exitosamente"}, status=201)

	else:
		return JsonResponse({"error": "M  todo no permitido"}, status=405)

@api_view(['POST'])
def update_event_data(request):
        datos = request.data
        token_data = datos.get('token', None)
        evento_id = datos.get('evento_id', None)
        foto = request.FILES.get('foto', None)

        if token_data is None:
            return JsonResponse({"error": "Token invalido"}, status=400)
        get_object_or_404(Usuario, token=token_data)

        evento = get_object_or_404(Evento, pk=evento_id)
        try:
            if 'titulo_evento' in datos:
                evento.titulo_evento = datos['titulo_evento']
            if 'pago' in datos:
                evento.pago = datos['pago']
            if 'limite_asistentes' in datos:
                evento.limite_asistentes = datos['limite_asistentes']
            if 'descripcion_evento' in datos:
                evento.descripcion_evento = datos['descripcion_evento']
            if 'localizacion_evento' in datos:
                evento.localizacion_evento = datos['localizacion_evento']
            if 'localizacion_evento_string' in datos:
                evento.localizacion_evento_string = datos['localizacion_evento_string']
            if 'fecha' in datos:
                evento.fecha = datos['fecha']
            if foto is not None:
                evento.foto_evento = datos['foto']
            
            evento.save()
            return JsonResponse({'mensaje': 'Datos del evento actualizados correctamente'})
        except KeyError as e:
            return JsonResponse({'error': f"Error al actualizar el evento: {str(e)}"}, status=400)


@api_view(['POST'])
def get_event_data(request,evento_id):
        data = request.data
        token_data = data.get('token', None)
        if token_data is None:
            return JsonResponse({"error": "Token invalido"}, status=400)
        get_object_or_404(Usuario, token=token_data)
        evento = get_object_or_404(Evento, pk=evento_id)
        evento_data={'id': evento.pk, 'usuario_anfitrion': evento.usuario_anfitrion.pk, 'titulo_evento': evento.titulo_evento,
                            'pago':evento.pago, 'limite_asistentes':evento.limite_asistentes,
                            'descripcion_evento':evento.descripcion_evento, 'localizacion_evento_string':evento.localizacion_evento_string,
                            'localizacion_evento':evento.localizacion_evento,
                            'fecha':evento.fecha
                            }
        return JsonResponse(evento_data, safe=False)







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
            "fecha_nacimiento":usuario.fecha_nacimiento,
            "foto_usuario":"user/"+ str(usuario.pk)+"/photo/"
        })

        return JsonResponse({"mensaje": "Evento creado exitosamente"}, status=201)

    else:
        return JsonResponse({"error": "M  todo no permitido"}, status=405)
    
@api_view(['POST'])
def update_user_data(request):
    if request.method == 'POST':
        user_data = request.data
        token_data = user_data.get('token', None)
        foto = request.FILES.get('foto', None)
        try:
            user = get_object_or_404(Usuario, token=token_data)
            if 'email' in user_data:
                user.email = user_data.get('email')
            if 'name' in user_data:
                user.nombre_usuario = user_data.get('name')
            if 'surname' in user_data:
                user.apellido_usuario = user_data.get('surname')
            if 'birth' in user_data:
                user.fecha_nacimiento = user_data.get('birth')
            if 'phone' in user_data:
                user.telefono = user_data.get('phone')
            if foto is not None:
                user.foto_usuario = foto
            

            user.save()
            return JsonResponse({'message': 'User data updated successfully'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
@api_view(['POST'])
def update_user_ubi(request):
    if request.method == 'POST':
        user_data = request.data
        token_data = user_data.get('token', None)
        try:
            user = get_object_or_404(Usuario, token=token_data)
            if 'ubi' in user_data:
                user.localizacion_usuario = user_data.get('ubi')
            

            user.save()
            return JsonResponse({'message': 'User data updated successfully'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
@api_view(['POST'])
def delete_event(request):
    if request.method == 'POST':
        data = request.data
        token_data = data.get('token', None)
        evento_id = data.get('evento_id', None)
        if token_data is None:
            return JsonResponse({"error": "Token invalido"}, status=400)
        usuario = get_object_or_404(Usuario, token=token_data)
        evento = get_object_or_404(Evento, pk=evento_id)
        evento.delete()  
        return JsonResponse({"mensaje": "Evento eliminado correctamente"})
    
@api_view(['POST'])
def get_events_locations(request):
    if request.method == 'POST':
        data = request.data
        token_data = data.get('token', None)

        if token_data is None:
            return JsonResponse({"error": "Token invalido"}, status=400)
        
        usuario = get_object_or_404(Usuario, token=token_data)
        
        subquery = UsuarioEvento.objects.filter(
            usuario=usuario,
            evento=OuterRef('pk')
        ).values('evento_id')
        
        eventos = Evento.objects.filter(
            fecha__gt=timezone.now(),
            limite_asistentes__gt=Subquery(subquery)
        ).exclude(usuarioevento__usuario=usuario)

        localizaciones = []
        
        for evento in eventos:
            # Verificar si no existe un UsuarioEvento con este usuario y evento
            if not UsuarioEvento.objects.filter(usuario=usuario, evento=evento).exists():
                # Comprobar que la fecha sea posterior a la del evento
                if evento.fecha > timezone.now():
                    # Verificar que la suma de UsuarioEvento con el evento sea menor al límite
                    cantidad_asistentes = UsuarioEvento.objects.filter(evento=evento).count()
                    if cantidad_asistentes < evento.limite_asistentes:
                        localizacion_json = json.loads(evento.localizacion_evento)

                        evento_json = {
                            'lat': localizacion_json['lat'],
                            'lng': localizacion_json['lng'],
                            'titulo_evento': evento.titulo_evento,
                            'id_evento': evento.pk,
                            'usuario_anfitrion': evento.usuario_anfitrion.nombre_usuario,
                            'localizacion_evento_string': evento.localizacion_evento_string,
                            'fecha': evento.fecha,
                            'descripcion_evento': evento.descripcion_evento
                        }
                        
                        localizaciones.append(evento_json)

        return JsonResponse(localizaciones, safe=False)


@api_view(['POST'])
def join_event(request):
    if request.method == 'POST':
        data = request.data
        token_data = data.get('token', None)
        evento_id = data.get('evento_id', None)
        if token_data is None:
            return JsonResponse({"error": "Token invalido"}, status=400)
        
        usuario = get_object_or_404(Usuario, token=token_data)
        evento = get_object_or_404(Evento, pk=evento_id)

        usuario_evento = UsuarioEvento(usuario=usuario, evento=evento)
        usuario_evento.save()

        return JsonResponse({"mensaje": "UsuarioEvento creado correctamente"})