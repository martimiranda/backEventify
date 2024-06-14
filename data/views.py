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
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.utils import timezone
from django.db.models import Count, Q, F, OuterRef, Subquery
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import EmailForm, PasswordResetForm

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
        passUser = make_password(passUser)
        if passUser != usuario.password:
            return JsonResponse({"error": "M  todo no permitido"}, status=404)

            

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
            usuarios_unidos =  UsuarioEvento.objects.filter(evento=evento).count() -1

            results.append({'id': evento.pk, 'titulo_evento': evento.titulo_evento,
                            'pago':evento.pago, 'limite_asistentes':evento.limite_asistentes,
                            'descripcion_evento':evento.descripcion_evento, 'localizacion_evento_string':evento.localizacion_evento_string,
                            'fecha':evento.fecha, 'usuarios_unidos':usuarios_unidos
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
    
    
    if os.path.isfile(photo_path):
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
def show_users_on_event(request):
    if request.method == 'POST':
        data = request.data
        evento_id = data.get('idEvento', None)
        evento = get_object_or_404(Evento, pk=evento_id)
        token_data = data.get('token', None)
        if token_data is None:
            return JsonResponse({"error": "Token invalido"}, status=400)
        usuario = get_object_or_404(Usuario, token=token_data)
        usuarios_evento = UsuarioEvento.objects.filter(evento=evento).exclude(usuario=evento.usuario_anfitrion)
        
        usuarios_data = []
        for usuario_evento in usuarios_evento:
            usuario_data = {
                'id': usuario_evento.usuario.pk,
                'email': usuario_evento.usuario.email,
                'telefono': usuario_evento.usuario.telefono,
                'nombre_usuario': usuario_evento.usuario.nombre_usuario,
                'apellido_usuario': usuario_evento.usuario.apellido_usuario,
                'foto_usuario': usuario_evento.usuario.foto_usuario.url if usuario_evento.usuario.foto_usuario else None,
                'localizacion_usuario': usuario_evento.usuario.localizacion_usuario,
                'fecha_nacimiento': usuario_evento.usuario.fecha_nacimiento,
                'sexo_usuario': usuario_evento.usuario.sexo_usuario,
                'biografia_usuario': usuario_evento.usuario.biografia_usuario,
                'evento_id': usuario_evento.evento.pk,
                'evento_name':usuario_evento.evento.titulo_evento
            }
            
            usuarios_data.append(usuario_data)
        
        return JsonResponse({'usuarios': usuarios_data})
		


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
            #intereses_evento = data.get('intereses_evento',''),
            foto_evento=foto,
            fecha=data.get('fecha', None)
            )
        nuevo_evento.save()
        intereses_evento = data.get('intereses_evento')
        intereses_evento = [s.strip() for s in intereses_evento.split(',')]
        print(intereses_evento)
        for interes in intereses_evento:
            interes_obj = get_object_or_404(Interes, nombre=interes)
            nuevo_evento.intereses_evento.add(interes_obj)


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
        intereses = evento.intereses_evento.all()
        intereses_data = [interes.nombre for interes in intereses]
        evento_data={'id': evento.pk, 'usuario_anfitrion': evento.usuario_anfitrion.pk, 'titulo_evento': evento.titulo_evento,
                            'pago':evento.pago, 'limite_asistentes':evento.limite_asistentes,
                            'descripcion_evento':evento.descripcion_evento, 'localizacion_evento_string':evento.localizacion_evento_string,
                            'localizacion_evento':evento.localizacion_evento,
                            'fecha':evento.fecha,'intereses_evento':intereses_data
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
        intereses_usuario = usuario.intereses_usuario.all().values_list('nombre', flat=True)
        return JsonResponse({
            "email":usuario.email,
            "telefono":usuario.telefono,
            "nombre_usuario":usuario.nombre_usuario,
            "apellido_usuario":usuario.apellido_usuario,
            "fecha_nacimiento":usuario.fecha_nacimiento,
            "foto_usuario":"user/"+ str(usuario.pk)+"/photo/",
            "biografia_usuario":usuario.biografia_usuario,
            "intereses_usuario":list(intereses_usuario)
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
            if 'biography' in user_data:
                user.biografia_usuario = user_data.get('biography')
            if foto is not None:
                user.foto_usuario = foto
            

            user.save()
            return JsonResponse({'message': 'User data updated successfully'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



@api_view(['POST'])
def update_interest_user_data(request):
    if request.method == 'POST':
        user_data = request.data
        token_data = user_data.get('token', None)
        try:
            user = get_object_or_404(Usuario, token=token_data)
            if 'intereses' in user_data:
                intereses = user_data.get('intereses')
                user.intereses_usuario.clear()  
                for interes in intereses:
                    interes_obj = get_object_or_404(Interes, nombre=interes)
                    user.intereses_usuario.add(interes_obj)
            

            user.save()
            return JsonResponse({'message': 'User data updated successfully'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
@api_view(['POST'])
def update_user_bio(request):
    if request.method == 'POST':
        user_data = request.data
        token_data = user_data.get('token', None)
        try:
            user = get_object_or_404(Usuario, token=token_data)
            if 'bio' in user_data:
                biografia = user_data.get('bio')
                user.biografia_usuario = biografia
            

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
            return JsonResponse({"error": "Token inválido"}, status=400)
        
        usuario = get_object_or_404(Usuario, token=token_data)
        usuarioEvento = UsuarioEvento.objects.filter(usuario=usuario) 
        if usuarioEvento.exists():
            eventos = Evento.objects.exclude(usuario_anfitrion=usuario).exclude(
                Q(pk__in=usuarioEvento.values_list('evento_id', flat=True))
            )
        else:
            eventos = Evento.objects.exclude(usuario_anfitrion=usuario)

        
        
        # Filtrar eventos que no tienen un UsuarioEvento para el mismo usuario y el mismo evento,
        # y cuya fecha sea posterior a la actual



        localizaciones = []
        
        for evento in eventos:
            localizacion_json = json.loads(evento.localizacion_evento)
            usuarios_unidos =  UsuarioEvento.objects.filter(evento=evento).count() -1


            evento_json = {
                'lat': localizacion_json['lat'],
                'lng': localizacion_json['lng'],
                'titulo_evento': evento.titulo_evento,
                'id_evento': evento.pk,
                'usuario_anfitrion': evento.usuario_anfitrion.nombre_usuario,
                'localizacion_evento_string': evento.localizacion_evento_string,
                'fecha': evento.fecha,
                'descripcion_evento': evento.descripcion_evento,
                'usuarios_unidos':usuarios_unidos,
                'limite_asistentes':evento.limite_asistentes
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

        mensaje = f"{usuario.nombre_usuario} se ha unido a tu evento {evento.titulo_evento}"
        notificacion = NotificacionUsuario(
            usuario=evento.usuario_anfitrion,
            mensaje=mensaje,
            notification_type="Evento"
        )
        notificacion.save()

        return JsonResponse({"mensaje": "UsuarioEvento creado correctamente"})

@api_view(['POST'])
def show_events_joins(request):
    if request.method == 'POST':
        data = request.data
        token_data = data.get('token', None)
        if token_data is None:
            return JsonResponse({"error": "Token inválido"}, status=400)
        usuario = get_object_or_404(Usuario, token=token_data)
        
        eventos_anfitrion_ids = Evento.objects.filter(usuario_anfitrion=usuario).values_list('id', flat=True)
        
        eventos_participante_ids = UsuarioEvento.objects.filter(usuario=usuario).values_list('evento_id', flat=True)
        
        eventos_creados = Evento.objects.exclude(id__in=eventos_anfitrion_ids)
        
        eventos_joins = eventos_creados.filter(id__in=eventos_participante_ids).order_by('-fecha')
        
        results = []
        for evento in eventos_joins:
            usuarios_unidos =  UsuarioEvento.objects.filter(evento=evento).count() - 1
            

            results.append({'id': evento.pk, 'titulo_evento': evento.titulo_evento,
                            'pago':evento.pago, 'limite_asistentes':evento.limite_asistentes,
                            'descripcion_evento':evento.descripcion_evento, 'localizacion_evento_string':evento.localizacion_evento_string,
                            'fecha':evento.fecha, 'usuarios_unidos':usuarios_unidos
                            })
        return JsonResponse(results, safe=False)

    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)

@api_view(['POST'])
def unsuscribe_event(request):
    if request.method == 'POST':
        data = request.data
        token_data = data.get('token', None)
        evento_id = data.get('evento_id', None)
        if token_data is None:
            return JsonResponse({"error": "Token invalido"}, status=400)
        usuario = get_object_or_404(Usuario, token=token_data)
        evento = get_object_or_404(Evento, pk=evento_id)
        union = get_object_or_404(UsuarioEvento, usuario=usuario, evento=evento) 
        union.delete() 
        return JsonResponse({"mensaje": "Evento eliminado correctamente"})



@api_view(['POST'])
def show_events_by_interests(request):
    if request.method == 'POST':
        data = request.data
        token_data = data.get('token', None)
        
        if token_data is None:
            return JsonResponse({"error": "Token inválido"}, status=400)
        
        usuario = get_object_or_404(Usuario, token=token_data)
        
        intereses_usuario = usuario.intereses_usuario.all()
        
        if intereses_usuario.exists():
            eventos = Evento.objects.filter(intereses_evento__in=intereses_usuario).distinct().order_by('-fecha')
        else:
            eventos = Evento.objects.all().order_by('-fecha')
        
        eventos_unidos_ids = UsuarioEvento.objects.filter(usuario=usuario).values_list('evento_id', flat=True)
        eventos = eventos.exclude(id__in=eventos_unidos_ids)
        
        results = []
        for evento in eventos:
            usuarios_unidos = UsuarioEvento.objects.filter(evento=evento).count()-1
            intereses_evento = evento.intereses_evento.all().values_list('nombre', flat=True)

            results.append({
                'id': evento.pk, 
                'titulo_evento': evento.titulo_evento,
                'pago': evento.pago, 
                'limite_asistentes': evento.limite_asistentes,
                'descripcion_evento': evento.descripcion_evento, 
                'localizacion_evento_string': evento.localizacion_evento_string,
                'fecha': evento.fecha, 
                'intereses': list(intereses_evento),

                'usuarios_unidos': usuarios_unidos
            })
        
        return JsonResponse(results, safe=False)
    
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)

@api_view(['POST'])
def admin_unsuscribe_event(request):
    if request.method == 'POST':
        data = request.data
        usuario_id = data.get('usuario_id', None)
        evento_id = data.get('evento_id', None)
        usuario = get_object_or_404(Usuario, pk=usuario_id)
        evento = get_object_or_404(Evento, pk=evento_id)
        union = get_object_or_404(UsuarioEvento, usuario=usuario, evento=evento) 
        union.delete() 
        return JsonResponse({"mensaje": "Evento eliminado correctamente"})
    
@api_view(['POST'])
def make_notification(request):
    if request.method == 'POST':
        data = request.data
        usuario_id = data.get('usuario_id', None)
        mensaje = data.get('mensaje', None)
        notification_type = data.get('notification_type', None)
        usuario = get_object_or_404(Usuario, pk=usuario_id)

        notificacion = NotificacionUsuario(usuario=usuario, mensaje=mensaje, notification_type=notification_type)
        notificacion.save()
        
        return JsonResponse({"mensaje": "Evento eliminado correctamente"})

@api_view(['POST'])
def get_user_notifications(request):
    if request.method == 'POST':
        data = request.data
        token_data = data.get('token', None)
        if token_data is None:
            return JsonResponse({"error": "Token invalido"}, status=400)
        usuario = get_object_or_404(Usuario, token=token_data)
        notifications = NotificacionUsuario.objects.filter(usuario=usuario)

        results = []
        for notification in notifications:
            results.append({
                'usuario_id': notification.usuario.id,
                'mensaje': notification.mensaje,
                'notification_type': notification.notification_type,
                'notificacion_id': notification.pk,
                # Añade más campos si es necesario
            })
        
        return JsonResponse(results, safe=False)

    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
@api_view(['POST'])
def delete_notification(request):
    if request.method == 'POST':
        data = request.data
        notificacion_id = data.get('notificacion_id', None)
        notificacion = get_object_or_404(NotificacionUsuario, pk=notificacion_id)
        notificacion.delete()  
        return JsonResponse({"mensaje": "Notificacion eliminada correctamente"})
    
@api_view(['POST'])
def search_events(request, query):
    if request.method == 'POST':
        data = request.data
        token_data = data.get('token', None)
        
        if token_data is None:
            return JsonResponse({"error": "Token inválido"}, status=400)
        
        usuario = get_object_or_404(Usuario, token=token_data)
        eventos = Evento.objects.filter(titulo_evento__icontains=query).distinct().order_by('-fecha')
        eventos_unidos_ids = UsuarioEvento.objects.filter(usuario=usuario).values_list('evento_id', flat=True)
        eventos = eventos.exclude(id__in=eventos_unidos_ids)
        results = []
        for evento in eventos:
            usuarios_unidos = UsuarioEvento.objects.filter(evento=evento).count() - 1
            intereses_evento = evento.intereses_evento.all().values_list('nombre', flat=True)

            results.append({
                'id': evento.pk,
                'titulo_evento': evento.titulo_evento,
                'pago': evento.pago,
                'limite_asistentes': evento.limite_asistentes,
                'descripcion_evento': evento.descripcion_evento,
                'localizacion_evento_string': evento.localizacion_evento_string,
                'fecha': evento.fecha,
                'intereses': list(intereses_evento),
                'usuarios_unidos': usuarios_unidos
            })
        
        return JsonResponse(results, safe=False)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)

@api_view(['POST'])
def search_events_by_date(request, date_filter):
    if request.method == 'POST':
        data = request.data
        token_data = data.get('token', None)
        
        if token_data is None:
            return JsonResponse({"error": "Token inválido"}, status=400)
        
        usuario = get_object_or_404(Usuario, token=token_data)
        now = timezone.now()

        if date_filter == 'Hoy':
            start_date = now
            end_date = now + timedelta(days=1)
        elif date_filter == 'Mañana':
            start_date = now + timedelta(days=1)
            end_date = now + timedelta(days=2)
        elif date_filter == 'Esta semana':
            start_date = now
            end_date = now + timedelta(days=7)
        elif date_filter == 'Este mes':
            start_date = now
            end_date = now + timedelta(days=30)
        else:
            return JsonResponse({"error": "Tipo de fecha no válido"}, status=400)

        eventos = Evento.objects.filter(
            fecha__range=(start_date, end_date)
        ).distinct().order_by('-fecha')
        eventos_unidos_ids = UsuarioEvento.objects.filter(usuario=usuario).values_list('evento_id', flat=True)
        eventos = eventos.exclude(id__in=eventos_unidos_ids)

        results = []
        for evento in eventos:
            usuarios_unidos = UsuarioEvento.objects.filter(evento=evento).count() - 1
            intereses_evento = evento.intereses_evento.all().values_list('nombre', flat=True)

            results.append({
                'id': evento.pk,
                'titulo_evento': evento.titulo_evento,
                'pago': evento.pago,
                'limite_asistentes': evento.limite_asistentes,
                'descripcion_evento': evento.descripcion_evento,
                'localizacion_evento_string': evento.localizacion_evento_string,
                'fecha': evento.fecha,
                'intereses': list(intereses_evento),
                'usuarios_unidos': usuarios_unidos
            })
        
        return JsonResponse(results, safe=False)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)
    


def email_view(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            usuario = get_object_or_404(Usuario, email=email)
            nombre = usuario.nombre_usuario
            token = usuario.token

            reset_password_link = f'https://eventify.ieti.site/reset_password?token={token}'

            email_subject = 'Solicitud de cambio de contraseña'
            email_body = (
                f'Estimado/a usuario {nombre},\n\n'
                'Hemos recibido una solicitud para cambiar la contraseña de su cuenta.\n'
                'Para proceder con el cambio de contraseña, por favor haga clic en el siguiente enlace:\n\n'
                f'{reset_password_link}\n\n'
                'Si usted no solicitó este cambio, por favor ignore este correo electrónico.\n\n'
                'Gracias,\n'
                'El equipo de soporte de Eventify'
            )

            send_mail(
                email_subject,
                email_body,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return render(request, 'data/success.html')  # Redirige a una página de éxito
    else:
        form = EmailForm()
    return render(request, 'data/email_form.html', {'form': form})

def success_view(request):
    return render(request, 'data/success.html')

def reset_password_view(request):
    token = request.GET.get('token')
    usuario = get_object_or_404(Usuario, token=token)

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            usuario.password = make_password(new_password)
            usuario.save()
            return render(request, 'data/password_reset_success.html')  
    else:
        form = PasswordResetForm()

    return render(request, 'data/reset_password.html', {'form': form, 'token': token})