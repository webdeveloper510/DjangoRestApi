# Generated by Django 3.1.7 on 2022-04-06 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0007_auto_20220406_0515'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='company',
        ),
        migrations.AddField(
            model_name='user',
            name='Team',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams'),
        ),
    ]
