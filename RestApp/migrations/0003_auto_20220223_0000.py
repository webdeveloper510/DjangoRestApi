# Generated by Django 3.1.8 on 2022-02-22 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0002_auto_20220222_2358'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='projectId',
            new_name='project',
        ),
        migrations.RenameField(
            model_name='localladder',
            old_name='project',
            new_name='projectId',
        ),
    ]
