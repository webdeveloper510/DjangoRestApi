# Generated by Django 4.0.5 on 2022-07-01 20:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0009_alter_addtrade_id_alter_addtradev2_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterlist',
            name='Previous_Owner',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, related_name='Previous_Owner', to='RestApp.teams'),
        ),
    ]