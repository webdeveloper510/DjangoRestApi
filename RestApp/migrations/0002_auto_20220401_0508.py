# Generated by Django 3.1.7 on 2022-03-31 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='Transaction_Details',
            field=models.TextField(),
        ),
    ]