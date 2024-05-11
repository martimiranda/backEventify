# Generated by Django 5.0.4 on 2024-05-11 14:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0013_auto_20240510_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='notificacionUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.TextField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.usuario')),
            ],
        ),
    ]
