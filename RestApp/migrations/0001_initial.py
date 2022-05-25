# Generated by Django 4.0.4 on 2022-05-24 23:22

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DraftRound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='library_AFL_Draft_Points',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PicksType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickType', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Players',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('FirstName', models.CharField(default='', max_length=100)),
                ('LastName', models.CharField(default='', max_length=100)),
                ('Full_Name', models.CharField(default='', max_length=100)),
                ('Height', models.CharField(default='', max_length=100)),
                ('Weight', models.CharField(default='', max_length=100)),
                ('club', models.CharField(default='', max_length=100)),
                ('State', models.CharField(default='', max_length=100)),
                ('Position_1', models.CharField(default='', max_length=100)),
                ('Position_2', models.CharField(default='', max_length=100)),
                ('Rank', models.CharField(default='', max_length=100)),
                ('Tier', models.CharField(default='', max_length=100)),
                ('Notes', models.CharField(default='', max_length=100)),
                ('projectId', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PriorityTransactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Transaction_Number', models.CharField(default='', max_length=100)),
                ('Transaction_DateTime', models.CharField(default='', max_length=100)),
                ('Transaction_Type', models.CharField(default='', max_length=500)),
                ('Transaction_Details', models.CharField(default='', max_length=500)),
                ('Transaction_Description', models.CharField(default='', max_length=500)),
                ('projectId', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=100)),
                ('project_desc', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TeamNames', models.CharField(default='', max_length=100)),
                ('ShortName', models.CharField(default='', max_length=100)),
                ('Image', models.ImageField(default='', upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='TradePotentialAnalyser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projectid', models.IntegerField()),
                ('Trade_Partner', models.CharField(default='', max_length=255)),
                ('Trading_Out_Num', models.IntegerField()),
                ('Trading_Out_Num_Player', models.IntegerField()),
                ('Trading_In_Num', models.IntegerField()),
                ('Trading_In_Num_Player', models.IntegerField()),
                ('note', models.CharField(default='', max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Trades',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Trade_Partner', models.CharField(default='', max_length=255)),
                ('Trading_Out', models.CharField(default='', max_length=255)),
                ('Trading_In', models.CharField(default='', max_length=255)),
                ('Points_Out', models.CharField(default='', max_length=255)),
                ('Points_In', models.CharField(default='', max_length=255)),
                ('Points_Diff', models.CharField(default='', max_length=255)),
                ('Notes', models.CharField(default='', max_length=255)),
                ('System_Out', models.CharField(default='', max_length=255)),
                ('System_In', models.CharField(default='', max_length=255)),
                ('Warning', models.CharField(default='', max_length=255)),
                ('projectid', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Transaction_Number', models.CharField(default='', max_length=100)),
                ('Transaction_DateTime', models.CharField(default='', max_length=100)),
                ('Transaction_Type', models.CharField(default='', max_length=500)),
                ('Transaction_Details', models.TextField()),
                ('Transaction_Description', models.CharField(default='', max_length=500)),
                ('projectId', models.IntegerField()),
                ('Type', models.CharField(default='  ', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uui', models.CharField(blank=True, default=uuid.uuid4, max_length=50, unique=True)),
                ('username', models.CharField(default='', max_length=100)),
                ('email', models.CharField(default='', max_length=100)),
                ('password', models.CharField(default='', max_length=100)),
                ('Active', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive')], default='', max_length=1)),
                ('Teams', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams')),
            ],
        ),
        migrations.CreateModel(
            name='PriorityPick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(default='', max_length=250)),
                ('pp_insert_instructions', models.CharField(default='', max_length=250)),
                ('round', models.CharField(default='', max_length=250)),
                ('projectid', models.IntegerField()),
                ('Team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams')),
            ],
        ),
        migrations.CreateModel(
            name='MasterList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Year', models.CharField(default='', max_length=100)),
                ('PickType', models.CharField(default='standard', max_length=100)),
                ('Position', models.CharField(default='', max_length=100)),
                ('Draft_Round', models.CharField(default='', max_length=100)),
                ('Draft_Round_Int', models.TextField()),
                ('Pick_Group', models.CharField(default='', max_length=100)),
                ('System_Note', models.TextField()),
                ('User_Note', models.TextField()),
                ('Reason', models.TextField()),
                ('Overall_Pick', models.CharField(default='', max_length=100)),
                ('AFL_Points_Value', models.CharField(default='', max_length=100)),
                ('Unique_Pick_ID', models.CharField(default='', max_length=100)),
                ('Club_Pick_Number', models.CharField(default='', max_length=100)),
                ('Display_Name', models.CharField(default='', max_length=100)),
                ('Display_Name_Short', models.CharField(default='', max_length=100)),
                ('Display_Name_Detailed', models.CharField(default='', max_length=100)),
                ('Display_Name_Mini', models.TextField()),
                ('Current_Owner_Short_Name', models.CharField(default='', max_length=100)),
                ('Pick_Status', models.TextField()),
                ('Selected_Player', models.TextField()),
                ('Current_Owner', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='Current_Owner', to='RestApp.teams')),
                ('Original_Owner', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='TeamName', to='RestApp.teams')),
                ('Previous_Owner', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Previous_Owner', to='RestApp.teams')),
                ('TeamName', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams')),
                ('projectid', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.project')),
            ],
        ),
        migrations.CreateModel(
            name='LocalLadder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(default='', max_length=100)),
                ('season', models.CharField(default='', max_length=100)),
                ('projectId', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.project')),
                ('teamname', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams')),
            ],
        ),
        migrations.CreateModel(
            name='DraftAnalyserTrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TradePartner', models.CharField(default='', max_length=100)),
                ('TotalPicks', models.CharField(default='', max_length=100)),
                ('TotalPLayers', models.CharField(default='', max_length=100)),
                ('PickTradingIn', models.CharField(default='', max_length=100)),
                ('PlayerTradingIn', models.CharField(default='', max_length=100)),
                ('TradeNotes', models.TextField(default='', max_length=200)),
                ('PlayerName', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.players')),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(default='', max_length=100)),
                ('Contact', models.CharField(default='', max_length=100)),
                ('Email', models.CharField(max_length=100)),
                ('Active', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive')], default='', max_length=1)),
                ('projectId', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.project')),
            ],
        ),
        migrations.CreateModel(
            name='AddTradev2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Team1_player_no', models.CharField(default='', max_length=250)),
                ('Team1_Player_Name', models.CharField(default='', max_length=250)),
                ('Team2_player_no', models.CharField(default='', max_length=250)),
                ('Team2_Player_Name', models.CharField(default='', max_length=250)),
                ('projectid', models.IntegerField()),
                ('Team1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams')),
                ('Team1_Pick1_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1', to='RestApp.masterlist')),
                ('Team2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_requests_created', to='RestApp.teams')),
                ('Team2_Pick1_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_requests_created', to='RestApp.masterlist')),
            ],
        ),
        migrations.CreateModel(
            name='AddTrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Team1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.teams')),
                ('Team1_Pick1', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_requests_created', to='RestApp.masterlist')),
                ('Team1_Pick2', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Team1_Pick1', to='RestApp.masterlist')),
                ('Team1_Pick3', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Team1_Pick2', to='RestApp.masterlist')),
                ('Team2', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_requests_created', to='RestApp.teams')),
                ('Team2_Pick1', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Team1_Pick3', to='RestApp.masterlist')),
                ('Team2_Pick2', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Team2_Pick1', to='RestApp.masterlist')),
                ('Team2_Pick3', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Team2_Pick2', to='RestApp.masterlist')),
            ],
        ),
    ]
