# Generated by Django 3.1.8 on 2022-02-21 19:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('RestApp', '0006_auto_20220222_0107'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pickstype',
            old_name='CustomFixedPositions',
            new_name='pickType',
        ),
        migrations.RemoveField(
            model_name='pickstype',
            name='FirstRound',
        ),
        migrations.RemoveField(
            model_name='pickstype',
            name='FirstRoundEnd',
        ),
        migrations.RemoveField(
            model_name='pickstype',
            name='SecondRound',
        ),
        migrations.RemoveField(
            model_name='pickstype',
            name='SecondRoundEnd',
        ),
        migrations.RemoveField(
            model_name='pickstype',
            name='StartOfDraft',
        ),
    ]
