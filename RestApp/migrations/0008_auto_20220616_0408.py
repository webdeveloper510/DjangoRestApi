# Generated by Django 3.0.1 on 2022-06-15 22:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0007_project_team'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='Team',
            new_name='teamid',
        ),
    ]
