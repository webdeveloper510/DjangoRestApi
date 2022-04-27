from dataclasses import fields
from pyexpat import model
from re import L
from rest_framework import serializers
from .models import (
    Company, User, LocalLadder,Transactions, Project, MasterList,  DraftAnalyserTrade,
    AddTradev2,
    Teams,PicksType,Players
)


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


class TransactionsSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = '__all__'

class DraftAnalyserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftAnalyserTrade
        fields = '__all__'


class AddTraderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddTradev2
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teams
        fields = '__all__'

class PicksTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PicksType
        fields = '__all__'


class ListImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Teams
        fields = '__all__'
        
        

class PlayersSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Players 
        fields = '__all__'
        
        

