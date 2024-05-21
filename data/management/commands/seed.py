from django.core.management.base import BaseCommand
from data.models import *

class Command(BaseCommand):
    help = 'Seed database with initial data'


    def handle(self, *args, **kwargs):
        seed()

def seed():
    intereses = [
    'Juegos', 'Fiesta', 'Música', 'Social', 'Deportes', 'Viajes',
    'Lectura', 'Cocina', 'Fotografía', 'Tecnología', 'Arte',
    'Naturaleza', 'Películas', 'Baile', 'Moda', 'Meditación',
    'Voluntariado', 'Yoga', 'Animales', 'Astronomía'
]

    # Crear o obtener cada interés
    for interes in intereses:
        Interes.objects.get_or_create(nombre=interes)