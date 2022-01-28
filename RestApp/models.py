from django.db import models

# Create your models here.



class User(models.Model):
    username = models.CharField(max_length=100,default='')
    email = models.CharField(max_length=100,default='')
    password = models.CharField(max_length=100,default='')

from django.contrib.auth.signals import user_logged_in

def login_handler(sender, user, request, **kwargs):
    print('logged in')

user_logged_in.connect(login_handler)