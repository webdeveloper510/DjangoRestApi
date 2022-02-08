from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class MakeUser(models.Model):
    uui = models.CharField(max_length=100, default='')
    username = models.CharField(max_length=100, default='')
    email = models.CharField(max_length=100, default='')
    password = models.CharField(max_length=100, default='')
    Active = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.username}"

class MakeCompany(models.Model):
    Name = models.CharField(max_length=100, default='')
    Contact = models.CharField(max_length=100, default='')
    Email = models.CharField(max_length=100)
    Active = models.BooleanField(null=True)


    def __str__(self):
        return f"{self.Name}"


class AddTeam(models.Model):
    TeamName = models.CharField(max_length=100)
    ShortName = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.TeamName}"


class CreateProject(models.Model):
    project_name = models.CharField(max_length=100)
    project_desc = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.project_name}"

class LocalLadder(models.Model):
    position = models.CharField(max_length=100, default='')
    season = models.CharField(max_length=100)
    teamname = models.CharField(max_length=100)


class MasterList(models.Model):
    Year = models.CharField(max_length=100, default='')


class Transactions(models.Model):
    Transaction_Number = models.IntegerField()
    Transaction_DateTime = models.DateTimeField(auto_now_add=True)
    Transaction_Type = models.CharField(max_length=100, default='')
    Transaction_Details = models.CharField(max_length=100, default='')
    Transaction_Description = models.CharField(max_length=100, default='')
