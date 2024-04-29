# Generated by Django 3.2.25 on 2024-04-22 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0009_alter_evento_fecha'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evento',
            name='id_anfitrion',
        ),
        migrations.AddField(
            model_name='evento',
            name='usuario_anfitrion',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='data.usuario'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Anfitrion',
        ),
    ]
