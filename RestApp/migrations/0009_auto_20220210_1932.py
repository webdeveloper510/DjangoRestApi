# Generated by Django 3.1.7 on 2022-02-10 19:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0008_auto_20220210_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.company'),
        ),
    ]
