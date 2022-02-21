from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.


class Project(models.Model):
    project_name = models.CharField(max_length=100)
    project_desc = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.project_name}"


class Company(models.Model):
    Name = models.CharField(max_length=100, default='')
    Contact = models.CharField(max_length=100, default='')
    Email = models.CharField(max_length=100)
    Active = models.CharField(max_length=1, choices=(
        ('A', 'Active'), ('I', 'Inactive')),default='')
    project_name = models.ForeignKey(Project, on_delete=models.CASCADE,default='')

    def __str__(self):
        return f"{self.Name}"


class User(models.Model):
    uui = models.CharField(max_length=50, blank=True,
                           unique=True, default=uuid.uuid4)
    username = models.CharField(max_length=100, default='')
    email = models.CharField(max_length=100, default='')
    password = models.CharField(max_length=100, default='')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False)
    Active = models.CharField(max_length=1, choices=(
        ('A', 'Active'), ('I', 'Inactive')), default='')

    def __str__(self):
        return f"{self.username}"


class AddTeam(models.Model):

    TeamName = models.CharField(max_length=100, default='')
    ShortName = models.CharField(max_length=100, default='')

    def __str__(self):
        return f"{self.TeamName}"


class MasterList(models.Model):
    Year = models.CharField(max_length=100, default='')
    PickType = models.CharField(max_length=100, default='')
    Original_Owner = models.ForeignKey(
        AddTeam, on_delete=models.CASCADE, default='', blank=False)
    Current_Owner = models.ForeignKey(
        AddTeam, related_name='%(class)s_requests_created', on_delete=models.CASCADE, blank=False)
    Most_Recent_Owner = models.ForeignKey(
        AddTeam, related_name='Most_Recent_Owner', on_delete=models.CASCADE, blank=False)
    Draft_Round = models.CharField(max_length=100, default='')
    Pick_Group = models.CharField(max_length=100, default='')
    project_name = models.ForeignKey(Project, on_delete=models.CASCADE,default='')


class LocalLadder(models.Model):
    position = models.CharField(max_length=100, default='')
    season = models.CharField(max_length=100, default='')
    teamname = models.ForeignKey(
        AddTeam, on_delete=models.CASCADE, blank=False)
    Project = models.ForeignKey(Project, on_delete=models.CASCADE,default='')


class Transactions(models.Model):
    # Transaction_Number = models.IntegerField()
    Transaction_DateTime = models.DateTimeField(auto_now_add=True)
    Transaction_Type = models.CharField(max_length=100, default='')
    Transaction_Details = models.CharField(max_length=100, default='')
    Transaction_Description = models.CharField(max_length=100, default='')

class Players(models.Model):
    names = models.CharField(max_length=100, default='')
    ratings = models.CharField(max_length=100, default='')
    notes = models.TextField(max_length=100, default='')


class DraftAnalyserTrade(models.Model):
    TradePartner = models.CharField(max_length=100, default="")
    TotalPicks = models.CharField(max_length=100, default="")
    TotalPLayers = models.CharField(max_length=100, default="")
    PlayerName = models.ForeignKey(
        Players, on_delete=models.CASCADE, blank=False)
    PickTradingIn = models.CharField(max_length=100, default="")
    PlayerTradingIn = models.CharField(max_length=100, default="")
    TradeNotes = models.TextField(max_length=200, default="")


# ############################################### Transaction API's #####################################################################


class AddTrade(models.Model):
    Team1 = models.ForeignKey(AddTeam, on_delete=models.CASCADE)
    Team1_Pick1 = models.CharField(max_length=100, default='')
    Team1_Pick2 = models.CharField(max_length=100, default='')
    Team1_Pick3 = models.CharField(max_length=100, default='')
    Team2 = models.ForeignKey(
        AddTeam, related_name='%(class)s_requests_created', on_delete=models.CASCADE)
    Team2_Pick1 = models.CharField(max_length=100, default='')
    Team2_Pick2 = models.CharField(max_length=100, default='')
    Team2_Pick3 = models.CharField(max_length=100, default='')


class PriorityPick(models.Model):
    PriorityTeam = models.ForeignKey(AddTeam, on_delete=models.CASCADE)
    PriorityPickType = models.CharField(max_length=100)
    PriorityAlignedPick = models.CharField(max_length=100, default='')
    PriorityPickInstructions = models.CharField(max_length=100, default='')


class AcademyBid(models.Model):
    AcademyTeam = models.CharField(max_length=100, default='')
    AcademyPickType = models.CharField(max_length=100, default='')
    AcademyBid = models.CharField(max_length=100, default='')


class FA_Compansations(models.Model):
    Fa_Team = models.ForeignKey(AddTeam, on_delete=models.CASCADE)
    Fa_PickType = models.CharField(max_length=100, default='')


class ManualTeam(models.Model):
    ManualTeam = models.CharField(max_length=100, default='')
    ManualRound = models.CharField(max_length=100, default='')
    ManualAlignedPick = models.CharField(max_length=100, default='')
    ManualInstructions = models.CharField(max_length=100, default='')
