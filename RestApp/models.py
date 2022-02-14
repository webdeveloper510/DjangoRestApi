from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.


class Company(models.Model):
    Name = models.CharField(max_length=100, default='')
    Contact = models.CharField(max_length=100, default='')
    Email = models.CharField(max_length=100)
    Active = models.CharField(max_length=1, choices=(
        ('A', 'Active'), ('I', 'Inactive')))

    def __str__(self):
        return f"{self.Name}"


class User(models.Model):
    uui = models.CharField(max_length=50, blank=True,unique=True, default=uuid.uuid4)
    username = models.CharField(max_length=100, default='')
    email = models.CharField(max_length=100, default='')
    password = models.CharField(max_length=100, default='')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True)
    Active = models.CharField(max_length=1, choices=(
        ('A', 'Active'), ('I', 'Inactive')), default='')

    def __str__(self):
        return f"{self.username}"


class AddTeam(models.Model):

    TeamName = models.CharField(max_length=100, default='')
    ShorName = models.CharField(max_length=100, default='')

    def __str__(self):
        return f"{self.TeamName}"


class Project(models.Model):
    project_name = models.CharField(max_length=100)
    project_desc = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.project_name}"


class MasterList(models.Model):
    Year = models.CharField(max_length=100, default='')
    PickType = models.CharField(max_length=100, default='')
    Original_Owner = models.ForeignKey(
        AddTeam, on_delete=models.CASCADE, default='', blank=True)
    Current_Owner = models.ForeignKey(
        AddTeam, related_name='%(class)s_requests_created', on_delete=models.CASCADE, blank=True)
    Most_Recent_Owner = models.ForeignKey(
        AddTeam, related_name='Most_Recent_Owner', on_delete=models.CASCADE, blank=True)
    Draft_Round = models.CharField(max_length=100, default='')
    Pick_Group = models.CharField(max_length=100, default='')


class LocalLadder(models.Model):
    position = models.CharField(max_length=100, default='')
    season = models.CharField(max_length=100, default='')
    teamname = models.ForeignKey(AddTeam, on_delete=models.CASCADE, blank=True)


class Transactions(models.Model):
    Transaction_Number = models.IntegerField()
    Transaction_DateTime = models.DateTimeField(auto_now_add=True)
    Transaction_Type = models.CharField(max_length=100, default='')
    Transaction_Details = models.CharField(max_length=100, default='')
    Transaction_Description = models.CharField(max_length=100, default='')
