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
    path('login/', views.api_login),
    path('register/',views.api_register),
    path('creation-events-page/',views.inicialize_events_page),
    path('create-new-event/',views.create_new_event),
    path('events/<int:evento_id>/photo/', views.show_photo),
    path('events/nophoto/', views.get_default_photo),
    path('users/get-user-data/', views.get_user_data),
]

