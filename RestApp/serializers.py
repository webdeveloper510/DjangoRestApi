from dataclasses import fields
from pyexpat import model
from re import L
from rest_framework import serializers
from .models import (
    Company, User, LocalLadder, Project, MasterList, AddTeam, Transactions, DraftAnalyserTrade,
    AddTrade, AcademyBid, PriorityPick, FA_Compansations, ManualTeam,
    LibraryAFLTeams,PicksType
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


class AddTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddTeam
        fields = '__all__'


class TransactionsSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
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
        model = AddTrade
        fields = '__all__'


class AcademyBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademyBid
        fields = '__all__'


class PriorityPickSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriorityPick
        fields = '__all__'


class ManualTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualTeam
        fields = '__all__'

class FA_CompansationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FA_Compansations
        fields = '__all__'

class LibraryAFLTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryAFLTeams
        fields = '__all__'

class PicksTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PicksType
        fields = '__all__'
