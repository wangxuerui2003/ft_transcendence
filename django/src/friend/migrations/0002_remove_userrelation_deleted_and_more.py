# Generated by Django 5.0.3 on 2024-09-15 02:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friend', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userrelation',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='userrelation',
            name='deleted_at',
        ),
    ]
