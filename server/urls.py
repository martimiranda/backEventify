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
from data import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('data.urls')),
    path('login/', views.api_login), #LOGEARSE
    path('register/',views.api_register), #REGISTRARSE
    path('creation-events-page/',views.inicialize_events_page), #CARGAR EVENTOS CREADOS POR EL USUARIO
    path('create-new-event/',views.create_new_event), #CREAR UN NUEVO EVENTO
    path('events/<int:evento_id>/photo/', views.show_photo), #OBTENER IMAGEN DE UN EVENTO
    path('events/get-event-data/<int:evento_id>/', views.get_event_data), #OBTENER DATOS DE UN EVENTO 
    path('events/update-event-data/', views.update_event_data), #EDITAR DATOS DE UN EVENTO 
    path('events/delete-event/', views.delete_event), #ELIMINAR EVENTO
    path('events/join-event/', views.join_event), #UNIRSE A EVENTO
    path('events/get-events-locations/', views.get_events_locations), #OBTENER UBICACION DE TODOS LOS EVENTOS
    path('events/show-events-joins/', views.show_events_joins), #OBTENER LOS EVENTOS A LOS QUE SE HA UNIDO EL USUARIO
    path('events/unsuscribe-event/', views.unsuscribe_event), #DESAPUNTARSE DE UN EVENTO
    path('events/admin-unsuscribe-event/', views.admin_unsuscribe_event), #DESAPUNTAR A UN USUARIO DE MI EVENTO
    path('events/show-users-on-event/', views.show_users_on_event), #MOSTRAR USUARIOS QUE SE HAN UNIDO AL EVENTO

    

    path('user/get-user-data/', views.get_user_data), #OBTENER INFORMACION USUARIO (NO IMPLEMENTADA CLIENTE)
    path('user/<int:user_id>/photo/', views.show_photo_user), #OBTENER IMAGEN DE UN USUARIO (NO IMPLEMENTADA CLIENTE)
    path('user/update-interest-user-data/', views.update_interest_user_data), #ACTUALIZAR INTERESES DE UN USUARIO 
    path('user/update-user-bio/', views.update_user_bio), #ACTUALIZAR BIOGRAFIA DE UN USUARIO 
    path('user/update-user-data/', views.update_user_data), #ACTUALIZAR DATOS DE UN USUARIO (NO IMPLEMENTADA CLIENTE)
    path('user/update-user-ubi/',  views.update_user_ubi), #ACTUALIZAR UBICACION DE UN USUARIO (NO IMPLEMENTADA CLIENTE)
    path('user/make-notification/',  views.make_notification), #CREAR UNA NOTIFICACION
    path('user/get-user-notifications/',  views.get_user_notifications), #MOSTRAR NOTIFICACIONES DE UN USUARIO 

    

]

