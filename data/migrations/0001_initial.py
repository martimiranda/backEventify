# Generated by Django 3.2.25 on 2024-03-13 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_grupo', models.CharField(max_length=100)),
                ('descripcion_grupo', models.TextField()),
                ('foto_grupo', models.ImageField(blank=True, null=True, upload_to='group_photos/')),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefono', models.CharField(blank=True, max_length=15, null=True)),
                ('nombre_usuario', models.CharField(blank=True, max_length=50, null=True)),
                ('apellido_usuario', models.CharField(blank=True, max_length=50, null=True)),
                ('foto_usuario', models.ImageField(blank=True, null=True, upload_to='user_photos/')),
                ('localizacion_usuario', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Anfitrion',
            fields=[
                ('identidad_usuario', models.CharField(max_length=255)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='data.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioGrupo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.grupo')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pago', models.BooleanField()),
                ('limite_asistentes', models.IntegerField()),
                ('descripcion_evento', models.TextField()),
                ('localizacion_evento', models.CharField(max_length=255)),
                ('foto_evento', models.ImageField(blank=True, null=True, upload_to='event_photos/')),
                ('id_anfitrion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.anfitrion')),
            ],
        ),
    ]
