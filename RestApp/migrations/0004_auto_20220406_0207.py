# Generated by Django 3.1.7 on 2022-04-05 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0003_teams_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teams',
            name='Image',
            field=models.ImageField(default='', upload_to=''),
        ),
    ]
