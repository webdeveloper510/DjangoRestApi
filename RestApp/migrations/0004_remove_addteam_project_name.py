# Generated by Django 3.1.8 on 2022-02-21 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0003_auto_20220221_2214'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addteam',
            name='project_name',
        ),
    ]
