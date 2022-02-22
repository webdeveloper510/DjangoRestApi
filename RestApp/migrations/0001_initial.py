
# Generated by Django 3.1.7 on 2022-02-22 16:53

# Generated by Django 3.1.8 on 2022-02-22 17:50

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
                ('ShortName', models.CharField(default='', max_length=100)),
            ],
        ),
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
            name='LibraryAFLTeams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TeamNames', models.CharField(default='', max_length=100)),
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
            name='Transactions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('uui', models.CharField(blank=True, default=uuid.uuid4, max_length=50, unique=True)),
                ('username', models.CharField(default='', max_length=100)),
                ('email', models.CharField(default='', max_length=100)),
                ('password', models.CharField(default='', max_length=100)),
                ('Active', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive')], default='', max_length=1)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.company')),
            ],
        ),
        migrations.CreateModel(
            name='PriorityPick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PriorityAlignedPick', models.CharField(default='', max_length=100)),
                ('PriorityPickInstructions', models.CharField(default='', max_length=100)),
                ('PriorityPickType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.pickstype')),
                ('PriorityTeam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.libraryaflteams')),
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
                ('Current_Owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='masterlist_requests_created', to='RestApp.addteam')),
                ('Most_Recent_Owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Most_Recent_Owner', to='RestApp.addteam')),
                ('Original_Owner', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.addteam')),
                ('projectId', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.project')),
            ],
        ),
        migrations.CreateModel(
            name='ManualTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ManualRound', models.CharField(default='', max_length=100)),
                ('ManualAlignedPick', models.CharField(default='', max_length=100)),
                ('ManualInstructions', models.CharField(default='', max_length=100)),
                ('ManualTeam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.libraryaflteams')),
            ],
        ),
        migrations.CreateModel(
            name='LocalLadder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(default='', max_length=100)),
                ('season', models.CharField(default='', max_length=100)),
                ('projectId', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='RestApp.project')),
                ('teamname', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.addteam')),
            ],
        ),
        migrations.CreateModel(
            name='FA_Compansations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Fa_PickType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.pickstype')),
                ('Fa_Team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.libraryaflteams')),
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
            name='AddTrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Team1_Pick1', models.CharField(default='', max_length=100)),
                ('Team1_Pick2', models.CharField(default='', max_length=100)),
                ('Team1_Pick3', models.CharField(default='', max_length=100)),
                ('Team2_Pick1', models.CharField(default='', max_length=100)),
                ('Team2_Pick2', models.CharField(default='', max_length=100)),
                ('Team2_Pick3', models.CharField(default='', max_length=100)),
                ('Team1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.libraryaflteams')),
                ('Team2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addtrade_requests_created', to='RestApp.libraryaflteams')),
            ],
        ),
        migrations.CreateModel(
            name='AcademyBid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AcademyBid', models.CharField(default='', max_length=100)),
                ('AcademyPickType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.pickstype')),
                ('AcademyTeam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RestApp.libraryaflteams')),
            ],
        ),
    ]
