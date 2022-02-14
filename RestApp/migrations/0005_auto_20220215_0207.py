# Generated by Django 3.1.8 on 2022-02-14 20:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0004_auto_20220215_0132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uui',
            field=models.CharField(blank=True, default=uuid.uuid4, max_length=50, unique=True),
        ),
    ]
