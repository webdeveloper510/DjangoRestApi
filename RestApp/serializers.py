from dataclasses import fields
from pyexpat import model
from re import L
from rest_framework import serializers
from .models import Company, User, LocalLadder, Project, MasterList , AddTeam , Transactions


class UserSerializer(serializers.ModelSerializer):

    date_joined = serializers.ReadOnlyField()

    class Meta(object):
        model = User
        fields = '__all__'


class LocalLaddderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalLadder
        fields = '__all__'


class CreateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class MasterLIstSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterList
        fields = '__all__'


class MakeCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        
        fields = '__all__'

class AddTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddTeam
        fields = '__all__'

class TransactionsSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = '__all__'
