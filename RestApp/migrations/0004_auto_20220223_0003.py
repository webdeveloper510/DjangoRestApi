# Generated by Django 3.1.8 on 2022-02-22 18:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0003_auto_20220223_0000'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='project',
            new_name='projectId',
        ),
    ]
