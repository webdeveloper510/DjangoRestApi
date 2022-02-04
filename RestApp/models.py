from django.contrib.auth.signals import user_logged_in
from django.db import models

# Create your models here.


class User(models.Model):
    uui = models.CharField(max_length=100,default='')
    username = models.CharField(max_length=100, default='')
    email = models.CharField(max_length=100, default='')
    password = models.CharField(max_length=100, default='')


def login_handler(sender, user, request, **kwargs):
    print('logged in')


user_logged_in.connect(login_handler)


class CreateProject(models.Model):
    project_name = models.CharField(max_length=100)
    project_desc = models.CharField(max_length=200)


class LocalLadder(models.Model):
    position = models.CharField(max_length=100, default='')
    season = models.CharField(max_length=100)
    teamname = models.CharField(max_length=100)
    shortname = models.CharField(max_length=100)


class MasterList(models.Model):
    Year = models.CharField(max_length=100, default='')
    Transaction_Number = models.IntegerField()
    Transaction_DateTime = models.DateTimeField(auto_now_add=True)
    Transaction_Type = models.CharField(max_length=100, default='')
    Transaction_Details = models.CharField(max_length=100, default='')
    Transaction_Description = models.CharField(max_length=100, default='')
