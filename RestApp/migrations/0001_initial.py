# Generated by Django 3.1.8 on 2022-02-14 19:46

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AddTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TeamName', models.CharField(default='', max_length=100)),
                ('ShorName', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(default='', max_length=100)),
                ('Contact', models.CharField(default='', max_length=100)),
                ('Email', models.CharField(max_length=100)),
                ('Active', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=100)),
                ('project_desc', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Transaction_Number', models.IntegerField()),
                ('Transaction_DateTime', models.DateTimeField(auto_now_add=True)),
                ('Transaction_Type', models.CharField(default='', max_length=100)),
                ('Transaction_Details', models.CharField(default='', max_length=100)),
                ('Transaction_Description', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uui', models.CharField(blank=True, default=uuid.uuid4, max_length=100, unique=True)),
                ('username', models.CharField(default='', max_length=100)),
                ('email', models.CharField(default='', max_length=100)),
                ('password', models.CharField(default='', max_length=100)),
                ('Active', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive')], default='', max_length=1)),
                ('company', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='RestApp.company')),
            ],
        ),
        migrations.CreateModel(
            name='MasterList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Year', models.CharField(default='', max_length=100)),
                ('PickType', models.CharField(default='', max_length=100)),
                ('Draft_Round', models.CharField(default='', max_length=100)),
                ('Pick_Group', models.CharField(default='', max_length=100)),
                ('Current_Owner', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='masterlist_requests_created', to='RestApp.addteam')),
                ('Most_Recent_Owner', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='Most_Recent_Owner', to='RestApp.addteam')),
                ('Original_Owner', models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.addteam')),
            ],
        ),
        migrations.CreateModel(
            name='LocalLadder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(default='', max_length=100)),
                ('season', models.CharField(default='', max_length=100)),
                ('teamname', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='RestApp.addteam')),
            ],
        ),
    ]
