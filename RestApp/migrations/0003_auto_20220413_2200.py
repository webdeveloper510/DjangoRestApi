# Generated by Django 3.1.7 on 2022-04-13 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0002_auto_20220401_0508'),
    ]

    operations = [
        migrations.RenameField(
            model_name='players',
            old_name='width',
            new_name='Full_Name',
        ),
        migrations.AddField(
            model_name='players',
            name='Weight',
            field=models.CharField(default='', max_length=100),
        ),
    ]
