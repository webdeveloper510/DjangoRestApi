# Generated by Django 3.0.1 on 2022-06-15 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0006_auto_20220616_0344'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='Team',
            field=models.CharField(default='', max_length=100),
        ),
    ]