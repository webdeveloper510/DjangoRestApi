# Generated by Django 3.1.7 on 2022-02-04 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0010_auto_20220205_0122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uui',
            field=models.CharField(default='', max_length=100),
        ),
    ]
