# Generated by Django 3.1.7 on 2022-03-14 21:40

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(default='', max_length=100)),
                ('Contact', models.CharField(default='', max_length=100)),
                ('Email', models.CharField(max_length=100)),
                ('Active', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive')], default='', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='library_AFL_Draft_Points',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PicksType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickType', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Players',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('FirstName', models.CharField(default='', max_length=100)),
                ('LastName', models.CharField(default='', max_length=100)),
                ('Height', models.CharField(default='', max_length=100)),
                ('width', models.CharField(default='', max_length=100)),
                ('club', models.CharField(default='', max_length=100)),
                ('State', models.CharField(default='', max_length=100)),
                ('Position_1', models.CharField(default='', max_length=100)),
                ('Position_2', models.CharField(default='', max_length=100)),
                ('Rank', models.CharField(default='', max_length=100)),
                ('Tier', models.CharField(default='', max_length=100)),
                ('Notes', models.CharField(default='', max_length=100)),
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
            name='Teams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TeamNames', models.CharField(default='', max_length=100)),
                ('ShortName', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Transaction_Number', models.CharField(default='', max_length=100)),
                ('Transaction_DateTime', models.CharField(default='', max_length=100)),
                ('Transaction_Type', models.CharField(default='', max_length=500)),
                ('Transaction_Details', models.CharField(default='', max_length=500)),
                ('Transaction_Description', models.CharField(default='', max_length=500)),
                ('projectId', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uui', models.CharField(blank=True, default=uuid.uuid4, max_length=50, unique=True)),
                ('username', models.CharField(default='', max_length=100)),
                ('email', models.CharField(default='', max_length=100)),
                ('password', models.CharField(default='', max_length=100)),
                ('Active', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive')], default='', max_length=1)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.company')),
            ],
        ),
        migrations.CreateModel(
            name='MasterList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Year', models.CharField(default='', max_length=100)),
                ('PickType', models.CharField(default='standard', max_length=100)),
                ('Position', models.CharField(default='', max_length=100)),
                ('Draft_Round', models.CharField(default='', max_length=100)),
                ('Pick_Group', models.CharField(default='', max_length=100)),
                ('System_Note', models.CharField(default='', max_length=100)),
                ('User_Note', models.CharField(default='', max_length=100)),
                ('Reason', models.CharField(default='', max_length=100)),
                ('Overall_Pick', models.CharField(default='', max_length=100)),
                ('AFL_Points_Value', models.CharField(default='', max_length=100)),
                ('Unique_Pick_ID', models.CharField(default='', max_length=100)),
                ('Club_Pick_Number', models.CharField(default='', max_length=100)),
                ('Display_Name', models.CharField(default='', max_length=100)),
                ('Display_Name_Detailed', models.CharField(default='', max_length=100)),
                ('Current_Owner', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='Current_Owner', to='RestApp.teams')),
                ('Original_Owner', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='TeamName', to='RestApp.teams')),
                ('Previous_Owner', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Previous_Owner', to='RestApp.teams')),
                ('TeamName', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams')),
                ('projectId', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.project')),
            ],
        ),
        migrations.CreateModel(
            name='LocalLadder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(default='', max_length=100)),
                ('season', models.CharField(default='', max_length=100)),
                ('projectId', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.project')),
                ('teamname', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams')),
            ],
        ),
        migrations.CreateModel(
            name='DraftAnalyserTrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TradePartner', models.CharField(default='', max_length=100)),
                ('TotalPicks', models.CharField(default='', max_length=100)),
                ('TotalPLayers', models.CharField(default='', max_length=100)),
                ('PickTradingIn', models.CharField(default='', max_length=100)),
                ('PlayerTradingIn', models.CharField(default='', max_length=100)),
                ('TradeNotes', models.TextField(default='', max_length=200)),
                ('PlayerName', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.players')),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='projectId',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.project'),
        ),
        migrations.CreateModel(
            name='AddTradev2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projectid', models.IntegerField()),
                ('Team1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams')),
                ('Team1_Pick1_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1', to='RestApp.masterlist')),
                ('Team1_player_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1_Pick1_no', to='RestApp.masterlist')),
                ('Team2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addtradev2_requests_created', to='RestApp.teams')),
                ('Team2_Pick1_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addtradev2_requests_created', to='RestApp.masterlist')),
                ('Team2_player_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team2_Pick1_no', to='RestApp.masterlist')),
            ],
        ),
        migrations.CreateModel(
            name='AddTrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Team1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams')),
                ('Team1_Pick1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addtrade_requests_created', to='RestApp.masterlist')),
                ('Team1_Pick2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1_Pick1', to='RestApp.masterlist')),
                ('Team1_Pick3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1_Pick2', to='RestApp.masterlist')),
                ('Team2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addtrade_requests_created', to='RestApp.teams')),
                ('Team2_Pick1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1_Pick3', to='RestApp.masterlist')),
                ('Team2_Pick2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team2_Pick1', to='RestApp.masterlist')),
                ('Team2_Pick3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team2_Pick2', to='RestApp.masterlist')),
            ],
        ),
    ]
