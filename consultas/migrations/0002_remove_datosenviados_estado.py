# Generated by Django 5.1.4 on 2025-01-08 00:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('consultas', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datosenviados',
            name='estado',
        ),
    ]