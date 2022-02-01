from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from.models import User,LocalLadder,CreateProject


class UserSerializer(serializers.ModelSerializer):

    date_joined = serializers.ReadOnlyField()

    class Meta(object):
        model = User
        fields =  '__all__'


class LocalLaddderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalLadder
        fields = '__all__'


class CreateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateProject
        fields = '__all__'