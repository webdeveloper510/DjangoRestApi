from charset_normalizer import models
from django import forms
from .models import User

class UserForm(forms.Form):
    models = User
    fields = '__all__'