# Generated by Django 3.1.8 on 2022-02-24 21:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0008_auto_20220225_0323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterlist',
            name='Previous_Owner',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Previous_Owner', to='RestApp.teams'),
        ),
    ]
