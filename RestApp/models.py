from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
import uuid
import datetime
import pandas as pd
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
    Active = models.CharField(max_length=1, choices=(('A', 'Active'), ('I', 'Inactive')), default='')
    projectId = models.ForeignKey(Project, on_delete=models.CASCADE, default='')

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



class Teams(models.Model):
    TeamNames = models.CharField(max_length=100, default='')
    ShortName = models.CharField(max_length=100,default='')

    def __str__(self):
        return f"{self.TeamNames}"


class MasterList(models.Model):

    Year = models.CharField(max_length=100, default='')
    PickType = models.CharField(max_length=100, default='standard')
    TeamName = models.ForeignKey(Teams,on_delete=models.CASCADE)
    Position = models.CharField(max_length=100,default='')
    Original_Owner = models.ForeignKey(Teams, related_name='TeamName', on_delete=models.CASCADE, default='', blank=False)
    Current_Owner = models.ForeignKey( Teams, related_name='Current_Owner', on_delete=models.CASCADE,default='', blank=False)
    Previous_Owner = models.ForeignKey(Teams, related_name='Previous_Owner', on_delete=models.CASCADE,default=None, blank=True,null=True)
    Draft_Round = models.CharField(max_length=100, default='')
    Pick_Group = models.CharField(max_length=100, default='')
    System_Note = models.CharField(max_length=100, default='')
    User_Note = models.CharField(max_length=100, default='')
    Reason = models.CharField(max_length=100, default='')
    Overall_Pick = models.CharField(max_length=100, default='')
    AFL_Points_Value = models.CharField(max_length=100, default='')
    Unique_Pick_ID = models.CharField(max_length=100, default='')
    Club_Pick_Number = models.CharField(max_length=100, default='')
    Display_Name = models.CharField(max_length=100,default='')
    Display_Name_Detailed = models.CharField(max_length=100,default='')
    projectId  = models.ForeignKey(Project, on_delete=models.CASCADE, default='')

class library_AFL_Draft_Points(models.Model):
    points = models.CharField(max_length=100,default='')

    def __str__(self):
        return f"{self.points}"

class LocalLadder(models.Model):
    position = models.CharField(max_length=100, default='')
    season = models.CharField(max_length=100, default='')
    teamname = models.ForeignKey(
        Teams, on_delete=models.CASCADE, blank=False)
    projectId  = models.ForeignKey(Project, on_delete=models.CASCADE, default='')


class Transactions(models.Model):
    # Transaction_Number = models.IntegerField()
    Transaction_DateTime = models.DateTimeField(auto_now_add=True)
    Transaction_Type = models.CharField(max_length=100, default='')
    Transaction_Details = models.CharField(max_length=100, default='')
    Transaction_Description = models.CharField(max_length=100, default='')


class Players(models.Model):
    FirstName = models.CharField(max_length=100, default='')
    LastName = models.CharField(max_length=100, default='')
    Height = models.CharField(max_length=100, default='')
    width = models.CharField(max_length=100, default='')
    club = models.CharField(max_length=100, default='')
    State = models.CharField(max_length=100, default='')
    Position_1 = models.CharField(max_length=100, default='')
    Position_2 = models.CharField(max_length=100, default='')
    Rank = models.CharField(max_length=100, default='')
    Tier = models.CharField(max_length=100, default='')
    Notes = models.CharField(max_length=100, default='')


class DraftAnalyserTrade(models.Model):
    TradePartner = models.CharField(max_length=100, default="")
    TotalPicks = models.CharField(max_length=100, default="")
    TotalPLayers = models.CharField(max_length=100, default="")
    PlayerName = models.ForeignKey(
        Players, on_delete=models.CASCADE, blank=False)
    PickTradingIn = models.CharField(max_length=100, default="")
    PlayerTradingIn = models.CharField(max_length=100, default="")
    TradeNotes = models.TextField(max_length=200, default="")


class PicksType(models.Model):
    pickType = models.CharField(max_length=100, default='')

    def __str__(self):
        return f"{self.pickType}"



# ############################################### Transaction API's #####################################################################

class AddTrade(models.Model):
    Team1 = models.ForeignKey(Teams, on_delete=models.CASCADE)
    Team1_Pick1 = models.ForeignKey(MasterList,on_delete=models.CASCADE,related_name='%(class)s_requests_created')
    Team1_Pick2 = models.ForeignKey(MasterList,on_delete=models.CASCADE,related_name='Team1_Pick1')
    Team1_Pick3 = models.ForeignKey(MasterList,on_delete=models.CASCADE,related_name='Team1_Pick2')
    Team2 = models.ForeignKey(Teams, related_name='%(class)s_requests_created', on_delete=models.CASCADE)
    Team2_Pick1 = models.ForeignKey(MasterList,on_delete=models.CASCADE,related_name='Team1_Pick3')
    Team2_Pick2 = models.ForeignKey(MasterList,on_delete=models.CASCADE,related_name='Team2_Pick1')
    Team2_Pick3 = models.ForeignKey(MasterList,on_delete=models.CASCADE,related_name='Team2_Pick2')


