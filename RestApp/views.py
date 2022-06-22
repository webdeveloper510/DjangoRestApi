from array import array
from ast import Add, Break
from dataclasses import replace
from distutils.command.config import dump_file
from doctest import master
from http.client import CONTINUE
# from locale import D_FMT
# from locale import D_T_FMT
from logging import raiseExceptions
from optparse import Values
from re import M, T
# from socket import MSG_EOR
from tabnanny import verbose
from telnetlib import TELNET_PORT
from urllib import response
from MySQLdb import DateFromTicks
from django.http import Http404, HttpResponse
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from RestApi.settings import SECRET_KEY
from .serializers import (
    LocalLaddderSerializer,
    CreateProjectSerializer,
    MakeCompanySerializer,
    MasterLIstSerializer,
    TransactionsSerialzer,
    DraftAnalyserSerializer,
    # AddTraderSerializer,
    UserSerializer,
    TeamSerializer,
    ListImageSerializer,
    PlayersSerializer
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import jwt
from django.conf import settings
from .models import (
    AddTradev2,
    MasterList,
    LocalLadder,
    Players,
    Project,
    User,
    Company,
    Teams,
    PicksType,
    library_AFL_Draft_Points,
    Transactions,
    PriorityPick,
    DraftRound,
    PriorityTransactions,
    TradePotentialAnalyser,
    Trades,
    Update_ladder_teams

)
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
import pandas as pd
import uuid
from datetime import date
import numpy as np
import math
import pytz
import datetime
from django.db import connection
from django.core.files import File
from django.db import connection
import sys
import ast
import jwt
import pulp as plp
import requests

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 500)

#########################################  POST Requests ###############################################################

unique_id = uuid.uuid4().hex[:6].upper()
loggin_userid = ''


class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    @api_view(['POST'])
    @permission_classes([AllowAny, ])
    def post(request):
        C_Name = Company.objects.filter().values('id', 'Name')
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        last_inserted_id = serializer.data['id']

        User.objects.filter(id=last_inserted_id).update(uui=unique_id)
        return Response({'success': 'User Created Successfuly'}, status=status.HTTP_201_CREATED)


def dataframerequest(request, pk):
    list = []
    df_re = MasterList.objects.filter(projectid=pk).values()
    for df_val in df_re:
        list.append(df_val)
    df = pd.DataFrame(list)
    # #### rename column names because database is returning columns fields with id concatenated
    df.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)
    df.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    df.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    df.rename(columns={'Previous_Owner_id': 'Previous_Owner'}, inplace=True)
    return df


def playerdataframe(request, pk):
    player_list = []
    player_val = Players.objects.filter(projectId=pk).values()
    for k in player_val:
        player_list.append(k)
    players = pd.DataFrame(player_list)
    return players


def transactionsdataframe(request, pk):
    append_list = []
    _transactions_val = Transactions.objects.filter(projectId=pk).values()
    for k in _transactions_val:
        append_list.append(k)
    transactions = pd.DataFrame(append_list)
    return transactions


def tradesdataframe(request, pk):
    append_trade = []
    trade_res = Trades.objects.filter(projectid=pk).values()
    for k in trade_res:
        append_trade.append(k)
    trades = pd.DataFrame(append_trade)
    return trades


@api_view(['GET'])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):

    try:
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email, password=password)
        if user:
            request.session['userId'] = user[0].id
            try:
                token = jwt.encode({'unique_Id': user[0].uui}, SECRET_KEY)
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                user_details = {}
                user_details['username'] = user[0].username
                user_details['userid'] = user[0].id
                user_details['token'] = token
                return Response(user_details, status=status.HTTP_200_OK)

            except Exception as e:
                raise e
        else:
            res = {
                'error': 'can not authenticate with the given credentials or the account has been deactivated'
            }
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'error': 'please provide a email and a password'}
        return Response(res)


@api_view(['POST'])
@csrf_exempt
def LocalLadderRequest(request):
    LocalLadder = request.data
    serializer = LocalLaddderSerializer(data=LocalLadder)
    serializer.is_valid(raise_exception=True)
    fk = serializer.data['teamname']
    TeamNames = Teams.objects.filter(id=fk).values('TeamNames')
    NamesDict = {
        "Names": TeamNames
    }
    fk = serializer.data['projectId']
    ProjectId = Project.objects.filter(id=fk).values('id', 'project_name')
    print(ProjectId)
    return Response({'success': 'LocalLadder Created Successfuly', 'data': serializer.data, "NamesDict": NamesDict, 'Projectid': ProjectId}, status=status.HTTP_201_CREATED)


def update_masterlist(df):
    library_AFL_Draft_Pointss = []
    library_AFL_Team_Names = []

    Team = Teams.objects.filter().values('id', 'TeamNames', 'ShortName')
    for teamdata in Team:
        library_AFL_Team_Names.append(teamdata['id'])

    PointsQueryset = library_AFL_Draft_Points.objects.filter().values('points')

    for pointss in list(PointsQueryset):

        library_AFL_Draft_Pointss.append(pointss['points'])

    # df.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    # df.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    # df.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)
    # df.rename(columns={'Previous_Owner_id': 'Previous_Owner'}, inplace=True)

    df['Overall_Pick'] = df.groupby('Year').cumcount() + 1

    ss = enumerate(library_AFL_Draft_Pointss)
    library_AFL_Draf = dict(ss)
    df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draf)

    df['Unique_Pick_ID'] = df['Year'].astype(str) + '-' + df['Draft_Round'].astype(str) \
        + '-' + df['PickType'].astype(str) + '-' + \
        df['Original_Owner'].astype(str)

    df['Club_Pick_Number'] = df.groupby(
        ['Year', 'Current_Owner']).cumcount() + 1
    df['Display_Name'] = df['Current_Owner']
    df['Display_Name_Detailed'] = df['Current_Owner']

    return df


def CreateMasterListRequest(request, pk):

    current_date = date.today()
    v_current_year = current_date.year
    v_current_year_plus1 = current_date.year+1
    Teamlist = list()
    Shortteamlist = dict()
    Team = Teams.objects.filter().values('id', 'TeamNames', 'ShortName')
    for teamdata in Team:
        Teamlist.append(teamdata['id'])
    ladder_current_year, ladder_current_year_plus1 = import_ladder_dragdrop(
        Teamlist, Shortteamlist, v_current_year, v_current_year_plus1)

    masterlistthisyearimport = ladder_current_year
    masterlistthisyearimport['Year'] = v_current_year
    masterlistnextyearimport = ladder_current_year_plus1
    masterlistnextyearimport['Year'] = v_current_year_plus1

    masterlistthisyear = masterlistthisyearimport.copy()
    masterlistnextyear = masterlistnextyearimport.copy()

    for i in range(9):
        masterlistthisyear = pd.concat(
            [masterlistthisyear, masterlistthisyearimport])
        masterlistnextyear = pd.concat(
            [masterlistnextyear, masterlistnextyearimport])
    df = pd.concat([masterlistthisyear, masterlistnextyear],
                   ignore_index=True, axis=0)
    pkkkk = MasterList.objects.filter(projectid=pk).first()
    if pkkkk is None:

        try:
            df['PickType'] = 'Standard'
            df['Original_Owner'] = df['TeamName']
            df['Current_Owner'] = df['TeamName']
            df['Previous_Owner'] = None
            df['Draft_Round'] = 'RD' + \
                (df.groupby(['Year', 'Current_Owner']
                            ).cumcount() + 1).astype(str)
            df['Draft_Round_Int'] = (df.groupby(
                ['Year', 'Current_Owner']).cumcount() + 1).astype(int)

            df['Pick_Group'] = df['Year'].astype(
                str) + '-' + df['Draft_Round'].astype(str) + '-' + df['PickType'].astype(str)
            df['System_Note'] = ''
            df['User_Note'] = ''
            df['Reason'] = ''
            df['Pick_Status'] = ''
            df['Selected_Player'] = ''
            df['projectid'] = pk

            udpatedf = update_masterlist(df)

            for index, updaterow in udpatedf.iterrows():
                ShortNames = []
                row1 = dict(updaterow)
                team = Teams.objects.get(id=updaterow.TeamName)
                teamsobj = Teams.objects.filter().values('ShortName')
                for teams_short_list in teamsobj:
                    ShortNames.append(teams_short_list['ShortName'])

                Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
                Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
                previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
                Overall_pickk = row1['Overall_Pick']

                Project1 = Project.objects.get(id=updaterow.projectid)

                row1['Previous_Owner_id'] = previous_owner.id
                team = Teams.objects.get(id=updaterow.TeamName)
                row1['TeamName'] = team
                row1['Original_Owner'] = Original_Owner
                row1['Current_Owner'] = Current_Ownerr
                row1['projectid'] = Project1
                # row1['Overall_Pick'] = *Overall_pickk

                row1['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
                    None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

                row1['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
                    updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(team.TeamNames)

                row1['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
                    None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
                    ' ' + str(Overall_pickk)

                row1['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
                    previous_owner + team.ShortName + \
                    ')' if Original_Owner != Current_Ownerr else team.ShortName

                row1['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
                    previous_owner + team.ShortName + \
                    ')' if Original_Owner != Current_Ownerr else team.ShortName

                MasterList(**row1).save()

            return Response({'success': 'MasterList Created Successfuly', 'data': df}, status=status.HTTP_201_CREATED)

        except Exception as e:

            raise e

    else:
        return Response({'error': 'Masterlist with same project is already exist'}, status=status.HTTP_208_ALREADY_REPORTED)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def Create_Project(request):
    Projectdata = request.data
    serializer = CreateProjectSerializer(data=Projectdata)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    pk = Project.objects.latest('id').id
    CreateMasterListRequest(request, pk)
    return Response({'success': 'Project Created Successfuly', 'data': serializer.data}, status=status.HTTP_201_CREATED)


def import_ladder_dragdrop(library_team_dropdown_list, library_AFL_Team_Names, v_current_year, v_current_year_plus1):

    ladder_current_year = pd.DataFrame(
        library_team_dropdown_list, columns=['TeamName'])

    ladder_current_year['Position'] = np.arange(len(ladder_current_year)) + 1

    ladder_current_year['Year'] = v_current_year

    ladder_current_year = ladder_current_year[['TeamName', 'Year', 'Position']]

    ladder_current_year_plus1 = ladder_current_year.copy()

    return ladder_current_year, ladder_current_year_plus1


def import_ladder_dragdrop_V2(ladder_list_current_yr, ladder_list_current_yr_plus1, library_AFL_Team_Names, v_current_year, v_current_year_plus1):
    #### Create ladder for the current year ####
    ladder_current_year = pd.DataFrame(
        ladder_list_current_yr, columns=['TeamName'])
    # Assuming ladder position is set from highest ladder position to lowest ladder position:
    ladder_current_year['Position'] = (
        (np.arange(len(ladder_current_year)) + 1) - 19)*-1
    # Sort by position:
    ladder_current_year = ladder_current_year.sort_values(
        by='Position', ascending=True)
    # Add Short Name:
    # Add Season
    ladder_current_year['Year'] = v_current_year
    # Reorder DF
    ladder_current_year = ladder_current_year[['Position', 'Year', 'TeamName']]

    #### Create ladder for the next year ####
    ladder_current_year_plus1 = pd.DataFrame(
        ladder_list_current_yr_plus1, columns=['TeamName_id'])
    # Add position:
    ladder_current_year_plus1['Position'] = (
        (np.arange(len(ladder_current_year)) + 1) - 19)*-1
    # Sort by position:
    ladder_current_year_plus1 = ladder_current_year_plus1.sort_values(
        by='Position', ascending=True)
    # Add Short Name:
    # Add Season
    ladder_current_year_plus1['Year'] = v_current_year_plus1
    # Reorder DF
    ladder_current_year_plus1 = ladder_current_year[[
        'Position', 'Year', 'TeamName']]

    # Return the two ladders
    return ladder_current_year, ladder_current_year_plus1


@api_view(['POST'])
@permission_classes([AllowAny, ])
def AddTradeRequest(request):

    team1_trades = []
    team2_trades = []

    data = request.data

    Teamobj = Teams.objects.filter(id=data['Team1']).values('id', 'TeamNames')
    team1 = Teamobj[0]['id']

    teamNames = Teamobj[0]['TeamNames']

    team1_pick1_obj = MasterList.objects.filter(
        id=data['team1_pick1']).values('Display_Name_Detailed')
    team1_pick1 = team1_pick1_obj[0]['Display_Name_Detailed']
    team1_pick1Id = team1_pick1_obj[0]['Display_Name_Detailed']
    team1_trades.append(team1_pick1)

    team1_pick2_obj = MasterList.objects.filter(
        id=data['team1_pick2']).values('id', 'Display_Name_Detailed')
    team1_pick2 = team1_pick2_obj[0]['Display_Name_Detailed']
    team1pick2Id = team1_pick2_obj[0]['id']

    team1_pick3_obj = MasterList.objects.filter(
        id=data['team1_pick3']).values('id', 'Display_Name_Detailed')
    team1_pick3 = team1_pick3_obj[0]['Display_Name_Detailed']
    team1_pick3Id = team1_pick3_obj[0]['id']

    Team2obj = Teams.objects.filter(id=data['Team2']).values('id', 'TeamNames')

    team2 = Team2obj[0]['id']
    team2name = Team2obj[0]['TeamNames']

    team2_pick1_obj = MasterList.objects.filter(id=data['team2_pick1']).values(
        'id', 'Display_Name_Detailed', 'Current_Owner')
    team2_pick1 = team2_pick1_obj[0]['Display_Name_Detailed']
    team2_trades.append(team2_pick1)
    team2pick1Id = team2_pick1_obj[0]['id']

    team2_pick2_obj = MasterList.objects.filter(
        id=data['team2_pick2']).values('id', 'Display_Name_Detailed')
    team2_pick2 = team2_pick2_obj[0]['Display_Name_Detailed']
    team2pick2Id = team2_pick2_obj[0]['id']

    team2_pick3_obj = MasterList.objects.filter(
        id=data['team2_pick3']).values('id', 'Display_Name_Detailed')
    team2_pick3 = team2_pick3_obj[0]['Display_Name_Detailed']
    team2_pick3Id = team2_pick3_obj[0]['id']

    MasterList.objects.filter(id=team2pick1Id).update(
        Previous_Owner=team2pick1Id)
    MasterList.objects.filter(id=team2pick1Id).update(Previous_Owner=team1)

    if len(team2_pick2) > 2:
        team1_trades.append(team1_pick2)
        MasterList.objects.filter(pk=team2pick2Id).update(
            Previous_Owner=team2pick2Id)
        MasterList.objects.filter(pk=team2pick2Id).update(Current_Owner=team1)

    else:
        pass

    if team2_pick3Id > 2:
        team1_trades.append(team2_pick3)
        MasterList.objects.filter(pk=team2_pick3Id).update(
            Previous_Owner=team2_pick3Id)
        MasterList.objects.filter(pk=team2_pick3Id).update(Current_Owner=team1)

    else:
        pass

    MasterList.objects.filter(pk=team2_pick3Id).update(
        Previous_Owner=team2_pick3Id)
    MasterList.objects.filter(pk=team2_pick3Id).update(Current_Owner=team2)

    if len(team1_pick2) > 2:
        team2_trades.append(team2_pick2)
        MasterList.objects.filter(pk=team1pick2Id).update(
            Previous_Owner=team1pick2Id)
        MasterList.objects.filter(pk=team1pick2Id).update(Current_Owner=team2)
    else:
        pass

    if len(team1_pick3) > 2:
        team2_trades.append(team1_pick3)
        MasterList.objects.filter(pk=team1_pick3Id).update(
            Previous_Owner=team1_pick3Id)
        MasterList.objects.filter(pk=team1_pick3Id).update(Current_Owner=team2)

    else:
        pass

    projectIdd = MasterList.objects.filter(
        id__in=[team1, team2]).values('projectId')
    pId = projectIdd[0]['projectId']
    trade_dict = {team1: team1_trades, team2: team2_trades}

    ListinList = list(trade_dict.values())

    TradePicks = ''.join(ListinList[0])

    trade_description = teamNames + ' traded ' + \
        ','.join(str(e) for e in team1_trades) + ' & ' + team2name + \
        ' traded ' + ','.join(str(e) for e in team2_trades)
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')

    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Trade',
        Transaction_Details=TradePicks,
        Transaction_Description=trade_description,
        projectId=pId

    )
    pk = Transactions.objects.latest('id')
    message_count = Transactions.objects.filter().count()
    Transactions.objects.filter(id=pk.id).update(
        Transaction_Number=message_count)

    return Response({'success': 'Trade and Trasactions Created'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def add_trade_v2_request(request, pk):

    # define lists of picks and players traded out:
    # team1 trading out
    df = dataframerequest(request, pk)
    masterlist = df

    team1_trades_picks = []
    team1_trades_players = []

    team2_trades_picks = []
    team2_trades_players = []
    team2_picks = []

    picks_trading_out_team1 = []
    picks_trading_out_team2 = []
    # TEAMS  TRADING OUT ######################## = []
    data = request.data
    team1 = data.get('Team1')
    team2 = data.get('Team2')

    picks_trading_out_team1_obj = data.get('Team1_Pick1')
    picks_trading_out_team1 = picks_trading_out_team1_obj[0]['value']
    # picks_trading_out_team2_obj = data['Team2_Pick2']
    # players_trading_out_team1 = data.get('Team1_players') or ''

    # picks_trading_out_team2 = data.get('Team2_Pick2')
    picks_trading_out_team2_obj = data.get('Team2_Pick2')
    picks_trading_out_team2 = picks_trading_out_team2_obj[0]['value']
    players_trading_out_team2 = data.get('Team2_players') or ''

    team1obj = Teams.objects.get(id=team1)
    team1name = team1obj.TeamNames

    team2obj = Teams.objects.get(id=team2)
    team2name = team2obj.TeamNames

    picks_trading_out_team2 = picks_trading_out_team2
    team2picks = ''
    Masterlistobj = MasterList.objects.filter(
        id=picks_trading_out_team2).values()
    for data in Masterlistobj:
        team2_picks.append(data['Display_Name_Detailed'])
    team2picks = "".join(team2_picks)
    # players_trading_out_team2_no = data['Team2_Players_no']
    picks_trading_out_team1_len = len(str(picks_trading_out_team1))

    players_trading_out_team1_len = len(players_trading_out_team1) or ''

    if picks_trading_out_team1_len:
        team1picks = masterlist[masterlist['Current_Owner']
                                == team1]['Display_Name_Detailed'].tolist()
        for i in range(picks_trading_out_team1_len):
            pick_trading_out_team1 = masterlist[masterlist['id'].astype(int) == int(
                picks_trading_out_team1)]['Display_Name_Detailed'].tolist()
            team1_trades_picks.append(pick_trading_out_team1)
    else:
        pass
    if players_trading_out_team1_len or players_trading_out_team1_len == '':
        for i in range(players_trading_out_team1_len or 0):
            player_trading_out_team1 = Players.objects.filter(
                id__in=[players_trading_out_team1]).values()
            for player_name in player_trading_out_team1:
                team1_trades_players.append(player_name['Full_Name'])
    else:
        pass

    picks_trading_out_team2_len = len(str(picks_trading_out_team2))
    players_trading_out_team2_len = len(players_trading_out_team2) or ''

    if picks_trading_out_team2_len:
        team2picks = masterlist[masterlist['Current_Owner']
                                == team2]['Display_Name_Detailed'].tolist()

        for i in range(picks_trading_out_team2_len):
            pick_trading_out_team2 = masterlist[masterlist['id'].astype(int) == int(
                picks_trading_out_team2)]['Display_Name_Detailed'].tolist()
            team2_trades_picks.append(pick_trading_out_team2)
    else:
        pass

    if players_trading_out_team2_len or players_trading_out_team2_len == '':

        for i in range(players_trading_out_team2_len or 0):

            player_trading_out_team2 = Players.objects.filter(
                id__in=[players_trading_out_team2]).values()

            for player_name in player_trading_out_team2:

                team1_trades_players.append(player_name['Full_Name'])
    else:
        pass

################### TRADE EXECUTION ############################

    # Trade facilitation - Swapping current owner names & Applying Most Recent Owner First:

    ##### Team 1 receiving from Team 2 #####
    # Loop for each pick that team 2 is trading out to team 1:
    for team2pickout in team2_trades_picks:
        # Changing the previous owner name
        masterlist['Previous_Owner'].mask(masterlist['Display_Name_Detailed'].astype(
            str) == str(team2pickout), masterlist['Current_Owner'], inplace=True)
        # Executing change of ownership
        masterlist['Current_Owner'].mask(masterlist['Display_Name_Detailed'].astype(
            str) == str(team2pickout), team1, inplace=True)

    ##### Team 2 receiving from Team 1 #####
    # Loop for each pick that team 1 is trading out to team 2:
    for team1pickout in team1_trades_picks:
        # Changing the previous owner name
        masterlist['Previous_Owner'].mask(masterlist['Display_Name_Detailed'].astype(
            str) == str(team1pickout), masterlist['Current_Owner'], inplace=True)

        # Executing change of ownership
        masterlist['Current_Owner'].mask(masterlist['Display_Name_Detailed'].astype(
            str) == str(team1pickout), team2, inplace=True)

    team1_out = team1_trades_players + team1_trades_picks
    team2_out = team2_trades_players + team2_trades_picks

    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    # Creating a dict of what each team traded out
    trade_dict = {team1name: team1_out, team2name: team2_out}
    trade_dict_full = {team1name: [team1_trades_players, team1_trades_picks], team2: [
        team2_trades_players, team2_trades_picks]}

    trade_description = team1name + ' traded ' + \
        ','.join(str(e) for e in team1_out) + ' & ' + team2name + \
        ' traded ' + ','.join(str(e) for e in team2_out)

    projectIdd = MasterList.objects.filter(
        id__in=[team1, team2]).values('projectid')
    pId = projectIdd[0]['projectid']

    Team_id1 = Teams.objects.get(id=team1)
    Team_id2 = Teams.objects.get(id=team2)
    masterpick1 = MasterList.objects.get(id=picks_trading_out_team1)
    masterpick2 = MasterList.objects.get(
        id=picks_trading_out_team2)

    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Trade',
        Transaction_Details=trade_dict_full,
        Transaction_Description=trade_description,
        projectId=pId
    )

    pk = Transactions.objects.latest('id')
    row_count = Transactions.objects.filter().count()
    Transactions.objects.filter(id=pk.id).update(Transaction_Number=row_count)

    return Response({'success': 'Trade and Trasactions Created'}, status=status.HTTP_201_CREATED)


def call_add_trade(transactions):
    return transactions


# Complete
# Two of the inputs for this functions are styatic lists that i am hoping will be a drag and drop list on the settings page:


def priority_pick_input_v1(request):

    data = request.data
    pp_team_idd = data.get('teamid')
    reason = data.get('reason')
    p_type = data.get('pick_type')
    pp_id = data.get('ppid')
    project_Id = data.get('projectId')
    pp_insert_instructions = data.get('pp_insert_instructions')

    return pp_team_idd, p_type, pp_id, project_Id, pp_insert_instructions, reason


@api_view(['POST'])
@permission_classes([AllowAny])
def PriorityPickrRequest(request):

    current_date = date.today()
    v_current_year = current_date.year

    pp_dict = {}
    pp_aligned_pick = []
    pp_description = []
    pp_round = ''

    pp_team_idd, p_type, pp_id, project_Id, pp_insert_instructions, reason = priority_pick_input_v1(
        request)

    pp_team_obj = Teams.objects.get(id=pp_team_idd)

    pp_team = pp_team_obj.TeamNames
    pp_team_id = pp_team_obj.id
    Pickobj = MasterList.objects.filter(id=pp_id).values()
    pp_aligned_pick = Pickobj[0]['Display_Name_Detailed']

    pp_description = ''
    pp_dict = {}

    # Get dataframe
    df = dataframerequest(request, project_Id)
    df1 = dataframerequest(request, project_Id)

    pp_pick_type_re = PicksType.objects.filter(
        pickType=p_type).values('id', 'pickType')
    pp_pick_type = pp_pick_type_re[0]['pickType']

    if pp_pick_type == 'Start of Draft':

        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD1-Standard')][0]
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team_id), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority',
                             'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id, 'Previous_Owner': pp_team_id,
                             'Draft_Round': 'RD1',
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + pp_pick_type, 'Reason': reason}, index=[rowno])

        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        df = df.iloc[1]
        df['id'] = rowno+1
        df['projectid_id'] = project_Id
        df['Previous_Owner_id'] = None

        MasterList.objects.filter(id=rowno+1).update(**df)
        # Update transactions
        pp_round = 'RD1'
        pp_aligned_pick = ''
        pp_unique_pick = ''
        pp_insert_instructions = ''
        pp_dict[pp_team] = [pp_pick_type, pp_round, reason,
                            pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = pp_team + 'received a ' + pp_pick_type + ' Priority Pick'

    if pp_pick_type == 'First Round':

        rowno = df.index[df['Display_Name_Detailed'] == pp_aligned_pick][0]

        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team_id), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority', 'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id,
                             'Previous_Owner': pp_team_id, 'Draft_Round': pp_round,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + pp_pick_type},
                            index=[rowno])
        if pp_insert_instructions == 'Before':

            df = pd.concat([df.loc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
            df['id'] = rowno
            df['projectid_id'] = project_Id
            df['Previous_Owner'] = None

            MasterList.objects.filter(id=rowno).update(**df)
        else:
            df = pd.concat([df.loc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['projectid_id'] = project_Id
            df['Previous_Owner_id'] = None
            MasterList.objects.filter(id=rowno+1).update(**df)

        pp_unique_pick = df1.loc[df1.Display_Name_Detailed ==
                                 pp_aligned_pick, 'Unique_Pick_ID'].iloc[0]
        pp_dict[pp_team] = [pp_pick_type, pp_round, reason,
                            pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'
    if pp_pick_type == 'End of First Round':

        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD1-Standard')][-1]

        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team_id), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': int(pp_team_id), 'PickType': 'Priority',
                             'Original_Owner': int(pp_team_id), 'Current_Owner': int(pp_team_id), 'Previous_Owner': pp_team_id,
                             'Draft_Round': 'RD1',
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + pp_pick_type}, index=[rowno])

        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno+1]

        df['id'] = rowno
        df['projectid_id'] = project_Id
        # df['Previous_Owner_id'] = None

        MasterList.objects.filter(id=rowno).update(**df)

        pp_round = 'RD1'
        pp_aligned_pick = ''
        pp_unique_pick = ''
        pp_insert_instructions = ''
        pp_dict[pp_team] = [pp_pick_type, pp_round, reason,
                            pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'

        # Update transactions
        pp_round = 'RD1'
        pp_aligned_pick = ''
        pp_unique_pick = ''
        pp_insert_instructions = ''
        pp_dict[pp_team] = [pp_pick_type, pp_round, reason,
                            pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = pp_team + ' received a ' + pp_pick_type + ' Priority Pick'

    if pp_pick_type == 'Start of Second Round':

        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD2-Standard')][0]

        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team_id), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority',
                             'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id, 'Previous_Owner': pp_team_id,
                             'Draft_Round': 'RD2',
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type}, index=[rowno])
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        df = df.iloc[rowno]

        df['id'] = rowno
        df['projectid_id'] = project_Id
        # df['Previous_Owner_id'] = None

        # Update transactions
        pp_round = 'RD2'
        pp_aligned_pick = ''
        pp_unique_pick = ''
        pp_insert_instructions = ''
        pp_dict[pp_team] = [pp_pick_type, pp_round, reason,
                            pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'

        MasterList.objects.filter(id=rowno).update(**df)

    if pp_pick_type == 'Second Round':
        pp_round = 'RD2'
        rowno = df.index[df['Display_Name_Detailed'] == pp_aligned_pick][0]
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team_id), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority', 'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id,
                             'Previous_Owner': pp_team_id, 'Draft_Round': pp_round,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type},
                            index=[rowno])

        if pp_insert_instructions == 'Before':

            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
            df['id'] = rowno
            df['projectid_id'] = project_Id
            # df['Previous_Owner'] = None

            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno]

            df['id'] = rowno+1
            df['projectid_id'] = project_Id
            # df['Previous_Owner_id'] = None

            MasterList.objects.filter(id=rowno+1).update(**df)

        pp_unique_pick = df1.loc[df1.Display_Name_Detailed.astype(
            str) == str(pp_aligned_pick), 'Unique_Pick_ID'].iloc[0]

        pp_dict[pp_team] = [pp_pick_type, pp_round, reason,
                            pp_aligned_pick, pp_unique_pick, pp_insert_instructions]

        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'

    if pp_pick_type == 'End of Second Round':

        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD2-Standard')][-1]
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team_id), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority',
                             'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id, 'Previous_Owner': pp_team_id,
                             'Draft_Round': 'RD2',
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type}, index=[rowno])

        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno+1]

        df['id'] = rowno+1
        df['projectid_id'] = project_Id
        # df['Previous_Owner_id'] = None
        MasterList.objects.filter(id=rowno).update(**df)

        # Update transactions
        pp_round = 'RD2'
        pp_aligned_pick = ''
        pp_unique_pick = ''
        pp_insert_instructions = ''
        pp_dict[pp_team] = [pp_pick_type, pp_round, reason,
                            pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'

    if pp_pick_type == 'Third Round':

        rowno = df.index[df['Display_Name_Detailed'] == pp_aligned_pick][0]

        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team_id), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority', 'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id,
                             'Previous_Owner': pp_team_id, 'Draft_Round': pp_round,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type},
                            index=[rowno])
        if pp_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
            df['id'] = rowno
            df['projectid_id'] = project_Id
            # df['Previous_Owner_id'] = None
            MasterList.objects.filter(id=rowno).update(**df)

            pp_dict = [pp_team] + [pp_pick_type, pp_round,
                                   pp_aligned_pick, pp_insert_instructions]
            pp_description = str(pp_team) + ' received a ' + \
                str(pp_pick_type) + ' Priority Pick'

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno]

            df['id'] = rowno+1
            df['projectid_id'] = project_Id
            # df['Previous_Owner_id'] = None

            MasterList.objects.filter(id=rowno+1).update(**df)
            # Update transactions
        pp_unique_pick = df1.loc[df1.Display_Name_Detailed.astype(
            str) == str(pp_aligned_pick), 'Unique_Pick_ID'].iloc[0]
        pp_dict[pp_team] = [pp_pick_type, pp_round, reason,
                            pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'

    if pp_pick_type == 'Custom Fixed Position':

        # find row number of the aligned pick:
        rowno = df.index[df['Display_Name_Detailed'] == pp_aligned_pick][0]
        # create the line to insert
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team_id), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority', 'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id,
                             'Previous_Owner': pp_team_id, 'Draft_Round': 'RD3',
                             'Pick_Group': str(v_current_year) + '-' + pp_round + '-Priority-' + pp_pick_type},
                            index=[rowno])
        # Execute Insert
        if pp_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
            df['id'] = rowno+1
            df['projectid_id'] = project_Id
            # df['Previous_Owner_id'] = None
            MasterList.objects.filter(id=rowno+1).update(**df)
        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['projectid_id'] = project_Id
            # df['Previous_Owner_id'] = None

            MasterList.objects.filter(id=rowno+1).update(**df)
            # Update Transactions List
        # Update transactions
        pp_unique_pick = df1.loc[df1.Display_Name_Detailed.astype(
            str) == str(pp_aligned_pick), 'Unique_Pick_ID'].iloc[0]
        pp_dict[pp_team] = [pp_pick_type, pp_round, reason,
                            pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'

    df = dataframerequest(request, project_Id)
    udpatedf = update_masterlist(df)
    iincreament_id = 1
    for index, updaterow in udpatedf.iterrows():
        academy_dict = dict(updaterow)

        team = Teams.objects.get(id=updaterow.TeamName)
        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = academy_dict['Overall_Pick']

        Project1 = Project.objects.get(id=project_Id)
        academy_dict['Previous_Owner'] = previous_owner
        team = Teams.objects.get(id=updaterow.TeamName)
        academy_dict['TeamName'] = team
        academy_dict['Original_Owner'] = Original_Owner
        academy_dict['Current_Owner'] = Current_Ownerr
        academy_dict['projectid'] = Project1

        academy_dict['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        academy_dict['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(academy_dict['Display_Name'])

        academy_dict['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        academy_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        academy_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        MasterList.objects.filter(id=iincreament_id).update(**academy_dict)

        iincreament_id += 1

    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    # pp_dict = {}
    # pp_dict[pp_team] = [pp_round, pp_aligned_pick, pp_insert_instructions]
    obj = Project.objects.get(id=project_Id)
    # PriorityTransactions = (
    #     {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Priority_Pick', 'Transaction_Details': pp_dict, 'Transaction_Description': pp_description, 'Type': 'Priority-Pick', 'projectId': obj.id})
    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Priority_Pick',
        Transaction_Details=pp_dict,
        Transaction_Description=pp_description,
        projectId=obj.id
    )
    last_inserted_obj = Transactions.objects.latest('id')
    last_inserted_id = last_inserted_obj.id
    Transactions.objects.filter(id=last_inserted_id).update(
        Transaction_Number=last_inserted_id)

    return Response({'success': 'Priority Pick Created Successfuly'}, status=status.HTTP_201_CREATED)


def call_priority_pick_v2(transactions):
    return transactions


def add_priority_pick_inputs(request, pk):

    # Ask for Priority Pick Team
    data = request.data
    pp_team = data.get('teamid')
    # Ask for Priority Pick Type
    pp_type = data.get('pick_type')
    # Ask for Priority Pick Reason
    reason = data.get('reason')
    Typesobj = PicksType.objects.filter(
        pickType=pp_type).values('id', 'pickType')
    pp_pick_type = Typesobj[0]['pickType']
    df = dataframerequest(request, pk)
    masterlist = df
    # define a blank round & aligned pick as it will either be made here or within function

    pp_aligned_pick = ''
    pp_unique_pick = ''
    pp_insert_instructions = ''

    # ask for extra details depending on pick type:
    if pp_pick_type == 'Custom Fixed Position':

        pp_aligned_pick_id = data.get('pp_aligned_pick_id')
        pp_pick_obj = MasterList.objects.filter(id=pp_aligned_pick_id).values()
        pp_aligned_pick = pp_pick_obj[0]['Display_Name_Detailed']
        pp_insert_instructions = data.get('instructions')
        pp_unique_pick = masterlist.loc[masterlist.Display_Name_Detailed ==
                                        pp_aligned_pick, 'Unique_Pick_ID'].iloc[0]

    if pp_pick_type == 'First Round' or pp_pick_type == 'Second Round' or pp_pick_type == 'Third Round':

        pp_aligned_pick_id = data.get('pp_aligned_pick_id')
        pp_pick_obj = MasterList.objects.filter(id=pp_aligned_pick_id).values()
        pp_aligned_pick = pp_pick_obj[0]['Display_Name_Detailed']
        pp_insert_instructions = data['instructions']

        pp_unique_pick = masterlist.loc[masterlist.Display_Name_Detailed ==
                                        pp_aligned_pick, 'Unique_Pick_ID'].iloc[0]
    return pp_team, masterlist, pp_pick_type, reason, pp_aligned_pick, pp_unique_pick, pp_insert_instructions


@api_view(['POST'])
@permission_classes([AllowAny])
def add_priority_pick_v2(request, pk):

    pp_team, masterlist, pp_pick_type, reason, pp_aligned_pick, pp_unique_pick, pp_insert_instructions = add_priority_pick_inputs(
        request, pk)
    df = masterlist
    current_date = date.today()
    v_current_year = current_date.year

    Teamsobj = Teams.objects.get(id=pp_team)
    teamname = Teamsobj.TeamNames
    if pp_pick_type == 'Start of Draft':
        # Find the first row that is a standard pick:
        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD1-Standard')][0]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team,  'PickType': 'Priority',
                             'Original_Owner': pp_team, 'Current_Owner': pp_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD1', 'Draft_Round_Int': 1,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + pp_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert above the rowno
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        df = df.iloc[rowno]
        df['id'] = rowno+1
        df['projectid_id'] = pk
        MasterList.objects.filter(id=rowno+1).update(**df)
        # Update transactions
        pp_dict = {}
        pp_round = 'RD1'
        pp_aligned_pick = ''
        pp_unique_pick = ''
        pp_insert_instructions = ''
        pp_dict = [pp_team] + [pp_pick_type, pp_round, reason,
                               pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = str(teamname) + ' received a ' + \
            pp_pick_type + ' Priority Pick' + '(' + reason + ')'

    if pp_pick_type == 'First Round':
        # Make the changes to the masterlist:
        rowno = df.index[df['Display_Name_Detailed'] == pp_aligned_pick][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team, 'PickType': 'Priority', 'Original_Owner': pp_team, 'Current_Owner': pp_team,
                             'Previous_Owner': '', 'Draft_Round': 'RD1', 'Draft_Round_Int': 1,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + pp_pick_type, 'Reason': reason},
                            index=[rowno])
        # Execute Insert
        # i.e stacks 3 dataframes on top of each other
        if pp_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
            df['id'] = rowno+1
            df['projectid_id'] = pk
            MasterList.objects.filter(id=rowno+1).update(**df)

        else:

            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['projectid_id'] = pk
            MasterList.objects.filter(id=rowno+1).update(**df)

        # Update transactions
        pp_dict = {}
        pp_round = 'RD1'
        pp_unique_pick = df.loc[df.Display_Name_Detailed ==
                                pp_aligned_pick, 'Unique_Pick_ID'].iloc[0]
        pp_dict = [pp_team] + [pp_pick_type, pp_round, reason,
                               pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = teamname + ' received a ' + \
            pp_pick_type + ' Priority Pick' + '(' + reason + ')'

    if pp_pick_type == 'End of First Round':
        # Find the last row that is a standard pick:
        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD1-Standard')][-1]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team,  'PickType': 'Priority',
                             'Original_Owner': pp_team, 'Current_Owner': pp_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD1', 'Draft_Round_Int': 1,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + pp_pick_type, 'Reason': reason}, index=[rowno])

        # Execute Insert below the rowno
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno+1]
        df['id'] = rowno+1
        df['projectid_id'] = pk
        MasterList.objects.filter(id=rowno+1).update(**df)

        # Update transactions
        pp_dict = {}
        pp_round = 'RD1'
        pp_aligned_pick = ''
        pp_unique_pick = ''
        pp_insert_instructions = ''
        pp_dict['pp_team'] = [pp_pick_type, pp_round, reason,
                              pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = teamname + ' received a ' + \
            pp_pick_type + ' Priority Pick' + '(' + reason + ')'
    if pp_pick_type == 'Start of Second Round':
        # Find the first row that is a standard pick in the 2nd round:
        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD2-Standard')][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team, 'Pick_Type': 'Priority',
                             'Original_Owner': pp_team, 'Current_Owner': pp_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD2', 'Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type, 'Reason': reason}, index=[rowno])

        # Execute Insert above the rowno
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        df = df.iloc[rowno]
        df['id'] = rowno
        df['projectid_id'] = pk
        MasterList.objects.filter(id=rowno+1).update(**df)

    if pp_pick_type == 'Second Round':
        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        rowno = df.index[df['Display_Name_Detailed'] == pp_aligned_pick][0]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team, 'PickType': 'Priority', 'Original_Owner': pp_team, 'Current_Owner': pp_team,
                             'Previous_Owner': '', 'Draft_Round': 'RD2', 'Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type, 'Reason': reason},
                            index=[rowno])
        # Execute Insert
        if pp_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
            df['id'] = rowno
            df['projectid_id'] = pk
            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno = 1
            df['projectid_id'] = pk
        # Update Transactions List
            pp_dict = {}
            pp_round = 'RD2'

            pp_unique_pick = df.loc[df.Display_Name_Detailed.astype(str) ==
                                    pp_aligned_pick, 'Unique_Pick_ID'].iloc[0]
            pp_dict = [pp_team] + [pp_pick_type, pp_round, reason,
                                   pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
            pp_description = str(teamname) + ' received a ' + \
                pp_pick_type + ' Priority Pick' + '(' + reason + ')'
            MasterList.objects.filter(id=rowno).update(**df)

    if pp_pick_type == 'End of Second Round':
        # Find the last row that is a standard pick:
        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD2-Standard')][-1]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team, 'PickType': 'Priority',
                             'Original_Owner': pp_team, 'Current_Owner': pp_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD2', 'Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert below the rowno
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno]
        df['id'] = rowno
        df['projectid_id'] = pk
        MasterList.objects.filter(id=rowno).update(**df)
        # Update transactions
        pp_round = 'RD2'
        pp_aligned_pick = ''
        pp_unique_pick = ''
        pp_insert_instructions = ''
        pp_dict = [teamname] + [pp_pick_type, pp_round, reason,
                                pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
        pp_description = teamname + ' received a ' + \
            pp_pick_type + ' Priority Pick' + '(' + reason + ')'

    if pp_pick_type == 'Third Round':
        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        rowno = df.index[df['Display_Name_Detailed'] == pp_aligned_pick][0]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team, 'PickType': 'Priority', 'Original_Owner': pp_team, 'Current_Owner': pp_team,
                             'Previous_Owner': '', 'Draft_Round': 'RD3', 'Draft_Round_Int': 3,
                             'Pick_Group': str(v_current_year) + '-' + 'RD3-Priority-' + pp_pick_type, 'Reason': reason},
                            index=[rowno])
        # Execute Insert
        if pp_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
            df['id'] = rowno
            df['projectid_id'] = pk
            MasterList.objects.filter(id=rowno).update(**df)
        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['projectid_id'] = pk
        # Update Transactions List
            pp_dict = {}
            pp_round = 'RD3'
            pp_unique_pick = df.loc[df.Display_Name_Detailed.astype(
                str) == pp_aligned_pick, 'Unique_Pick_ID'].iloc[0]
            pp_dict = [pp_team]+[pp_pick_type, pp_round, reason,
                                 pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
            pp_description = str(teamname) + ' received a ' + \
                pp_pick_type + ' Priority Pick' + '(' + reason + ')'
            MasterList.objects.filter(id=rowno+1).update(**df)

    if pp_pick_type == 'Custom Fixed Position':
        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        pp_round = 'RD4'
        rowno = df.index[df['Display_Name_Detailed'] == pp_aligned_pick][0]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(pp_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team,  'PickType': 'Priority', 'Original_Owner': pp_team, 'Current_Owner': pp_team,
                             'Previous_Owner': '', 'Draft_Round': pp_round,
                             'Pick_Group': str(v_current_year) + '-' + pp_round + '-Priority-' + pp_pick_type, 'Reason': reason},
                            index=[rowno])
        # Execute Insert
        if pp_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
            df['id'] = rowno
            df['projectid_id'] = pk
            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['projectid_id'] = pk
        # Update Transactions List
            pp_dict = {}
            pp_unique_pick = df.loc[df.Display_Name_Detailed ==
                                    pp_aligned_pick, 'Unique_Pick_ID'].iloc[0]
            pp_dict = [pp_team] + [pp_pick_type, pp_round, reason,
                                   pp_aligned_pick, pp_unique_pick, pp_insert_instructions]
            pp_description = str(teamname) + ' received a ' + \
                pp_pick_type + ' Priority Pick' + '(' + reason + ')'
            MasterList.objects.filter(id=rowno+1).update(**df)
    df = dataframerequest(request, pk)
    df = update_masterlist(df)
    iincreament_id = 1

    for index, updaterow in df.iterrows():
        pp_dict = dict(updaterow)

        team = Teams.objects.get(id=updaterow.TeamName)

        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = pp_dict['Overall_Pick']

        Project1 = Project.objects.get(id=pk)
        pp_dict['Previous_Owner'] = team
        team = Teams.objects.get(id=updaterow.TeamName)
        pp_dict['TeamName'] = team
        pp_dict['Original_Owner'] = Original_Owner
        pp_dict['Current_Owner'] = Current_Ownerr
        pp_dict['projectid'] = Project1

        pp_dict['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        pp_dict['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(pp_dict['Display_Name'])

        pp_dict['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        pp_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        pp_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        MasterList.objects.filter(id=iincreament_id).update(**pp_dict)

        iincreament_id += 1

    pp_description = ''
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    pp_dicttt = {pp_team: [pp_pick_type, pp_round, reason,
                           pp_aligned_pick, pp_unique_pick, pp_insert_instructions]}
    # pp_dict = {pp_team : [pp_round,pp_aligned_pick,pp_insert_instructions]}
    obj = Project.objects.get(id=pk)
    # Exporting trade to the transactions df
    transaction_details = pd.DataFrame(
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Priority_Pick', 'Transaction_Details': [pp_dict], 'Transaction_Description': pp_description})
    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Priority_Pick',
        Transaction_Details=pp_dicttt,
        Transaction_Description=pp_description,
        projectId=obj.id

    )
    last_inserted_obj = Transactions.objects.latest('id')
    last_inserted_id = last_inserted_obj.id
    Transactions.objects.filter(id=last_inserted_id).update(
        Transaction_Number=last_inserted_id)
    call_priority_pick_v2(transaction_details)

    return Response({'success': 'Add Trade has been Created'}, status=status.HTTP_201_CREATED)


def academy_bid_v1_inputs(request):

    data = request.data
    academy_player = data.get('playerid')

    teamid = data.get('academy_team')
    pick_id = data.get('pickid')
    return academy_player, teamid, pick_id


@api_view(['POST'])
@permission_classes([AllowAny])
def AcademyBidRequest(request, pk):
    academy_player, teamid, pick_id = academy_bid_v1_inputs(request)
    projectid = pk
    current_date = date.today()
    v_current_year = current_date.year
    v_current_year_plus1 = v_current_year+1

    df = dataframerequest(request, pk)
    teamQurerySet = Teams.objects.filter(id=teamid).values('id', 'TeamNames')
    academy_team = teamQurerySet[0]['TeamNames']
    academy_team_id = teamQurerySet[0]['id']
    academy_pick_type = 'Academy Bid Match'

    transactions = []

    transactionsqueryset = Transactions.objects.filter().values()
    for tran_deta in transactionsqueryset:
        transactions.append(tran_deta)

    df2 = pd.DataFrame(transactions)

    df_original = df.copy()
    df2_original = df2.copy()

    PickQueryset = MasterList.objects.filter(
        id=pick_id).values('Display_Name_Detailed')

    academy_bid = PickQueryset[0]['Display_Name_Detailed']

    academy_pts_value = df.loc[df.Display_Name_Detailed ==
                               academy_bid, 'AFL_Points_Value'].iloc[0]
    academy_bid_round = df.loc[df.Display_Name_Detailed ==
                               academy_bid, 'Draft_Round'].iloc[0]
    academy_bid_round_int = df.loc[df.Display_Name_Detailed ==
                                   academy_bid, 'Draft_Round_Int'].iloc[0]
    academy_bid_team = df.loc[df.Display_Name_Detailed ==
                              academy_bid, 'Current_Owner'].iloc[0]
    academy_bid_pick_no = df.loc[df.Display_Name_Detailed ==
                                 academy_bid, 'Overall_Pick'].iloc[0]

    sum_line1 = str(academy_bid_team) + ' have placed a bid on a ' + str(academy_team) + \
        ' academy player at pick ' + \
        str(academy_bid_pick_no) + ' in ' + str(academy_bid_round)

    # Defining discounts based off what round the bid came in:

    if academy_bid_round == 'RD1':
        academy_pts_required = int(academy_pts_value) * .8
        sum_line2 = academy_team + ' will require ' + \
            str(academy_pts_required) + ' draft points to match bid.'
    else:
        academy_pts_required = int(academy_pts_value) - 197
        sum_line2 = academy_team + ' will require ' + \
            str(academy_pts_required) + ' draft points to match bid.'

    # Creating a copy df of that teams available picks to match bid
    df_subset = df.copy()

    df_subset = df_subset[(df_subset.Current_Owner == academy_team_id) & (df_subset.Year.astype(
        int) == v_current_year) & (df_subset.Overall_Pick >= academy_bid_pick_no)]

    # Creating the cumulative calculations to determine how the points are repaid:

    df_subset['Cumulative_Pts'] = df_subset.groupby(
        'Current_Owner')['AFL_Points_Value'].transform(pd.Series.cumsum)

    df_subset['Payoff_Diff'] = df_subset['Cumulative_Pts'].astype(
        float) - academy_pts_required

    df_subset['AFL_Pts_Left'] = np.where(
        df_subset['Payoff_Diff'] <= 0,
        0,
        np.where(
            df_subset['Payoff_Diff'].astype(
                float) < df_subset['AFL_Points_Value'].astype(float),
            df_subset['Payoff_Diff'],
            df_subset['AFL_Points_Value']
        )
    )

    # creating previous pick rows to compare whether the picks have to be used or not:
    df_subset['AFL_Pts_Left_previous_pick'] = df_subset['AFL_Pts_Left'].shift()

    df_subset['AFL_Pts_Value_previous_pick'] = df_subset['AFL_Points_Value'].shift()

    df_subset['Action'] = np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'] == 0),
                                   'Pick lost to back of draft',
                                   np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'].astype(int) > 0),
                                            'Pick Shuffled Backwards',
                                            np.where((df_subset['AFL_Pts_Left'] == df_subset['AFL_Points_Value']) & (df_subset['Payoff_Diff'] < 0) & (df_subset['AFL_Pts_Value_previous_pick'].astype(float) > 0), 'Points Deficit',
                                                     'No Change')))

    df_subset['Deficit_Amount'] = np.where(
        df_subset['Action'] == 'Points Deficit', df_subset['Payoff_Diff'], np.nan)
    # defining the deficit amount
    try:
        academy_points_deficit = df_subset.loc[df_subset.Action ==
                                               'Points Deficit', 'Deficit_Amount'].iloc[0]

    except:
        academy_points_deficit = []

      # Create lists of changes to make:

    picks_lost = df_subset.loc[df_subset.Action ==
                               'Pick lost to back of draft', 'Display_Name_Detailed'].to_list()
    picks_shuffled = df_subset.loc[df_subset.Action ==
                                   'Pick Shuffled Backwards', 'Display_Name_Detailed'].to_list()

    pick_deficit = df_subset.loc[df_subset.Action ==
                                 'Points Deficit', 'Display_Name_Detailed']

    try:
        picks_shuffled_points_value = df_subset.loc[df_subset.Action ==
                                                    'Pick Shuffled Backwards', 'AFL_Pts_Left'].iloc[0]
    except:
        picks_shuffled_points_value = np.nan
    carry_over_deficit = academy_points_deficit

    # Executing The Academy Bid:
    # 3 Steps: Picks moving to back of draft, Pick getting shuffled backwards, and then if a pick has carryover deficit.

    # Step 1: Moving all picks to the back of the draft:

    if len(picks_lost) > 0:
        pick_lost_details = pd.DataFrame(
            columns=['Pick', 'Moves_To', 'New_Points_Value'])

        for pick in picks_lost:
            # Reset the index
            df = df.reset_index(drop=True)
            # Find row number of pick lost
            rowno_picklost = df.index[df.Display_Name_Detailed == pick][0]
            # print(rowno_picklost)

            # Find row number of the first pick in the next year

            rowno_start = df.index[((df.Year.astype(
                int)+1)[0] == v_current_year_plus1) & (df.Overall_Pick.astype(int) == 1)]
            # Insert pick to the row before next years draft:
            rowno_startnextyear = rowno_start[1]

            df = pd.concat([df.iloc[:rowno_startnextyear], df.iloc[[
                           rowno_picklost]], df.iloc[rowno_startnextyear:]]).reset_index(drop=True)
            # Find row number to delete and execute delete:
            rowno_delete = df.index[df.Display_Name_Detailed == pick][0]
            # print(rowno_delete)
            df.drop(rowno_delete, axis=0, inplace=True)

            # Changing the names of some key details:
            # Change system note to describe action

            df['System_Note'].mask(df['Display_Name_Detailed'] == pick,
                                   'Academy bid match: pick lost to back of draft', inplace=True)

            # Change the draft round
            df['Draft_Round'].mask(
                df['Display_Name_Detailed'] == pick, 'BOD', inplace=True)
            df['Draft_Round_Int'].mask(
                df['Display_Name_Detailed'] == pick, 99, inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick, str(
                v_current_year) + '-Back of Draft', inplace=True)

            # Reset points value
            df['AFL_Points_Value'].mask(
                df['Display_Name_Detailed'] == pick, 0, inplace=True)

            # If needing to update pick moves before the inserts
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
            df['AFL_Points_Value'] = df['Overall_Pick'].map(
                df['AFL_Points_Value']).fillna(0)

            # Reset index Again
            df = df.reset_index(drop=True)

            # One line summary:
            # print(pick + ' has been lost to the back of the draft.')

            # Update picks lost details df
            pick_lost_details_loop = pd.DataFrame({'Pick': pick,
                                                   'Moves_To': 'End of Draft',
                                                   'New_Points_Value': 0}, index=[0])
            pick_lost_details = pick_lost_details.append(
                pick_lost_details_loop)

    else:
        pick_lost_details = pd.DataFrame(
            columns=['Pick', 'Moves_To', 'New_Points_Value'])

    if len(picks_shuffled) > 0:
        pick_shuffled = picks_shuffled[0]

        # Find row number of pick shuffled
        rowno_pickshuffled = df.index[df.Display_Name_Detailed ==
                                      pick_shuffled][0]
        # Find the row number of where the pick should be inserted:
        rowno_pickshuffled_to = df[(df.Year.astype(int) == v_current_year)]['AFL_Points_Value'].astype(
            float).ge(picks_shuffled_points_value).idxmin()

        # Execute Shuffle
        # Insert pick to the row before next years draft:
        df = pd.concat([df.iloc[:rowno_pickshuffled_to], df.iloc[[
                       rowno_pickshuffled]], df.iloc[rowno_pickshuffled_to:]]).reset_index(drop=True)

        # Find row number to delete and execute delete:
        df.drop(rowno_pickshuffled, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(
            df['AFL_Points_Value']).fillna(0)

        # Reset index Again
        df = df.reset_index(drop=True)

        # Changing the names of some key details:
        # Change system note to describe action
        df['System_Note'].mask(df['Display_Name_Detailed'] == pick_shuffled,
                               'Academy bid match: pick shuffled backwards', inplace=True)

        # Change the draft round
        # Just take row above? if above and below equal each other, then value, if not take one above.
        # Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed ==
                                   pick_shuffled][0] - 1

        # Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

        # Make Changes
        # df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == pick_shuffled, new_rd_no,inplace=True)
        df['Draft_Round_Int'].mask(
            df['Display_Name_Detailed'] == pick_shuffled, str(new_rd_no), inplace=True)

        df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick_shuffled, str(
            v_current_year) + '-RD' + str(new_rd_no) + '-ShuffledBack', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(
            df['Display_Name_Detailed'] == pick_shuffled, picks_shuffled_points_value, inplace=True)

        # Summary:
        new_shuffled_pick_no = df.index[df.Display_Name_Detailed ==
                                        pick_shuffled][0] + 1
        # print(pick_shuffled + ' will be shuffled back to pick ' + new_shuffled_pick_no.astype(str) + ' in RD' + str(new_rd_no))

        # Summary Dataframe
        pick_shuffle_details = pd.DataFrame(
            {'Pick': pick_shuffled, 'Moves_To':  str(new_rd_no) + '-Pick' + new_shuffled_pick_no.astype(str), 'New_Points_Value': picks_shuffled_points_value}, index=[0])

    else:
        pick_shuffle_details = []

        # Step 3: Applying the deficit to next year:

    if len(pick_deficit) > 0:
        deficit_subset = df.copy()
        deficit_subset = deficit_subset[(deficit_subset.Current_Owner == academy_team_id) & (
            deficit_subset.Year.astype(int) == v_current_year_plus1) & (deficit_subset.Draft_Round >= academy_bid_round_int)]

        # Finding the first pick in the round to take the points off (and rowno)

        deficit_attached_pick = deficit_subset['Display_Name_Detailed'].iloc[0]
        deficit_pickshuffled_rowno = df.index[df.Display_Name_Detailed ==
                                              deficit_attached_pick][0]

        # finding the points value of that pick and then adjusting the deficit
        deficit_attached_pts = deficit_subset['AFL_Points_Value'].iloc[0]

        deficit_pick_points = float(
            deficit_attached_pts) + academy_points_deficit

        # Find the row number of where the pick should be inserted:
        deficit_pickshuffled_to = df[(df.Year.astype(int) == v_current_year_plus1)]['AFL_Points_Value'].astype(
            float).ge(deficit_pick_points).idxmin()

        # Execute pick shuffle
        df = pd.concat([df.iloc[:deficit_pickshuffled_to], df.iloc[[
                       deficit_pickshuffled_rowno]], df.iloc[deficit_pickshuffled_to:]]).reset_index(drop=True)

        # Find row number to delete and execute delete:
        df.drop(deficit_pickshuffled_rowno, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(
            library_AFL_Draft_Points).fillna(0)
        # Reset index Again
        df = df.reset_index(drop=True)

        # Change system note to describe action
        df['System_Note'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'Academy bid match: Points Deficit',
                               inplace=True)

        # Change the draft round
        # Just take row above? if above and below equal each other, then value, if not take one above.
        # Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed ==
                                   deficit_attached_pick][0] - 1

        # Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

        # Make Changes
        df['Draft_Round_Int'].mask(
            df['Display_Name_Detailed'] == deficit_attached_pick, new_rd_no, inplace=True)
        df['Draft_Round'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'RD' + str(new_rd_no),
                               inplace=True)
        df['Pick_Group'].mask(df['Display_Name_Detailed'] == deficit_attached_pick,
                              str(v_current_year) + '-RD' + str(new_rd_no) + '-AcademyDeficit', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(
            df['Display_Name_Detailed'] == deficit_attached_pick, deficit_pick_points, inplace=True)

        # Summary:
        # getting the new overall pick number and what round it belongs to:
        deficit_new_shuffled_pick_no = df[df.Display_Name_Detailed ==
                                          deficit_attached_pick].Overall_Pick.iloc[0]
        deficit_new_shuffled_pick_RD_no = df[df.Display_Name_Detailed ==
                                             deficit_attached_pick].Draft_Round.iloc[0]

        # 2021-RD3-Pick43-Richmond
        pick_deficit_details = pd.DataFrame(
            {'Pick': deficit_attached_pick, 'Moves_To': deficit_new_shuffled_pick_no, 'New_Points_Value': deficit_pick_points}, index=[0])

        # print(deficit_attached_pick + ' moves to pick ' + deficit_new_shuffled_pick_ no.astype(str) + ' in ' + deficit_new_shuffled_pick_RD_no)

    else:
        pick_deficit_details = []

    ########## EXECUTE INSERT OF PICK TO THE SPOT OF THE BID ##############
    # inserting pick above academy_bid

    # Make the changes to the masterlist:
    rowno = df.index[df['Display_Name_Detailed'] == academy_bid][0]
    # create the line to insert:

    line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == academy_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                         'TeamName': academy_team_id, 'PickType': 'AcademyBidMatch', 'Original_Owner': academy_team_id, 'Current_Owner': academy_team_id,
                         'Previous_Owner': '', 'Draft_Round': academy_bid_round, 'Draft_Round_Int': academy_bid_round_int,
                         'Pick_Group': str(v_current_year) + '-' + academy_bid_round + '-AcademyBidMatch', 'Reason': 'Academy Bid Match',
                         'Pick_Status': 'Used', 'Selected_Player': academy_player}, index=[rowno])

    # Execute Insert
    # i.e stacks 3 dataframes on top of each other
    df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                   ).reset_index(drop=True)

    # MasterList.objects.filter(projectid_id=pk).delete()

    udpatedf = update_masterlist(df)

    udpatedf = udpatedf.drop('id', 1)

    iincreament_id = 1

    for index, updaterow in udpatedf.iterrows():
        row1 = dict(updaterow)

        team = Teams.objects.get(id=updaterow.TeamName)

        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = row1['Overall_Pick']

        Project1 = Project.objects.get(id=pk)
        row1['Previous_Owner'] = team
        row1['TeamName'] = team
        row1['Original_Owner'] = Original_Owner
        row1['Current_Owner'] = Current_Ownerr
        row1['projectid_id'] = Project1.id

        row1['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        row1['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(row1['Display_Name'])

        row1['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        row1['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        row1['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        MasterList.objects.filter(id=iincreament_id).update(**row1)

        iincreament_id += 1

     ######## Combine into a summary dataframe: #############

        academy_summaries_list = [pick_lost_details,
                                  pick_shuffle_details, pick_deficit_details]

        academy_summary_df = pd.DataFrame(
            columns=['Pick', 'Moves_To', 'New_Points_Value'])

    for x in academy_summaries_list:
        if len(x) > 0:
            academy_summary_df = academy_summary_df.append(x)

    academysummery_list = []
    academy_summary_dict = academy_summary_df.to_dict(orient="list")

    for key, value in academy_summary_dict.items():
        for i in value:

            result = ' ' + key + ' - ' + str(i)
            academysummery_list.append(result)
    academy_summary_str = ''.join(str(e) for e in academy_summaries_list)

    ######### Exporting Transaction Details: ###############

    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    academy_dict = {academy_team: [
        academy_pick_type, academy_bid, academy_bid_pick_no, academy_player]}

    project_obj = Project.objects.get(id=pk)

    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Academy_Bid_Match',
        Transaction_Details=academy_dict,
        Transaction_Description=academy_summaries_list,
        projectId=project_obj.id

    )
    obj = Transactions.objects.latest('id')
    count = Transactions.objects.filter().count()
    Transactions.objects.filter(id=obj.id).update(Transaction_Number=count)
    return Response({'success': 'Academy Bid has Created'}, status=status.HTTP_201_CREATED)


def academy_bid_inputs(request, pk):

    masterlist = dataframerequest(request, pk)
    data = request.data
    academy_player = data.get('player')
    academy_team = data.get('team')
    academy_bid = data.get('pickid')
    return masterlist, academy_player, academy_team, academy_bid


def call_academy_bid_v2(transactions):
    return transactions


@api_view(['POST'])
@permission_classes([AllowAny])
def academy_bid_v2(request, pk):
    current_time = date.today()
    v_current_year = current_time.year
    v_current_year_plus1 = v_current_year + 1

    masterlist, academy_player, academy_team, academy_bid = academy_bid_inputs(
        request, pk)

    df = masterlist
    library_AFL_Draft_Points = df['AFL_Points_Value']

    # Details of the bid
    picklist = []
    df.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    queryset = MasterList.objects.filter(id__in=academy_bid).values()
    for pick_data in queryset:
        picklist.append(pick_data['Display_Name_Detailed'])
    fa_pick = "".join(picklist)
    academy_pts_value = df.loc[df.Display_Name_Detailed ==
                               fa_pick, 'AFL_Points_Value'].iloc[0]
    academy_bid_round = df.loc[df.Display_Name_Detailed ==
                               fa_pick, 'Draft_Round'].iloc[0]
    academy_bid_round_int = df.loc[df.Display_Name_Detailed ==
                                   fa_pick, 'Draft_Round_Int'].iloc[0]
    academy_bid_team = df.loc[df.Display_Name_Detailed ==
                              fa_pick, 'Current_Owner'].iloc[0]
    academy_bid_pick_no = df.loc[df.Display_Name_Detailed ==
                                 fa_pick, 'Overall_Pick'].iloc[0]
    academy_pick_type = 'Academy Bid Match'

    sum_line1 = str(academy_bid_team) + ' have placed a bid on a ' + str(academy_team) + \
        ' academy player at pick ' + \
        str(academy_bid_pick_no) + ' in ' + str(academy_bid_round)

    # Defining discounts based off what round the bid came in:
    if academy_bid_round == 'RD1':
        academy_pts_required = float(academy_pts_value) * .8
        sum_line2 = str(academy_team) + ' will require ' + \
            str(academy_pts_required) + ' draft points to match bid.'
    else:
        academy_pts_required = float(academy_pts_value) - 197
        sum_line2 = str(academy_team) + ' will require ' + \
            str(academy_pts_required) + ' draft points to match bid.'

    # Creating a copy df of that teams available picks to match bid
    df_subset = df.copy()
    df_subset = df_subset[(df_subset.Current_Owner.astype(int) == int(academy_team)) & (
        df_subset.Year.astype(int) == int(v_current_year)) & (df_subset.Overall_Pick >= academy_bid_pick_no)]

    # Creating the cumulative calculations to determine how the points are repaid:

    df['AFL_Points_Value'] = df['AFL_Points_Value'].apply(
        lambda x: float(x.split()[0].replace(',', '')))

    df_subset['Payoff_Diff'] = df_subset['AFL_Points_Value'].astype(
        float) - float(academy_pts_required)
    df_subset['AFL_Pts_Left'] = np.where(
        df_subset['Payoff_Diff'] <= 0,
        0,
        np.where(
            df_subset['Payoff_Diff'].astype(
                float) < df_subset['AFL_Points_Value'].astype(float),
            df_subset['Payoff_Diff'],
            df_subset['AFL_Points_Value']
        )
    )
    # creating previous pick rows to compare whether the picks have to be used or not:
    df_subset['AFL_Pts_Left_previous_pick'] = df_subset['AFL_Pts_Left'].shift()
    df_subset['AFL_Pts_Value_previous_pick'] = df_subset['AFL_Points_Value'].shift()

    df_subset['Action'] = np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'] == 0),
                                   'Pick lost to back of draft',
                                   np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'].astype(float).astype('int', errors='ignore') > 0),
                                            'Pick Shuffled Backwards',
                                            np.where((df_subset['AFL_Pts_Left'] == df_subset['AFL_Points_Value']) & (df_subset['Payoff_Diff'] < 0) & (df_subset['AFL_Pts_Value_previous_pick'].astype(float) > 0), 'Points Deficit',
                                                     'No Change')))
    # Add a column for the deficit amount and then define it as a variable:
    df_subset['Deficit_Amount'] = np.where(
        df_subset['Action'] == 'Points Deficit', df_subset['Payoff_Diff'], np.nan)
    # defining the deficit amount
    try:
        academy_points_deficit = df_subset.loc[df_subset.Action ==
                                               'Points Deficit', 'Deficit_Amount'].iloc[0]

    except:
        academy_points_deficit = []

     # Create lists of changes to make:
    picks_lost = df_subset.loc[df_subset.Action ==
                               'Pick lost to back of draft', 'Display_Name_Detailed'].to_list()

    picks_shuffled = df_subset.loc[df_subset.Action ==
                                   'Pick Shuffled Backwards', 'Display_Name_Detailed'].to_list()
    pick_deficit = df_subset.loc[df_subset.Action ==
                                 'Points Deficit', 'Display_Name_Detailed'].to_list()

    try:
        picks_shuffled_points_value = df_subset.loc[df_subset.Action ==
                                                    'Pick Shuffled Backwards', 'AFL_Pts_Left'].iloc[0]

    except:
        picks_shuffled_points_value = np.nan

    carry_over_deficit = academy_points_deficit

    # Step 1: Moving all picks to the back of the draft:

    if len(picks_lost) > 0:
        pick_lost_details = pd.DataFrame(
            columns=['Pick', 'Moves_To', 'New_Points_Value'])

        for pick in picks_lost:
            # Reset the index
            df = df.reset_index(drop=True)

            # Find row number of pick lost

            rowno_picklost = df.index[df.Display_Name_Detailed == pick][0]

            # Find row number of the first pick in the next year
            rowno_startnextyear = df.index[(df.Year.astype(int) == int(
                v_current_year_plus1)) & (df.Overall_Pick.astype(float) == 1)][0]

            # print(rowno_startnextyear)

            # Insert pick to the row before next years draft:
            df = pd.concat([df.iloc[:rowno_startnextyear], df.iloc[[
                           rowno_picklost]], df.iloc[rowno_startnextyear:]]).reset_index(drop=True)

            # Find row number to delete and execute delete:

            rowno_delete = df.index[df.Display_Name_Detailed == pick][0]
            # print(rowno_delete)
            df.drop(rowno_delete, axis=0, inplace=True)

            # Changing the names of some key details:
            # Change system note to describe action
            df['System_Note'].mask(df['Display_Name_Detailed'] == pick,
                                   'Academy bid match: pick lost to back of draft', inplace=True)

            # Change the draft round
            df['Draft_Round'].mask(
                df['Display_Name_Detailed'] == pick, 'BOD', inplace=True)
            df['Draft_Round_Int'].mask(
                df['Display_Name_Detailed'] == pick, 99, inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick, str(
                v_current_year) + '-Back of Draft', inplace=True)

            # Reset points value
            df['AFL_Points_Value'].mask(
                df['Display_Name_Detailed'] == pick, 0, inplace=True)

            # If needing to update pick moves before the inserts
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
            df['AFL_Points_Value'] = df['Overall_Pick'].map(
                library_AFL_Draft_Points).fillna(0)

            # Reset index Again
            df = df.reset_index(drop=True)

            # One line summary:
            # print(pick + ' has been lost to the back of the draft.')

            # Update picks lost details df
            pick_lost_details_loop = pd.DataFrame({'Pick': pick,
                                                   'Moves_To': 'End of Draft',
                                                   'New_Points_Value': 0}, index=[0])
            pick_lost_details = pick_lost_details.append(
                pick_lost_details_loop)

    else:
        pick_lost_details = pd.DataFrame(
            columns=['Pick', 'Moves_To', 'New_Points_Value'])

    if len(picks_shuffled) > 0:

        pick_shuffled = picks_shuffled[0]

        # Find row number of pick shuffled
        rowno_pickshuffled = df.index[df.Display_Name_Detailed ==
                                      pick_shuffled][0]

        # Find the row number of where the pick should be inserted:
        rowno_pickshuffled_to = df[(df.Year.astype(int) == int(
            v_current_year))]['AFL_Points_Value'].astype(float).ge(picks_shuffled_points_value).idxmin()

        # Execute Shuffle
        # Insert pick to the row before next years draft:
        df = pd.concat([df.iloc[:rowno_pickshuffled_to], df.iloc[[
                       rowno_pickshuffled]], df.iloc[rowno_pickshuffled_to:]]).reset_index(drop=True)

        # Find row number to delete and execute delete:
        df.drop(rowno_pickshuffled, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(
            library_AFL_Draft_Points).fillna(0)

        # Reset index Again
        df = df.reset_index(drop=True)

        # Changing the names of some key details:
        # Change system note to describe action
        df['System_Note'].mask(df['Display_Name_Detailed'] == pick_shuffled,
                               'Academy bid match: pick shuffled backwards', inplace=True)

        # Change the draft round
        # Just take row above? if above and below equal each other, then value, if not take one above.
        # Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed ==
                                   pick_shuffled][0] - 1
        # Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

        # Make Changes
        df['Draft_Round_Int'].mask(
            df['Display_Name_Detailed'] == pick_shuffled, new_rd_no, inplace=True)

        df['Draft_Round'].mask(df['Display_Name_Detailed'] ==
                               pick_shuffled, 'RD' + str(int(new_rd_no)), inplace=True)
        df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick_shuffled, str(
            v_current_year) + '-RD' + str(int(new_rd_no)) + '-ShuffledBack', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(
            df['Display_Name_Detailed'] == pick_shuffled, picks_shuffled_points_value, inplace=True)

        # Summary:
        new_shuffled_pick_no = df.index[df.Display_Name_Detailed ==
                                        pick_shuffled][0] + 1
        print(pick_shuffled + ' will be shuffled back to pick ' +
              new_shuffled_pick_no.astype(str) + ' in RD' + str(int(new_rd_no)))

        # Summary Dataframe
        pick_shuffle_details = pd.DataFrame(
            {'Pick': pick_shuffled, 'Moves_To': 'RD' + str(int(new_rd_no)) + '-Pick' + new_shuffled_pick_no.astype(str), 'New_Points_Value': picks_shuffled_points_value}, index=[0])

    else:
        pick_shuffle_details = []

        # Step 3: Applying the deficit to next year:
    if len(pick_deficit) > 0:
        deficit_subset = df.copy()

        deficit_subset = deficit_subset[(deficit_subset.Current_Owner.astype(int) == int(academy_team)) & (deficit_subset.Year.astype(
            int) == int(v_current_year_plus1)) & (deficit_subset.Draft_Round_Int.astype(int) >= int(academy_bid_round_int))]

        # Finding the first pick in the round to take the points off (and rowno)

        deficit_attached_pick = deficit_subset['Display_Name_Detailed'].iloc[0]
        deficit_pickshuffled_rowno = df.index[df.Display_Name_Detailed ==
                                              deficit_attached_pick][0]

        # finding the points value of that pick and then adjusting the deficit
        deficit_attached_pts = deficit_subset['AFL_Points_Value'].iloc[0]
        academy_points_deficit_as_float = np.array(
            list(academy_points_deficit)).astype(float)

        deficit_pick_points = deficit_attached_pts + academy_points_deficit_as_float

        # Find the row number of where the pick should be inserted:

        deficit_pickshuffled_to = df[(int(df.Year[0])+1 == int(v_current_year_plus1))
                                     ]['AFL_Points_Value'].astype(float).ge(deficit_pick_points).idxmin()

        # Execute pick shuffle
        df = pd.concat([df.iloc[:deficit_pickshuffled_to], df.iloc[[
                       deficit_pickshuffled_rowno]], df.iloc[deficit_pickshuffled_to:]]).reset_index(drop=True)

        # Find row number to delete and execute delete:
        df.drop(deficit_pickshuffled_rowno, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(
            library_AFL_Draft_Points).fillna(0)

        # Reset index Again
        df = df.reset_index(drop=True)

        # Change system note to describe action
        df['System_Note'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'Academy bid match: Points Deficit',
                               inplace=True)

        # Change the draft round
        # Just take row above? if above and below equal each other, then value, if not take one above.
        # Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed ==
                                   deficit_attached_pick][0] - 1

        # Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

        # Make Changes
        df['Draft_Round_Int'].mask(
            df['Display_Name_Detailed'] == deficit_attached_pick, new_rd_no, inplace=True)
        df['Draft_Round'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'RD' + new_rd_no.round(0).astype(str),
                               inplace=True)
        df['Pick_Group'].mask(df['Display_Name_Detailed'] == deficit_attached_pick,
                              str(v_current_year) + '-RD' + new_rd_no.round(0).astype(str) + '-AcademyDeficit', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(
            df['Display_Name_Detailed'] == deficit_attached_pick, deficit_pick_points, inplace=True)

        # Summary:
        # getting the new overall pick number and what round it belongs to:
        deficit_new_shuffled_pick_no = df[df.Display_Name_Detailed ==
                                          deficit_attached_pick].Overall_Pick.iloc[0]
        deficit_new_shuffled_pick_RD_no = df[df.Display_Name_Detailed ==
                                             deficit_attached_pick].Draft_Round.iloc[0]

        # 2021-RD3-Pick43-Richmond
        pick_deficit_details = pd.DataFrame(
            {'Pick': deficit_attached_pick, 'Moves_To': deficit_new_shuffled_pick_no, 'New_Points_Value': deficit_pick_points}, index=[0])

        print(deficit_attached_pick + ' moves to pick ' +
              deficit_new_shuffled_pick_no.astype(str) + ' in ' + deficit_new_shuffled_pick_RD_no)

    else:
        pick_deficit_details = []

    ########## EXECUTE INSERT OF PICK TO THE SPOT OF THE BID ##############
    # inserting pick above academy_bid

    #  Rename Columns name because database is returning names with id concatenated (Forienkey relation working on the columns fields)

    # Make the changes to the masterlist:
    rowno = df.index[df['Display_Name_Detailed'] == fa_pick][0]

    # create the line to insert:

    line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(academy_team), 'Position'].iloc[0], 'Year': v_current_year,
                         'TeamName': academy_team, 'PickType': 'AcademyBidMatch', 'Original_Owner': academy_team, 'Current_Owner': academy_team,
                         'Previous_Owner': '', 'Draft_Round': academy_bid_round, 'Draft_Round_Int': academy_bid_round_int,
                         'Pick_Group': str(v_current_year) + '-' + academy_bid_round + '-AcademyBidMatch', 'Reason': 'Academy Bid Match',
                         'Pick_Status': 'Used', 'Selected_Player': academy_player}, index=[rowno])

    # Execute Insert
    # i.e stacks 3 dataframes on top of each other
    df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                   ).reset_index(drop=True)
    df = df.iloc[rowno]

    df['id'] = rowno+1
    df['projectid_id'] = pk

    MasterList.objects.filter(id=rowno+1).update(**df)
    new_df = []
    Queryset = MasterList.objects.filter(projectid_id=pk).values()
    for picks in Queryset:
        new_df.append(picks)

    df = pd.DataFrame(df)

    df = dataframerequest(request, pk)

    updatedf = update_masterlist(df)

    iincreament_id = 1
    for index, updaterow in updatedf.iterrows():
        academy_dict = dict(updaterow)
        team = Teams.objects.get(id=updaterow.TeamName)
        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = academy_dict['Overall_Pick']

        Project1 = Project.objects.get(id=pk)
        academy_dict['Previous_Owner'] = previous_owner
        team = Teams.objects.get(id=updaterow.TeamName)
        academy_dict['TeamName'] = team
        academy_dict['Original_Owner'] = Original_Owner
        academy_dict['Current_Owner'] = Current_Ownerr
        academy_dict['projectid'] = Project1

        academy_dict['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        academy_dict['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(academy_dict['Display_Name'])

        academy_dict['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        academy_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        academy_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        MasterList.objects.filter(id=iincreament_id).update(**academy_dict)

        iincreament_id += 1

    ######## Combine into a summary dataframe: #############
    academy_summaries_list = [pick_lost_details,
                              pick_shuffle_details, pick_deficit_details]

    academy_summary_df = pd.DataFrame(
        columns=['Pick', 'Moves_To', 'New_Points_Value'])
    for x in academy_summaries_list:
        if len(x) > 0:
            academy_summary_df = academy_summary_df.append(x)
    academy_summary_dict = academy_summary_df.to_dict(orient="list")

    ######### Exporting Transaction Details: ###############
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    academy_dict = {academy_team: [
        academy_pick_type, academy_bid, academy_bid_pick_no, academy_player]}

    # Create Simple description.
    academy_description = 'Academy Bid Match: Pick ' + \
        str(academy_bid_pick_no) + ' ' + str(academy_team) + \
        ' (' + str(academy_player) + ')'

    obj = Project.objects.get(id=pk)

    drafted_player_dict = {academy_team: [
        academy_bid_round, academy_bid_pick_no, academy_player]}
    drafted_description = 'With pick ' + \
        str(academy_bid_pick_no) + ' ' + str(academy_team) + \
        ' have selected ' + str(academy_player)

    obj = Project.objects.get(id=pk)

    transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Academy_Bid_Match',
         'Transaction_Details': academy_dict,
         'Transaction_Description': academy_description,
         'projectid': obj.id
         })
    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Academy_Bid_Match',
        Transaction_Details=academy_dict,
        Transaction_Description=academy_description,
        projectId=obj.id

    )
    lastinserted_obj = Transactions.objects.latest('id')
    Transactions.objects.filter(Transaction_Number=lastinserted_obj).update()
    call_academy_bid_v2(transaction_details)
    return Response({'success': 'Academy-Bid-v2 has been Created'}, status=status.HTTP_201_CREATED)


def add_FA_compansation_inputs(request):

    data = request.data
    fa_team = data.get('teamid')
    reason = data.get('reason')
    types = data.get('picktype')
    pickId = data.get('pickid')
    fa_insert_instructions = data.get('instructions')
    return fa_team, reason, types, pickId, fa_insert_instructions


@api_view(['POST'])
@permission_classes([AllowAny])
def add_FA_compansation(request, pk):

    current_date = date.today()
    v_current_year = current_date.year
    v_current_year_plus1 = v_current_year+1
    fa_round = ''

    df = dataframerequest(request, pk)
    fa_team, reason, types, pickId, fa_insert_instructions = add_FA_compansation_inputs(
        request)

    fa_team_name = []
    fa_dict = {}
    teams_queryset = Teams.objects.filter(id=int(fa_team)).values()
    for teams_data in teams_queryset:
        fa_team_name.append(teams_data['TeamNames'])

    fa_pick_obj = PicksType.objects.get(pickType=types)
    fa_pick_type = fa_pick_obj.pickType

    pick_queryset = MasterList.objects.filter(id=pickId).values()
    fa_aligned_pick_list = []
    for picksdata in pick_queryset:
        fa_aligned_pick_list.append(picksdata['Display_Name_Detailed'])
    fa_aligned_pick = "".join(fa_aligned_pick_list)

    #  Rename Columns name because database is returning names with id concatenated (Forienkey relation working on the columns fields)
    if fa_pick_type == 'Start of Draft':

        # Find the first row that is a standard pick:

        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD1-Standard')].iloc[0]

        # create the line to insert:

        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year, 'TeamName': fa_team,  'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD1',
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])

        # Execute Insert above the rowno

        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        df = df.iloc[rowno]

        df['id'] = rowno
        df['projectid_id'] = pk

        MasterList.objects.filter(id=rowno).update(**df)

        fa_round = 'RD1'
        # Update transactions
        fa_dict[fa_team] = [fa_pick_type, fa_round, reason,
                            fa_aligned_pick, fa_insert_instructions]
        fa_description = str(fa_team_name) + ' received a ' + \
            str(fa_pick_type) + ' FA Compensation Pick'

    if fa_pick_type == 'First Round':

        fa_round = 'RD1'

        fa_aligned_pick = "".join(fa_aligned_pick_list)

        rowno = df.index[df['Display_Name_Detailed'] == fa_aligned_pick][0]

        # create the line to insert:

        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': '', 'Draft_Round': fa_round, 'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])

        # Execute Insert

        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]

            df['id'] = rowno
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]

            df['id'] = rowno+1
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno+1).update(**df)

        fa_description = {}
        # Update Transactions List
        fa_dict[fa_team] = [fa_pick_type, fa_round, reason,
                            fa_aligned_pick, fa_insert_instructions]

        fa_description = str(fa_team_name) + 'received a ' + \
            fa_pick_type + ' FA Compensation Pick'

    if fa_pick_type == 'End of First Round':
        # Find the last row that is a standard pick:

        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD1-Standard')][-1]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': fa_team,
                             'Draft_Round': 'RD1', 'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert below the rowno
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)

        df = df.iloc[rowno+1]

        df['id'] = rowno+1
        df['projectid_id'] = pk
        # df['Previous_Owner']=None

        MasterList.objects.filter(id=rowno+1).update(**df)

        # Update transactions

        fa_description = {}
        fa_dict[fa_team] = [fa_pick_type, reason]
        fa_description['fa_team_name'] = ' received a ' + \
            fa_pick_type + ' FA Compensation Pick'

    if fa_pick_type == 'Start of Second Round':

        # Find the first row that is a standard pick in the 2nd round:
        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD2-Standard')][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': fa_team,
                             'Draft_Round': 'RD2',
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])

        # Execute Insert above the rowno
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)

        df = df.iloc[rowno]

        df['id'] = rowno
        df['projectid_id'] = pk

        MasterList.objects.filter(id=rowno).update(**df)

        fa_round = 'RD1'

        # Update transactions

        fa_dict[fa_team] = [fa_pick_type, fa_round, reason,
                            fa_aligned_pick, fa_insert_instructions]

        fa_description = fa_team + ' received a ' + \
            fa_pick_type + ' FA Compensation Pick'

    if fa_pick_type == 'Second Round':

        # Get Round
        fa_round = 'RD2'

        # Make the changes to the masterlist:
        # find row number of the aligned pick:

        rowno = df.index[df['Display_Name_Detailed'] == fa_aligned_pick][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                            'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': fa_team, 'Draft_Round': fa_round, 'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])

        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df['id'] = rowno
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                            df.iloc[rowno + 1:]]).reset_index(drop=True)

            df = df.iloc[rowno+1]

            df['id'] = rowno+1
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno+1).update(**df)

        # Update Transactions List

        fa_dict[fa_team] = [fa_pick_type, fa_round, reason,
                            fa_aligned_pick, fa_insert_instructions]
        fa_description = str(fa_team_name) + ' received a ' + \
            fa_pick_type + ' FA Compensation Pick'

    if fa_pick_type == 'End of Second Round':
        # Find the last row that is a standard pick:
        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD2-Standard')][-1]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': fa_team,
                             'Draft_Round': 'RD2', 'Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert below the rowno
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)

        df = df.iloc[rowno+1]

        df['id'] = rowno
        df['projectid_id'] = pk

        MasterList.objects.filter(id=rowno).update(**df)

        # Update transactions
        fa_round = 'RD2'
        fa_aligned_pick = ''
        fa_unique_pick = ''
        fa_insert_instructions = ''
        fa_dict[fa_team] = [fa_pick_type, fa_round, reason,
                            fa_aligned_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + fa_pick_type + \
            ' FA Compensation Pick' + '(' + reason + ')'

    if fa_pick_type == 'Third Round':

        # Get Round
        fa_round = 'RD3'

        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        rowno = df.index[df['Display_Name_Detailed'] == fa_aligned_pick][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': fa_team, 'Draft_Round': fa_round, 'Pick_Group': str(v_current_year) + '-' + 'RD3-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])

        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]

            df['id'] = rowno
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)

            df = df.iloc[rowno+1]

            df['id'] = rowno+1
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno+1).update(**df)
        # Update Transactions List

        fa_dict[fa_team] = [fa_pick_type, fa_round, reason,
                            fa_aligned_pick, fa_insert_instructions]
        fa_description = str(fa_team_name) + ' received a ' + \
            fa_pick_type + ' FA Compensation Pick'

    if fa_pick_type == 'Custom Fixed Position':
        fa_round = 'RD5'

        # find row number of the aligned pick:

        rowno = df.index[df['Display_Name_Detailed'].astype(
            str) == fa_aligned_pick][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': int(fa_team), 'PickType': 'FA_Compensation', 'Original_Owner': int(fa_team), 'Current_Owner': int(fa_team),
                             'Previous_Owner': fa_team, 'Draft_Round': fa_round,
                             'Pick_Group': str(v_current_year) + '-' + fa_round + '-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])

        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)

            df = df.iloc[rowno]
            df['id'] = rowno
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)

            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['projectid_id'] = pk
            MasterList.objects.filter(id=rowno+1).update(**df)

        fa_dict[fa_team] = [fa_pick_type, fa_round, reason,
                            fa_aligned_pick, fa_insert_instructions]
        fa_description = str(fa_team_name) + ' received a ' + \
            str(fa_pick_type) + ' FA Compensation Pick'

    df = dataframerequest(request, pk)

# ############################ Call update masterlist ###########################

    udpatedf = update_masterlist(df)

    iincreament_id = 1
    for index, updaterow in udpatedf.iterrows():

        row1 = dict(updaterow)
        team = Teams.objects.get(id=updaterow.TeamName)
        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = row1['Overall_Pick']

        Project1 = Project.objects.get(id=pk)

        row1['Previous_Owner'] = team
        row1['TeamName'] = team
        row1['Original_Owner'] = Original_Owner
        row1['Current_Owner'] = Current_Ownerr
        row1['projectid'] = Project1

        row1['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        row1['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(row1['Display_Name'])

        row1['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        row1['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        row1['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        MasterList.objects.filter(id=iincreament_id).update(**row1)

        iincreament_id += 1

    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')

    # Exporting trade to the transactions df
    transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'FA_Compensation', 'Transaction_Details': fa_dict, 'Transaction_Description': fa_description, 'projectId': pk})

    objj = Project.objects.get(id=pk)
    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='FA_Compensation',
        Transaction_Details=fa_dict,
        Transaction_Description=fa_description,
        projectId=objj.id

    )
    obj = Transactions.objects.latest('id')
    count = Transactions.objects.filter().count()
    Transactions.objects.filter(id=obj.id).update(Transaction_Number=count)

    return Response({'success': 'Add-FA-compansation Created Successfuly'}, status=status.HTTP_201_CREATED)


def add_FA_compensation_inputs_request(request, pk):

    projectid = pk

    masterlist = dataframerequest(request, pk)

    data = request.data

    # Ask for team Name:
    fa_team = data.get('teamid')
    fa_pick_type = data.get('picktype')
    reason = data.get('reason')
    fa_round = data.get('round')
    pick_id = data.get('pickid')
    fa_insert_instructions = data.get('instructions')

    # Define the teams current picks

    fa_team_picks = masterlist[masterlist['Current_Owner'].astype(
        int) == int(fa_team)]['Display_Name_Detailed'].tolist()

    # define a blank round & aligned pick as it will either be made here or within function

    fa_aligned_pick_list = []
    # fa_round = ''
    fa_unique_pick = ''
    # fa_insert_instructions = ''

    MasterlistQuerySet = MasterList.objects.filter(id=pick_id).values()

    for masterlist_data in MasterlistQuerySet:
        fa_aligned_pick_list.append(masterlist_data['Display_Name_Detailed'])

    fa_aligned_pick = "".join(fa_aligned_pick_list)

    # ask for extra details depending on pick type:
    if fa_pick_type == 'Custom Fixed Position':

        fa_unique_pick = masterlist.loc[masterlist.Display_Name_Detailed ==
                                        fa_aligned_pick, 'Unique_Pick_ID'].iloc[0]

    if fa_pick_type == 'First Round' or fa_pick_type == 'Second Round' or fa_pick_type == 'Third Round':

        fa_unique_pick = masterlist.loc[masterlist.Display_Name_Detailed ==
                                        fa_aligned_pick, 'Unique_Pick_ID'].iloc[0]

    return masterlist, pick_id, fa_team, fa_pick_type, fa_round, reason, fa_aligned_pick, fa_unique_pick, fa_insert_instructions


def call_FA_Compensation(transactions):
    return transactions


@api_view(['POST'])
@permission_classes([AllowAny])
def add_FA_compensation_v2(request, pk):

    current_date = date.today()
    v_current_year = current_date.year
    masterlist, fa_team, pick_id, fa_pick_type, fa_round, reason, fa_aligned_pick, fa_unique_pick, fa_insert_instructions = add_FA_compensation_inputs_request(
        request, pk)

    df = masterlist

    if fa_pick_type == 'Start of Draft':
        # Find the first row that is a standard pick:
        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD1-Standard')]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': int(fa_team), 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD1', 'Draft_Round_Int': 1,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])

        # Execute Insert above the rowno
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       )

        df = df.iloc[rowno]

        df['id'] = rowno

        df['projectid_id'] = pk

        # Update transactions
        fa_round = 'RD1'
        fa_aligned_pick = ''
        fa_unique_pick = ''
        fa_insert_instructions = ''
        fa_dict = {}
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,
                              fa_aligned_pick, fa_unique_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + \
            ' FA Compensation Pick' + '(' + str(reason) + ')'
        MasterList.objects.filter(id=rowno).update(**df)

    if fa_pick_type == 'First Round':

        # ///////////// Make the changes to the masterlist: /////////////////////////

        rowno = df.index[df['Display_Name_Detailed'] == fa_aligned_pick][0]
        fa_unique_pick = df.loc[df.Display_Name_Detailed ==
                                fa_aligned_pick, 'Unique_Pick_ID'].iloc[0]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team,  'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': '', 'Draft_Round': 'RD1', 'Draft_Round_Int': 1,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])
        # Execute Insert
        # i.e stacks 3 dataframes on top of each other
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)

            df = df.iloc[rowno]

            df['id'] = rowno
            df['projectid'] = pk
            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = pd.concat([df.loc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno+1).update(**df)

        # Update transactions
        fa_round = 'RD1'

        fa_dict = {}
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,
                              fa_aligned_pick, fa_unique_pick, fa_insert_instructions]

        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + \
            ' FA Compensation Pick' + '(' + reason + ')'

    if fa_pick_type == 'End of First Round':
        # Find the last row that is a standard pick:
        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD1-Standard')][-1]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD1', 'Draft_Round_Int': 1,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert below the rowno
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno+1]

        df['id'] = rowno+1
        df['projectid_id'] = pk

        MasterList.objects.filter(id=rowno+1).update(**df)

        # Update transactions
        fa_round = 'RD1'
        fa_aligned_pick = ''
        fa_unique_pick = ''
        fa_insert_instructions = ''
        fa_dict = {}
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,
                              fa_aligned_pick, fa_unique_pick, fa_insert_instructions]

        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + \
            ' FA Compensation Pick' + '(' + reason + ')'

    if fa_pick_type == 'Start of Second Round':
        # Find the first row that is a standard pick in the 2nd round:
        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD2-Standard')][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD2', 'Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert above the rowno
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        df = df.iloc[rowno]
        df['id'] = rowno
        df['projectid_id'] = pk
        MasterList.objects.filter(id=rowno).update(**df)
        # Update transactions
        fa_round = 'RD2'
        fa_aligned_pick = ''
        fa_unique_pick = ''
        fa_insert_instructions = ''
        fa_dict = {}
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,
                              fa_aligned_pick, fa_unique_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + \
            ' FA Compensation Pick' + '(' + reason + ')'

    if fa_pick_type == 'Second Round':
        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        rowno = df.index[df['Display_Name_Detailed'] == fa_aligned_pick][0]
        fa_unique_pick = df.loc[df.Display_Name_Detailed ==
                                fa_aligned_pick, 'Unique_Pick_ID'].iloc[0]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': fa_team, 'Draft_Round': 'RD2', 'Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])
        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
            df['id'] = rowno
            df['projectid_id'] = pk
            MasterList.objects.filter(id=rowno).update(**df)
        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                            df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['projectid_id'] = pk
            MasterList.objects.filter(id=rowno+1).update(**df)
        # Update Transactions List
        fa_round = 'RD2'

        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,
                              fa_aligned_pick, fa_unique_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + \
            ' FA Compensation Pick' + '(' + reason + ')'

    if fa_pick_type == 'End of Second Round':
        # Find the last row that is a standard pick:

        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD2-Standard')].iloc[-1]

        fa_dict = {}
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,
                              fa_aligned_pick, fa_unique_pick, fa_insert_instructions]

        # create the line to insert:

        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': fa_team,
                             'Draft_Round': 'RD2', 'Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert below the rowno
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno+1]

        df['id'] = rowno
        df['projectid_id'] = pk

        MasterList.objects.filter(id=rowno).update(**df)

        # display(df)

        # Update transactions
        fa_round = 'RD2'
        fa_aligned_pick = ''
        fa_unique_pick = ''
        fa_insert_instructions = ''

        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + \
            ' FA Compensation Pick' + '(' + reason + ')'

    if fa_pick_type == 'Third Round':
        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        rowno = df.index[df['Display_Name_Detailed'] == fa_aligned_pick][0]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': fa_team, 'Draft_Round': 'RD3', 'Draft_Round_Int': 3,
                             'Pick_Group': str(v_current_year) + '-' + 'RD3-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])

        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]

            df['id'] = rowno

            df['projectid_id'] = pk
            MasterList.objects.filter(id=rowno).update(**df)
        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno+1).update(**df)

        # Update Transactions List
        fa_round = 'RD3'

        fa_dict = {}
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,
                              fa_aligned_pick, fa_unique_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + \
            ' FA Compensation Pick' + '(' + reason + ')'

    if fa_pick_type == 'Custom Fixed Position':
        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        rowno = df.index[df['Display_Name_Detailed'] == fa_aligned_pick][0]
        # create the line to insert:
        fa_unique_pick = df.loc[df.Display_Name_Detailed ==
                                fa_aligned_pick, 'Unique_Pick_ID'].iloc[0]

        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': fa_team, 'Draft_Round': fa_round,
                             'Pick_Group': str(v_current_year) + '-' + fa_round + '-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])
        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
            df['id'] = rowno
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno).update(**df)
        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)

            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno+1).update(**df)

        # Update Transactions List

        fa_dict = {}
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,
                              fa_aligned_pick, fa_unique_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + \
            ' FA Compensation Pick' + '(' + reason + ')'

        new_df = []

    df = dataframerequest(request, pk)
    udpatedf = update_masterlist(df)

    iincreament_id = 1
    for index, updaterow in udpatedf.iterrows():
        FA_v2_data = dict(updaterow)
        team = Teams.objects.get(id=updaterow.TeamName)
        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = FA_v2_data['Overall_Pick']
        Project1 = Project.objects.get(id=pk)
        FA_v2_data['Previous_Owner'] = team
        FA_v2_data['TeamName'] = team
        FA_v2_data['Original_Owner'] = Original_Owner
        FA_v2_data['Current_Owner'] = Current_Ownerr
        FA_v2_data['projectid'] = Project1
        FA_v2_data['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        FA_v2_data['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(FA_v2_data['Display_Name'])

        FA_v2_data['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        FA_v2_data['Display_Name_Short'] = str(Overall_pickk) + '  ' + str(Current_Ownerr) + ' (Origin: ' + str(Original_Owner) + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        FA_v2_data['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName
        MasterList.objects.filter(id=iincreament_id).update(**FA_v2_data)
        iincreament_id += 1

     # variables for transactions dict
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')

    fa_dict = {fa_team: [fa_pick_type, fa_round, reason,
                         fa_aligned_pick, fa_unique_pick, fa_insert_instructions]}
    fa_description = fa_team + ' received a ' + fa_pick_type + \
        ' FA Compensation Pick' + '(' + reason + ')'
    # Exporting trade to the transactions df
    FA_v2_transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'FA_Compensation', 'Transaction_Details': fa_dict, 'Transaction_Description': fa_description, 'projectId': pk})

    obj = Transactions.objects.latest('id')
    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='FA_Compensation',
        Transaction_Details=fa_dict,
        Transaction_Description=fa_description,
        projectId=obj.id

    )
    count = Transactions.objects.filter().count()
    Transactions.objects.filter(id=obj.id).update(Transaction_Number=count)
    call_FA_Compensation(FA_v2_transaction_details)
    return Response({'success': 'add_FA_compensation_v2 has been Created'}, status=status.HTTP_201_CREATED)


def manual_pick_move_inputs(request, pk):

    data = request.data
    pick_move_team = data.get('teamid')
    reason = data.get('reason')
    pick_destination_round = data.get('round')
    pick_being_moved = data.get('pick_being_moved')
    pick_destination = data.get('pick_moved_to')
    pick_move_insert_instructions = data.get('instructions')

    df = dataframerequest(request, pk)
    masterlist = df

    pick_move_obj = MasterList.objects.get(id=pick_being_moved)
    pick_being_moved_val = pick_move_obj.Display_Name_Detailed

    pick_des_obj = MasterList.objects.get(id=pick_destination)
    pick_destination_val = pick_des_obj.Display_Name_Detailed
    # Unique Pick of pick being moved and the destination:
    pick_being_moved_unique_pick = masterlist.loc[masterlist.Display_Name_Detailed.astype(str) ==
                                                  pick_being_moved_val, 'Unique_Pick_ID'].iloc[0]
    pick_destination_unique_pick = masterlist.loc[masterlist.Display_Name_Detailed ==
                                                  pick_destination_val, 'Unique_Pick_ID'].iloc[0]

    return masterlist, pick_move_team, reason, pick_being_moved_val, pick_destination_round, pick_destination_val, pick_move_insert_instructions, pick_being_moved_unique_pick, pick_destination_unique_pick


@api_view(['POST'])
@permission_classes([AllowAny])
def manual_pick_move(request, pk):

    masterlist, pick_move_team, reason, pick_being_moved_val, pick_destination_round, pick_destination_val, pick_move_insert_instructions, pick_being_moved_unique_pick, pick_destination_unique_pick = manual_pick_move_inputs(
        request, pk)
    df = masterlist
    manual_move_dict = {}
    current_date = date.today()
    v_current_year = current_date

    manual_pick_move_type = 'Manual Pick Move'
    # Execute the Pick Move:

    # Find row number of pick shuffled
    rowno_pick_being_moved = df.index[df.Display_Name_Detailed ==
                                      pick_being_moved_val][0]

    # Find the row number of where the pick should be inserted:
    rowno_pick_destination = df.index[df.Display_Name_Detailed ==
                                      pick_destination_val][0]
    # Execute Move:
    if pick_move_insert_instructions == 'Before':
        # Insert pick to the row before the destination:
        df = pd.concat([df.iloc[:rowno_pick_destination], df.iloc[[
                       rowno_pick_being_moved]], df.iloc[rowno_pick_destination:]]).reset_index(drop=True)
        # df = df.iloc[rowno_pick_destination]
        # MasterList.objects.filter(id=rowno_pick_destination).update(**df)

    else:
        # Insert After the destination pick:
        df = pd.concat([df.iloc[:rowno_pick_destination + 1], df.iloc[[rowno_pick_being_moved]],
                       df.iloc[rowno_pick_destination + 1:]]).reset_index(drop=True)
        # df = df.iloc[rowno_pick_destination+1]
        # MasterList.objects.filter(id=rowno_pick_destination+1).update(**df)

    # Find row number to delete and execute delete:
    df.drop(rowno_pick_being_moved, axis=0, inplace=True)

    # If needing to update pick numbers after the delete
    df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
    library_AFL_Draft_Points = df['AFL_Points_Value']
    df['AFL_Points_Value'] = df['Overall_Pick'].map(
        library_AFL_Draft_Points).fillna(0)
    # get new overall pick number:
    new_pick_no = df.loc[df.Display_Name_Detailed ==
                         pick_being_moved_val, 'Overall_Pick'].iloc[0]

    # Reset index Again
    df = df.reset_index(drop=True)

    # Changing the names of some key details:
    # Change system note to describe action
    df['System_Note'].mask(df['Display_Name_Detailed'] ==
                           pick_being_moved_val, 'Manually Moved Pick', inplace=True)
    library_round_map = df['Draft_Round']
    # Change the draft round
    pick_destination_round_int = library_round_map.get(pick_destination_round)

    draft_round_int = df['Draft_Round_Int'].mask(df['Display_Name_Detailed'].astype(
        str) == str(pick_being_moved_val), pick_destination_round_int, inplace=True)

    df['Draft_Round'].mask(df['Display_Name_Detailed'] ==
                           pick_being_moved_val, pick_destination_round, inplace=True)

    df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick_being_moved_val, str(
        v_current_year) + '-RD' + pick_destination_round + '-ManualPickMove', inplace=True)

    df['Reason'].mask(df['Display_Name_Detailed'] ==
                      pick_being_moved_val, reason, inplace=True)

    df = update_masterlist(df)

    iincreament_id = 1
    for index, updaterow in df.iterrows():
        manualpickmove_dict = dict(updaterow)
        team = Teams.objects.get(id=updaterow.TeamName)
        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = manualpickmove_dict['Overall_Pick']

        Project1 = Project.objects.get(id=pk)
        manualpickmove_dict['Previous_Owner'] = previous_owner
        team = Teams.objects.get(id=updaterow.TeamName)
        manualpickmove_dict['TeamName'] = team
        manualpickmove_dict['Original_Owner'] = Original_Owner
        manualpickmove_dict['Current_Owner'] = Current_Ownerr
        manualpickmove_dict['projectid'] = Project1

        if manualpickmove_dict['Draft_Round_Int'] == None:

            manualpickmove_dict['Draft_Round_Int'] = ''
        else:
            pass

        manualpickmove_dict['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        manualpickmove_dict['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(manualpickmove_dict['Display_Name'])

        manual_move_dict['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        manualpickmove_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        manualpickmove_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        MasterList.objects.filter(
            id=iincreament_id).update(**manualpickmove_dict)

        iincreament_id += 1

    # Record Transaction:
    # Update Transactions List

    manual_move_dict = {pick_move_team: [manual_pick_move_type, pick_being_moved_val, reason, pick_destination_round,
                                         pick_destination_val, pick_move_insert_instructions, pick_being_moved_unique_pick, pick_destination_unique_pick, new_pick_no]}

    manual_move_description = pick_being_moved_val + \
        ' has been manually moved to pick ' + new_pick_no.astype(str)

    # variables for transactions dict
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')

    # Exporting trade to the transactions df
    obj = Project.objects.get(id=pk)
    transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Manual_Pick_Move', 'Transaction_Details': manual_move_dict, 'Transaction_Description': manual_move_description, 'projectId': obj.id})
    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Manual_Pick_Move',
        Transaction_Details=manual_move_dict,
        Transaction_Description=manual_move_description,
        projectId=obj.id

    )
    last_inserted_obj = Transactions.objects.latest('id')
    last_inserted_id = last_inserted_obj.id
    Transactions.objects.filter(id=last_inserted_id).update(
        Transaction_Number=last_inserted_id)
    call_manual_pick_move(transaction_details)
    return Response({'success': 'Manual Pick Move has been Created'}, status=status.HTTP_201_CREATED)


def call_drafted_player(transactions):
    return transactions


def call_add_father_son(transactions):
    return transactions


def call_add_draft_night_selection(transactions):
    return transactions


def call_manual_pick_move(transactions):
    return transactions


# ################### Visualisations Api's #########################################
@api_view(['GET'])
@permission_classes([AllowAny])
def Visualisations(request, pk):
    # call masterlist dataframe
    df = dataframerequest(request, pk)
    masterlist = df.fillna('')
    # call players dataframe
    players = playerdataframe(request, pk)
    # call trade dataframe
    trades = tradesdataframe(request, pk)
    # call transactions dataframe
    transactions = transactionsdataframe(request, pk)
    current_day = date.today()
    v_current_year = current_day.year
    v_current_year_plus1 = v_current_year+1
    v_team_name = masterlist['TeamName']

    data_dashboard_trade_offers = {}
    data_current_year_club_picks = {}
    data_trade_offers = {}
    data_transaction_list = {}
    data_completed_trades = {}
    draft_player_dict = {}
    data_dashboard_draftboard = {}

    # Current Year Picks to a List:
    data_current_year_club_picks['data_current_year_club_picks'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year)) & (
        masterlist.Current_Owner.astype(int) == v_team_name.astype(int))].Display_Name_Mini.to_dict()

    # Current Year Picks to a List:
    data_next_year_club_picks = {}

    data_next_year_club_picks['data_next_year_club_picks'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year_plus1)) & (
        masterlist.Current_Owner.astype(int) == v_team_name.astype(int))].Display_Name_Mini.to_dict()

    # Dashboard page Draft Board
    if players.empty:
        pass
    else:
        data_dashboard_draftboard_dict = {}
        data_dashboard_draftboard_dict['data_dashboard_draftboard'] = players[[
            'FirstName', 'LastName', 'Position_1', 'Rank']].sort_values(by='Rank', ascending=True)
# Dashboard Page trade Offers
    if trades.empty:
        pass
    else:
        data_dashboard_trade_offers['data_dashboard_trade_offers'] = trades[[
            'Trade_Partner', 'Trading_Out', 'Trading_In', 'Points_Diff', 'Notes']]
    # Dashboard Page Transactions
    if transactions.empty:
        pass
    else:

        data_transaction_list['data_transaction_list'] = transactions[[
            'Transaction_Number', 'Transaction_Type', 'Transaction_Description']]
    ##### DRAFT PICKS WEBPAGE #####

    # Current Year Round by Round:
    current_year_round_dict = {}
    current_year_round_dict['data_current_year_rd1'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year)) & (masterlist.Draft_Round.astype(str) == 'RD1')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    current_year_round_dict['data_current_year_rd2'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year)) & (masterlist.Draft_Round.astype(str) == 'RD2')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    current_year_round_dict['data_current_year_rd3'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year)) & (masterlist.Draft_Round.astype(str) == 'RD3')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    current_year_round_dict['data_current_year_rd4'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year)) & (masterlist.Draft_Round.astype(str) == 'RD4')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    current_year_round_dict['data_current_year_rd5'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year)) & (masterlist.Draft_Round.astype(str) == 'RD5')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    current_year_round_dict['data_current_year_rd6'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year)) & (masterlist.Draft_Round.astype(str) == 'RD6')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]

    # Next Year Round by Round:
    next_year_round_dict = {}
    next_year_round_dict['data_next_year_rd1'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year_plus1)) & (masterlist.Draft_Round.astype(str) == 'RD1')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    next_year_round_dict['data_next_year_rd2'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year_plus1)) & (masterlist.Draft_Round.astype(str) == 'RD2')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    next_year_round_dict['data_next_year_rd3'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year_plus1)) & (masterlist.Draft_Round.astype(str) == 'RD3')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    next_year_round_dict['data_next_year_rd4'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year_plus1)) & (masterlist.Draft_Round.astype(str) == 'RD4')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    next_year_round_dict['data_next_year_rd5'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year_plus1)) & (masterlist.Draft_Round.astype(str) == 'RD5')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    next_year_round_dict['data_next_year_rd6'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year_plus1)) & (masterlist.Draft_Round.astype(str) == 'RD6')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]

    # Order of Entry Table
    data_order_of_entry = {}
    data_order_of_entry['data_order_of_entry'] = masterlist[(masterlist.Year.astype(int) == int(
        v_current_year_plus1))][['TeamName', 'Overall_Pick', 'Club_Pick_Number', 'AFL_Points_Value']].sort_values(by='Overall_Pick')
    data_order_of_entry['data_order_of_entry'] = pd.crosstab(
        data_order_of_entry['data_order_of_entry']['TeamName'], data_order_of_entry['data_order_of_entry']['Club_Pick_Number'], values=data_order_of_entry['data_order_of_entry']['Overall_Pick'], aggfunc=sum)

    # Draft Assets Graph - Bar Graph
    data_draft_assets_graph = {}
    data_draft_assets_graph['data_draft_assets_graph'] = masterlist.groupby(
        ['Current_Owner_Short_Name', 'Year'])['AFL_Points_Value'].sum()

    ##### Full List of Draft Picks #####
    data_full_masterlist = {}
    data_full_masterlist['data_full_masterlist'] = masterlist[['Year', 'Draft_Round', 'Overall_Pick', 'TeamName', 'PickType',
                                                               'Original_Owner', 'Current_Owner', 'Previous_Owner', 'AFL_Points_Value', 'Club_Pick_Number']]

    ##### TRADE ANALYSER WEBPAGE #####

    # Trade Suggestion table (still in development)
    # Trade Offers
    if trades.empty:
        pass
    else:

        data_trade_offers['data_trade_offers'] = trades[['Trade_Partner', 'Trading_Out',
                                                         'Points_Out', 'Trading_In', 'Points_In', 'Points_Diff', 'Notes']]

    # List of completed trades
    if transactions.empty:
        pass
    else:

        data_completed_trades['data_completed_trades'] = transactions[(
            transactions.Transaction_Type == 'Trade')]['Transaction_Description']

    ##### DRAFT BOARD WEBPAGE #####
    if players.empty:
        pass
    else:
        # Draft Player List - Would like some fields to be updateable here:

        draft_player_dict['data_player_list'] = players[['FirstName', 'LastName', 'Height', 'Weight',
                                                         'club', 'State', 'Position_1', 'Position_2', 'Rank', 'Tier', 'Notes']]
        # Draft Tiers
        draft_player_dict['data_draft_tier_1'] = players[(players.Tier.astype(int) == 1)][[
            'FirstName', 'LastName', 'club', 'Position_1']]
        draft_player_dict['data_draft_tier_2'] = players[(players.Tier.astype(int) == 2)][[
            'FirstName', 'LastName', 'club', 'Position_1']]
        draft_player_dict['data_draft_tier_3'] = players[(players.Tier.astype(int) == 3)][[
            'FirstName', 'LastName', 'club', 'Position_1']]
        draft_player_dict['data_draft_tier_4'] = players[(players.Tier.astype(int) == 4)][[
            'FirstName', 'LastName', 'club', 'Position_1']]
        draft_player_dict['data_draft_tier_5'] = players[(players.Tier.astype(int) == 5)][[
            'FirstName', 'LastName', 'club', 'Position_1']]

        # Ranking View

        data_dashboard_draftboard['data_dashboard_draftboard'] = players[[
            'FirstName', 'LastName', 'Position_1', 'Rank']].sort_values(by='Rank', ascending=True)
    # For Each project:
    # Comparison 1 picks
    comparison_1_club_picks_dict = {}
    comparison_1_club_picks_dict['comparison_1_club_picks'] = masterlist[(masterlist.Year.astype(int) == v_current_year) & (
        masterlist.Current_Owner.astype(int) == v_team_name)].Display_Name_Mini.to_list()

    # Current Year Picks to a List:
    comparison_1_club_picks_dict['comparison_1_club_picks_next_year'] = masterlist[(masterlist.Year.astype(int) == v_current_year_plus1) & (
        masterlist.Current_Owner.astype(int) == v_team_name)].Display_Name_Mini.to_list()

    # Dashboard Page masterlist:
    comparison_1_club_picks_dict['comparison_1_masterlist'] = masterlist[[
        'Year', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]

    # Menu Bar - List for each club and their picks
    data_menu_bar_picks = {}
    data_menu_bar_picks['data_menu_bar_picks'] = masterlist.groupby('Current_Owner_Short_Name')[
        'Display_Name_Detailed'].agg(list).to_dict()
    visualisations_data = [data_current_year_club_picks, data_next_year_club_picks, data_dashboard_draftboard, data_dashboard_trade_offers, data_transaction_list, current_year_round_dict, next_year_round_dict,
                           data_order_of_entry, data_full_masterlist, data_trade_offers, data_completed_trades, draft_player_dict, comparison_1_club_picks_dict, data_menu_bar_picks]

    return Response({'response': visualisations_data}, status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
# ##################### Code Done by Abhishek ########################
def update_player_details(request):
    data = request.data
    playerid = data.get('playerid')
    player_details = data.get('player_details')
    Players.objects.filter(id=playerid).update(player_details)


def add_trade_v3_inputs(request, pk):

    # define lists of picks and players traded out:.
    # team1 trading out
    team1_trades_picks = []
    team1_trades_players = []
    team1_trades_pick_names = []

    # team2 trading out:
    team2_trades_picks = []
    team2_trades_players = []
    team2_trades_pick_names = []

    data = request.data
    team1 = data.get('teamid1')
    team2 = data.get('teamid2')

    df = dataframerequest(request, pk)
    masterlist = df
    picks_trading_out_team1_obj = data.get('pickid1')
    picks_trading_out_team1 = picks_trading_out_team1_obj[0]['value']
    players_trading_out_team1 = str(len(data.get('player1'))) or ''
    player_id = ''
    if players_trading_out_team1 is not None:
        for i in range(int(players_trading_out_team1)):
            player_obj = Players.objects.get(FirstName=players_trading_out_team1)
            player_id = player_obj.id
    # Getting the pick(s) name for the pick(s) traded out:

    if int(picks_trading_out_team1) > 0:
        # Priniting the available picks for team 1 to trade out
        for i in range(picks_trading_out_team1 or 0):
           
            # get unique pick name
            pick_trading_out_team1_str = masterlist.loc[masterlist.Current_Owner.astype(int) == int(picks_trading_out_team1), 'Display_Name_Detailed']
            unique_name = masterlist.loc[masterlist.Display_Name_Detailed.astype(
                str) == str(pick_trading_out_team1_str), 'Unique_Pick_ID']
            team1_trades_pick_names.append(unique_name)
    else:
        pass

    # Getting the pick(s) name for the pick(s) traded out:
    if player_id !='':
        # Priniting the available picks for team 1 to trade out
        for i in range(int(player_id)):

            player_trading_out_team1_obj = Players.objects.filter(
                id=player_id).values()

        for i in range(int(player_id) or 0):
            for k in player_trading_out_team1_obj:
                team1_trades_players.append(k['Full_Name'])
    else:
        pass

    picks_trading_out_team2_obj = data.get('pickid2')
    picks_trading_out_team2 = picks_trading_out_team2_obj[0]['value']
    players_trading_out_team2_id = str(data.get('player2')) or ''
    player_id2 = ''
    if players_trading_out_team2 is not None:
        player_obj = Players.objects.get(FirstName=players_trading_out_team2)
        player_id2 = player_obj.id

    if player_id2 !='':
        # Priniting the available picks for team 1 to trade out
        for i in range (picks_trading_out_team2):

            team2picks = masterlist[masterlist['Current_Owner'].astype(
                int) == int(team2)]['Display_Name_Detailed'].tolist()
                
            for i in range(int(picks_trading_out_team2)):
                pick_trading_out_team2 = data.get('pickid2')
                team2_trades_picks.append(pick_trading_out_team2)
                pick_trading_out_team2_str = masterlist.loc[masterlist.Current_Owner.astype(int) == int(picks_trading_out_team2), 'Display_Name_Detailed']
                # get unique pick name
                unique_name = masterlist.loc[masterlist.Display_Name_Detailed.astype(
                    str) == str(pick_trading_out_team2_str), 'Unique_Pick_ID']
                team2_trades_pick_names.append(unique_name)
    else:
        pass

    # Getting the pick(s) name for the pick(s) traded out:
 
    if int(player_id2) > 0 or '':
        # Priniting the available picks for team 1 to trade out
        for i in range(int(player_id)):
            player2 = data.get('player2')
            player_trading_out_team2 = Players.objects.filter(
                id=player_id).values()
            for i in range(int(player_id)):
                for k in player_trading_out_team2:
                    team2_trades_players.append(k['Full_Name'])
    else:
        pass
    return masterlist, team1, team2, team1_trades_picks, team1_trades_players, team2_trades_picks, team2_trades_players, team1_trades_pick_names, team2_trades_pick_names


@api_view(['POST'])
@permission_classes([AllowAny, ])
def add_trade_v3(request, pk):

   ################### TRADE EXECUTION ############################

    # Trade facilitation - Swapping current owner names & Applying Most Recent Owner First:

    ##### Team 1 receiving from Team 2 #####
    # Loop for each pick that team 2 is trading out to team 1:

    masterlist, team1, team2, team1_trades_picks, team1_trades_players, team2_trades_picks, team2_trades_players, team1_trades_pick_names, team2_trades_pick_names = add_trade_v3_inputs(
        request, pk)
    current_date = date.today()
    v_current_year = current_date.year
    for team2pickout in team2_trades_picks:
        # Changing the previous owner name
        masterlist['Previous_Owner'].mask(masterlist['Display_Name_Detailed'].astype(
            str) == str(team2pickout), masterlist['Current_Owner'], inplace=True)
        # Executing change of ownership
        masterlist['Current_Owner'].mask(masterlist['Display_Name_Detailed'].astype(
            str) == str(team2pickout), team1, inplace=True)

    ##### Team 2 receiving from Team 1 #####
    # Loop for each pick that team 1 is trading out to team 2:
    for team1pickout in team1_trades_picks:
        # Changing the previous owner name
        masterlist['Previous_Owner'].mask(masterlist['Display_Name_Detailed'].astype(
            str) == str(team1pickout), masterlist['Current_Owner'], inplace=True)
        # print( masterlist['Previous_Owner'])
        # Executing change of ownership
        masterlist['Current_Owner'].mask(
            masterlist['Display_Name_Detailed'] == team1pickout, team2, inplace=True)

    # ###########  Call Update masterlist ############
    udpatedf = update_masterlist(masterlist)
    incremented_id = 1
    for index, updaterow in udpatedf.iterrows():
        trade_dict = dict(updaterow)

        team = Teams.objects.get(id=updaterow.TeamName)

        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = trade_dict['Overall_Pick']

        Project1 = Project.objects.get(id=pk)
        trade_dict['Previous_Owner'] = previous_owner
        team = Teams.objects.get(id=updaterow.TeamName)
        trade_dict['TeamName'] = team
        trade_dict['Original_Owner'] = Original_Owner
        trade_dict['Current_Owner'] = Current_Ownerr
        trade_dict['projectid'] = Project1

        trade_dict['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        trade_dict['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(trade_dict['Display_Name'])

        trade_dict['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        trade_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        trade_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        MasterList.objects.filter(id=incremented_id).update(**trade_dict)
        incremented_id += 1
    ################### RECORDING TRANSACTION ############################
    # Summarising what each team traded out:
    team1_out = team1_trades_players + team1_trades_picks
    team2_out = team2_trades_players + team2_trades_picks

    # variables for transactions dict
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')

    # Creating a dict of what each team traded out
    trade_dict_full = {}
    trade_dict = {team1: team1_out, team2: team2_out}
    trade_dict_full[team1] = [team1_trades_players,
                              team1_trades_picks, team1_trades_pick_names]
    trade_dict_full[team2] = [team2_trades_players,
                              team2_trades_picks, team2_trades_pick_names]

    # Creating a written description
    trade_description = team1 + ' traded ' + \
        ','.join(str(e) for e in team1_out) + ' & ' + team2 + \
        ' traded ' + ','.join(str(e) for e in team2_out)

    # Exporting trade to the transactions df
    Proj_obj = Project.objects.get(id=pk)
    project_id = Proj_obj.id
    transaction_details = pd.DataFrame(
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Trade',
         'Transaction_Details': trade_dict_full,
         'Transaction_Description': trade_description})
    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Trade',
        Transaction_Details=trade_dict_full,
        Transaction_Description=trade_description,
        projectId=project_id
    )

    transactions_obj = Transactions.objects.latest('id')
    last_Transations_id = transactions_obj.id
    Transactions.objects.filter(id=last_Transations_id).update(
        Transaction_Number=last_Transations_id)
    call_add_trade(transaction_details)
    return Response({'success': 'Add-Trade-v3 Created Successfuly'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def update_ladder(request, pk):
    ################ CREATING MASTERLIST FROM SCRATCH #######################
    # First stage bringing in the ordered ladder list which will be generated from the Settings page:
    current_day = date.today()
    v_current_year = current_day.year
    ladder_list_current_yr = v_current_year
    ladder_list_current_yr_plus1 = ladder_list_current_yr+1
    v_current_year_plus1 = v_current_year+1
    updated_ladderlist_current_year = ''
    updated_ladderlist_current_year_plus1 = []
    data = request.data
    update_ladder_teamid = data.get('update_ladder_teamid')
    df = dataframerequest(request, pk)
    Query = Update_ladder_teams.objects.filter(
        id=update_ladder_teamid).values()
    for data in Query:
        updated_ladderlist_current_year = data['updated_ladderlist_TeamName']
    updated_ladderlist_current_year_plus1 = updated_ladderlist_current_year

    library_AFL_Team_Names = df['TeamName']
    # updated_ladder_current_year, updated_ladder_current_year_plus1 = import_ladder_dragdrop_V2(
    #     ladder_list_current_yr, ladder_list_current_yr_plus1, library_AFL_Team_Names, v_current_year, v_current_year_plus1)
    masterlist = df
    library_round_map = masterlist['Draft_Round']
    # Using the create masterlist code with the updated ladders as inputs:
    new_masterlist = update_masterlist(df)

    transactions = []
    Get_Transactions_obj = Transactions.objects.filter().values()
    for transactions_data in Get_Transactions_obj:
        transactions.append(transactions_data)
    new_transactions = pd.DataFrame(transactions)
    if len(transactions) == 0:
        pass
    else:
        # looping over each row to extract the keys and return their current position & value:
        for row in transactions:

            #### Trade Transaction ####
            if row['Transaction_Type'] == 'Trade':

                # print(row.Transaction_Details)

                # Unpack transaction_details
                details = row['Transaction_Details']
                # Upack the cell string:
                details_dict = ast.literal_eval(details)
                # Save keys and values to be used as inputs into the trade function:
                team1, team2 = details_dict.keys()

                team1_trades_players, team1_trades_picks = details_dict[team1]
                team2_trades_players, team2_trades_picks = details_dict[team2]

                team1_trades_pick_names = team1_trades_picks
                team2_trades_pick_names = team2_trades_picks

                # reset team1 and team2 trades picks to get the updated pick names from their unique names
                team1_trades_picks = []
                team2_trades_picks = []
                # loop to get updated names and append to list
                for pick in team1_trades_pick_names:

                    pick_as_str = "".join(pick)
                    t1_pick = masterlist.loc[masterlist.Unique_Pick_ID.astype(
                        str) == str(pick_as_str), 'Display_Name_Detailed']

                    team1_trades_picks.append(t1_pick)

                for pick in team2_trades_pick_names:

                    t2_pick = masterlist.loc[masterlist.Unique_Pick_ID.astype(
                        str) == str(pick), 'Display_Name_Detailed']
                    team2_trades_picks.append(t2_pick)

                # Execute Function and add to the transaction list:
                new_transactions = call_add_trade(transactions)

                new_masterlist = update_masterlist(new_masterlist)

             #### Priority Pick Transaction ####
            if row['Transaction_Type'] == 'Priority_Pick':

                # Unpack transaction_details
                details = row['Transaction_Details']

                # Upack the cell string:
                details_dict = ast.literal_eval(details)

                # Extract the first (only) key in dictionary for the team:

                pp_team = list(details_dict.keys())[0]
                # Extract the rest of the values:
                pp_pick_type, pp_round, reason, pp_aligned_pick, pp_unique_pick, pp_insert_instructions = details_dict[
                    pp_team]

                # now need to use the unique pick name to then find the aligned pick in the new_masterlist:
                # Now find the new aligned pick name from the unique pick id if there is an aligned pick:

                # if pp_unique_pick != '':
                #     pp_aligned_pick = new_masterlist.loc[new_masterlist.Display_Name_Detailed.astype(
                #         str) == str(pp_unique_pick), 'Display_Name_Detailed'].iloc[0]

                # else:
                #     pass
                # Execute Function and add to the transaction list:
                new_transactions = call_priority_pick_v2(transactions)

                new_masterlist = update_masterlist(new_masterlist)

            if row['Transaction_Type'] == 'FA_Compensation':
                # Unpack transaction_details
                details = row['Transaction_Details']
                # Upack the cell string:
                details_dict = ast.literal_eval(details)
                # Extract the first (only) key in dictionary for the team:
                fa_team = list(details_dict.keys())[0]

                for _s in list(details_dict.values()):

                    if _s[0] == 'End of First Round':
                        fa_pick_type, reason = details_dict[fa_team]

                    else:
                        # Extract the rest of the values:
                        fa_pick_type, fa_round, reason, fa_uniquepick, fa_insert_instructions = details_dict[
                            fa_team]

                        fa_aligned_pick = new_masterlist.loc[new_masterlist.Unique_Pick_ID ==
                                                             fa_uniquepick, 'Display_Name_Detailed']
                        #
                    # Execute Function and add to the transaction list:
                    new_transactions = call_FA_Compensation(
                        transactions)
                    new_masterlist = update_masterlist(new_masterlist)

            if row['Transaction_Type'] == 'Academy_Bid_Match':
                # Unpack transaction_details
                details = row['Transaction_Details']
                # Upack the cell string:
                details_dict = ast.literal_eval(details)

                # Get details
                academy_team = list(details_dict.keys())[0]
                academy_pick_type, academy_bid, academy_bid_pick_no, academy_player = details_dict[
                    academy_team]
                # Check to make sure the bid pick is not the same team. If it is, then move the bid to the next pick:

                academy_bid_pick_no = np.where(new_masterlist.loc[new_masterlist.Overall_Pick.astype(str) == str(
                    academy_bid_pick_no), 'Current_Owner'].iloc[0] == academy_team, int(academy_bid_pick_no) + 1, academy_bid_pick_no)
                # Updating the official pick name based off the academy_pick_no
                academy_bid = new_masterlist.loc[new_masterlist.Overall_Pick.astype(
                    int) == int(academy_bid_pick_no), 'Display_Name_Detailed'].iloc[0]

                # Execute Function and add to the transaction list:
                new_transactions = call_academy_bid_v2(new_transactions)

                new_masterlist = update_masterlist(new_masterlist)

            if row['Transaction_Type'] == 'FS_Bid_Match':
                # Unpack transaction_details
                details = row['Transaction_Details']
                # Upack the cell string:
                details_dict = ast.literal_eval(details)
                # Get details
                fs_team = list(details_dict.keys())[0]

                fs_pick_type, fs_bid, fs_bid_pick_no, fs_player = details_dict[fs_team]

                # Check to make sure the bid pick is not the same team. If it is, then move the bid to the next pick:
                fs_bid_pick_no = np.where(new_masterlist.loc[new_masterlist.Overall_Pick.astype(int) == int(
                    fs_bid_pick_no), 'Current_Owner'].iloc[0] == fs_team, int(fs_bid_pick_no) + 1, fs_bid_pick_no)
                # Updating the official pick name based off the academy_pick_no
                fs_bid = new_masterlist.loc[new_masterlist.Overall_Pick.astype(
                    int) == int(fs_bid_pick_no), 'Display_Name_Detailed'].iloc[0]
                # Execute Function and add to the transaction list:
                new_transactions = call_add_father_son(new_transactions)
                new_masterlist = update_masterlist(new_masterlist)

            if row['Transaction_Type'] == 'NGA_Bid_Match':
                # Unpack transaction_details
                details = row['Transaction_Details']

                # Upack the cell string:
                details_dict = ast.literal_eval(details)
                # Get details
                nga_team = list(details_dict.keys())[0]

                nga_pick_type, nga_bid, nga_bid_pick_no, nga_player = details_dict[nga_team]

                # Check to make sure the bid pick is not the same team. If it is, then move the bid to the next pick:
                nga_bid_pick_no = np.where(new_masterlist.loc[new_masterlist.Overall_Pick.astype(int) == int(nga_bid_pick_no),
                                           'Current_Owner'].iloc[0] == nga_team, int(nga_bid_pick_no) + 1, nga_bid_pick_no)
                # Updating the official pick name based off the academy_pick_no
                nga_bid = new_masterlist.loc[new_masterlist.Overall_Pick.astype(int) ==
                                             int(nga_bid_pick_no), 'Display_Name_Detailed'].iloc[0]

                # Check to make sure NGA bid is not before pick 40:
                nga_bid_pick_no = new_masterlist.loc[new_masterlist.Display_Name_Detailed.astype(int) ==
                                                     int(nga_bid), 'Overall_Pick'].iloc[0]
                # if nga_bid_pick_no < 21:
                #     print("NGA bid match invalid (Bid pick is inside 20)")
                #     sys.exit("Exiting Function")

                # Execute Function and add to the transaction list:
                new_transactions = call_nga_bid(new_transactions)
                new_masterlist = update_masterlist(new_masterlist)

            if row['Transaction_Type'] == 'Manual_Insert':
                # Unpack transaction_details
                details = row['Transaction_Details']
                # Upack the cell string:
                details_dict = ast.literal_eval(details)
                # Get details
                manual_team = list(details_dict.keys())[0]
                manual_pick_type, manual_round, reason, manual_aligned_pick, manual_insert_unique_pick, manual_insert_instructions = details_dict[
                    manual_team]
                manual_aligned_pick = new_masterlist.loc[new_masterlist.Unique_Pick_ID.astype(
                    str) == str(manual_insert_unique_pick), 'Display_Name_Detailed'].iloc[0]

                # Execute Function and add to the transaction list:
                new_transactions = call_manual_insert(new_transactions)
                new_masterlist = update_masterlist(new_masterlist)
            if row['Transaction_Type'] == 'Manual_Pick_Move':
                # Unpack transaction_details
                details = row['Transaction_Details']
                # Upack the cell string:
                details_dict = ast.literal_eval(details)
                # Get details
                pick_move_team = list(details_dict.keys())[0]
                manual_pick_move_type, pick_being_moved, reason, pick_destination_round, pick_destination, pick_move_insert_instructions, pick_being_moved_unique_pick, pick_destination_unique_pick, new_pick_no = details_dict[
                    pick_move_team]

                pick_being_moved = new_masterlist.loc[new_masterlist['Unique_Pick_ID'].astype(
                    str) == str(pick_being_moved_unique_pick), 'Display_Name_Detailed']
                pick_destination = new_masterlist.loc[new_masterlist.Unique_Pick_ID.astype(
                    str) == str(pick_destination_unique_pick), 'Display_Name_Detailed'].iloc[0]

                # Execute Function and add to the transaction list:
                new_transactions = call_manual_pick_move(new_transactions)
                new_masterlist = update_masterlist(new_masterlist)

            if row['Transaction_Type'] == 'Drafted_Player':
                # Unpack transaction_details
                details = row['Transaction_Details']
                # Upack the cell string:
                details_dict = ast.literal_eval(details)
                # Get details
                team_name = list(details_dict.keys())[0]
                pick_round, overall_pick, player_taken = details_dict[team_name]
                # Updating the official pick name based off the academy_pick_no
                selected_pick = new_masterlist.loc[new_masterlist.Overall_Pick.astype(
                    int) == int(overall_pick), 'Display_Name_Detailed'].iloc[0]
                # Execute Function and add to the transaction list:
                new_transactions = call_add_draft_night_selection(
                    new_transactions)
                new_masterlist = update_masterlist(new_masterlist)
          # Drop duplicate rows and recount transaction number
        new_transactions = pd.DataFrame(new_transactions)
        new_transactions.drop_duplicates(
            subset='Transaction_Description', keep="first", inplace=True)
        new_transactions['Transaction_Number'] = np.arange(
            len(new_transactions)) + 1

        new_masterlist = update_masterlist(new_masterlist)
        iincreament_id = 1
        for index, updaterow in new_masterlist.iterrows():
            update_ladder_dict = dict(updaterow)
            team = Teams.objects.get(id=updaterow.TeamName)
            Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
            Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
            previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
            Overall_pickk = update_ladder_dict['Overall_Pick']

            Project1 = Project.objects.get(id=pk)
            update_ladder_dict['Previous_Owner'] = previous_owner
            team = Teams.objects.get(id=updaterow.TeamName)
            update_ladder_dict['TeamName'] = team
            update_ladder_dict['Original_Owner'] = Original_Owner
            update_ladder_dict['Current_Owner'] = Current_Ownerr
            update_ladder_dict['projectid'] = Project1

            update_ladder_dict['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
                None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

            update_ladder_dict['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
                updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(update_ladder_dict['Display_Name'])

            update_ladder_dict['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
                None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
                ' ' + str(Overall_pickk)

            update_ladder_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
                previous_owner + team.ShortName + \
                ')' if Original_Owner != Current_Ownerr else team.ShortName

            update_ladder_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
                previous_owner + team.ShortName + \
                ')' if Original_Owner != Current_Ownerr else team.ShortName

            MasterList.objects.filter(
                id=iincreament_id).update(**update_ladder_dict)

            iincreament_id += 1

        return Response({'success': 'success'}, status=status.HTTP_201_CREATED)


def update_ladder_teams(request):
    data = request.data
    teamid = data.get('teamid')
    team_value = data.get('team_val')
    Update_ladder_teams.objects.filter(id=teamid).update(
        updated_ladderlist_TeamName=team_value)
    return Response({'success': 'Team Name updated Successfully'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_draftee_player(request, pk):
    C_Name = Company.objects.filter().values('id', 'Name')
    user = request.data
    serializer = PlayersSerializer(data=user)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    last_inserted_id = serializer.data['id']
    User.objects.filter(id=last_inserted_id).update(uui=unique_id)
    return Response({'success': 'Player has been Created Successfuly'}, status=status.HTTP_201_CREATED)


def add_trade_offer_inputs(request):
    data = request.data
    v_team_name = data.get('teamid')
    Trade_Partner = data.get('Trade_Partner')
    Trading_Out_Num = data.get('Trading_Out_Num')
    Trading_Out_Num_Player = data.get('Trading_Out_Num_Player')
    pick_out_idd = data.get('pick_trading_out')
    player_trading_out = data.get('player_trading_out')
    pick_in_id = data.get('pick_trading_in')
    Trading_In_Num = data.get('Trading_In_Num')
    Trading_In_Num_Player = data.get('Trading_In_Num_Player')
    player_trading_in = data.get('player_trading_in')
    notes = data.get('notes')

    return v_team_name, Trade_Partner, notes, Trading_Out_Num, Trading_Out_Num_Player, pick_out_idd, player_trading_out, pick_in_id, Trading_In_Num, Trading_In_Num_Player, player_trading_in


def add_trade_offer(request, pk):

    df = []
    dfobj = MasterList.objects.filter(projectid=pk).values()
    for df_data in dfobj:
        df.append(df_data)
    v_team_name, Trade_Partner, notes, Trading_Out_Num, Trading_Out_Num_Player, pick_out_idd, player_trading_out, pick_in_id, Trading_In_Num, Trading_In_Num_Player, player_trading_in = add_trade_offer_inputs(
        request)
    masterlist = pd.DataFrame(df)

    Trading_Out = {}
    Trading_Out_Simple = []
    total_points_out = 0
    total_points_in = 0

    pick_trading_out_list = []
    pick_trading_in_list = []

    Trading_Out_Num_int = int(Trading_Out_Num)
    Trading_In_Num = int(Trading_Out_Num_Player)
    Trading_In_Num_Player_Num = int(Trading_In_Num_Player)
    # pick_in_id = masterlist.loc[masterlist.Display_Name_Detailed == pick_trading_in, 'Unique_Pick_ID'].iloc[0]
    MasterQuerytset = MasterList.objects.filter(
        id__in=[pick_out_idd, pick_in_id]).values()

    for masterlist_data in MasterQuerytset:
        if masterlist_data['id'] == int(pick_out_idd):
            pick_trading_out_list.append(
                masterlist_data['Display_Name_Detailed'])
        elif masterlist_data['id'] == int(pick_in_id):
            pick_trading_in_list.append(
                masterlist_data['Display_Name_Detailed'])

    pick_trading_out = "".join(pick_trading_out_list)
    pick_trading_in = "".join(pick_trading_in_list)

    if Trading_Out_Num is not None:
        for i in range(Trading_Out_Num_int):

            points_trading_out = masterlist.loc[masterlist.Display_Name_Detailed ==
                                                pick_trading_out, 'AFL_Points_Value'].iloc[0]
            pick_out_id = masterlist.loc[masterlist.Display_Name_Detailed ==
                                         pick_trading_out, 'Unique_Pick_ID'].iloc[0]

            Trading_Out[pick_out_id] = [points_trading_out, pick_out_id]
            Trading_Out_Simple.append(pick_trading_out)

    else:
        pass

    # Ask for which players to trade out:
    if Trading_Out_Num_Player is not None:
        for i in range(Trading_In_Num):

            Trading_Out['Player'] = [player_trading_out, 0]
            Trading_Out_Simple.append(player_trading_out)

    Trading_In = dict()
    Trading_In_Simple = []
    # print picks of trade partner

    if Trading_Out_Num is not None:
        for i in range(Trading_In_Num):

            points_trading_in = masterlist.loc[masterlist.Display_Name_Detailed ==
                                               pick_trading_in, 'AFL_Points_Value'].iloc[0]
            pick_in_id = masterlist.loc[masterlist.Display_Name_Detailed ==
                                        pick_trading_in, 'Unique_Pick_ID'].iloc[0]
            Trading_In[pick_in_id] = [pick_trading_in, points_trading_in]
            Trading_In_Simple.append(pick_trading_in)

    else:
        pass

    if Trading_In_Num_Player is not None:
        for i in range(Trading_In_Num_Player_Num):
            Trading_In['Player'] = [player_trading_in, 0]

    # loop to get the points for each pick going out

    for v in Trading_Out.values():

        total_points_out += int(v[0])

    # loop to get the points for each pick coming in

    for v in Trading_In.values():
        total_points_in += int(v[1])

    print("You will be trading out " + str(total_points_out) +
          "pts out and receiving " + str(total_points_in) + "pts in.")

    total_points_diff = total_points_in - total_points_out

    trades = pd.DataFrame({'Trade_Partner': Trade_Partner, 'Trading_Out': [Trading_Out_Simple], 'Trading_In': [Trading_In_Simple],
                           'Points_Out': total_points_out, 'Points_In': total_points_in,  'Points_Diff': total_points_diff,  'Notes': notes, 'System_Out': [Trading_Out], 'System_In': [Trading_In]}, index=[0])

    # Append to the trades dataframe
    append_df = pd.DataFrame({'Trade_Partner': Trade_Partner, 'Trading_Out': [Trading_Out_Simple], 'Trading_In': [Trading_In_Simple],
                              'Points_Out': total_points_out, 'Points_In': total_points_in,  'Points_Diff': total_points_diff,  'Notes': notes, 'System_Out': [Trading_Out], 'System_In': [Trading_In]}, index=[0]).shape

    # trades = pd.concat([append_df])

    return trades, masterlist, v_team_name


@api_view(['POST'])
@permission_classes([AllowAny])
def update_trade_offers(request, pk):
    trades_updated = ''
    trades, masterlist, v_team_name = add_trade_offer(request, pk)
    if trades.empty:
        pass
    else:
        # creating the new trades df to reaplace the old trades at the end of function
        trades_updated = pd.DataFrame(columns=['Trade_Partner', 'Trading_Out',
                                               'Trading_In', 'Points_Out', 'Points_In', 'Points_Diff',  'Notes', 'System_Out', 'System_In', 'Warning'])
        # looping over each row to extract the keys and return their current position & value:
        Trading_Out = dict()
        Trading_In = dict()
        Trading_Out_Simple = []
        Trading_In_Simple = []
        Trade_Warning = []
        for _, row in trades.iterrows():

            Trade_Partner = row.Trade_Partner
            Notes = row.Notes

            ##### Picks Traded Out ######
            # converting string back to a dictionary:
            d = ast.literal_eval(str(row.System_Out))
            for k in d:
                unique_pick_id = k
                if unique_pick_id == 'Player':

                    for player in d.values():

                        player_trading_out = player[0]

                        Trading_Out['Player'] = [player_trading_out, 0]

                        Trading_Out_Simple.append(player_trading_out)

                else:
                    updated_pick_name = masterlist.loc[masterlist.Unique_Pick_ID ==
                                                       unique_pick_id, 'Display_Name_Detailed'].iloc[0]

                    masterlist.rename(
                        columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)

                    masterlist.rename(
                        columns={'Previous_Owner_id': 'Previous_Owner'}, inplace=True)
                    updated_pick_pts = masterlist.loc[masterlist.Unique_Pick_ID ==
                                                      unique_pick_id, 'AFL_Points_Value'].iloc[0]

                    updated_pick_owner = masterlist.loc[masterlist.Unique_Pick_ID ==
                                                        unique_pick_id, 'Current_Owner'].iloc[0]
                    updated_recent_owner = masterlist.loc[masterlist.Unique_Pick_ID ==
                                                          unique_pick_id, 'Previous_Owner'].iloc[0]
                    if updated_pick_owner != v_team_name or updated_recent_owner == Trade_Partner:
                        warning = 'Trade is no longer valid'
                    else:
                        warning = ''

                    # Appending to dictionaries

                    Trade_Warning.append(warning)
                    Trading_In[unique_pick_id] = [
                        updated_pick_name, updated_pick_pts]

                    Trading_In_Simple.append(updated_pick_name)

                total_points_out = 0
                total_points_in = 0

                # loop to get the points for each pick going out
                for v in Trading_Out.values():
                    total_points_out += int(v[1])

                # loop to get the points for each pick coming in
                for v in Trading_In.values():
                    total_points_in += int(v[1])

                # Calculations for pick difference
                total_points_diff = total_points_in - total_points_out

                Trading_Out_list = []
                for trade_out_data in Trading_Out:
                    Trading_Out_list.append(trade_out_data)
                Trading_Out_as_str = "".join(Trading_Out_list)

                # Creating a new row to add to the updated trad
        obj = Project.objects.get(id=pk)

        append_df = pd.DataFrame({'Trade_Partner': Trade_Partner, 'Trading_Out': [Trading_Out_Simple], 'Trading_In': Trading_In_Simple,
                                  'Points_Out': total_points_out, 'Points_In': total_points_in,  'Points_Diff': total_points_diff,  'Notes': Notes, 'System_Out': [Trading_Out], 'System_In': [Trading_In], 'Warning': Trade_Warning, 'projectid': obj.id}, index=[0])

        trades_updated = pd.concat([trades_updated, append_df])
    # print(trades_updated)
    Tarde_dict = {}
    for index, updaterow in append_df.iterrows():
        Tarde_dict = dict(updaterow)

    Trades(**Tarde_dict).save()
    return Response({'success': 'success'}, status=status.HTTP_201_CREATED)


def add_nga_bid_inputs(request):

    bid_list = []
    data = request.data

    nga_player = data.get('playerid')
    nga_team_id = data.get('teamid')
    nga_bid_id = data.get('pickid')

    teamlist = []

    teamqueryset = Teams.objects.filter(id__in=[nga_team_id]).values()
    for teamvalues in teamqueryset:
        teamlist.append(teamvalues['TeamNames'])

    nga_team = "".join(teamlist)

    bidqueryset = MasterList.objects.filter(id__in=[nga_bid_id]).values()

    for bidvalues in bidqueryset:

        bid_list.append(bidvalues['Display_Name_Detailed'])

    nga_bid = "".join(bid_list)

    # Check to make sure NGA bid is not before pick 40:

    if int(nga_bid_id) < 21:

        print("NGA bid match invalid (Bid pick is inside 20)")
        sys.exit("Exiting Function")

        # Return variables for main function
    return nga_team_id, nga_player, nga_team, nga_bid


def call_nga_bid(transactions):
    return transactions


@api_view(['POST'])
@permission_classes([AllowAny])
def add_nga_bid(request, pk):
    current_day = date.today()
    v_current_year = current_day.year
    v_current_year_plus1 = v_current_year+1
    nga_team_id, nga_player, nga_team, nga_bid = add_nga_bid_inputs(request)
    df = dataframerequest(request, pk)
    # originals to be returned if cancelling bid:
    df_original = df.copy()
    deficit_subset = df.copy()
    df_subset = df.copy()

    df.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    df_subset.rename(
        columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)

    # Details of the bid

    nga_pts_value = df.loc[df.Display_Name_Detailed.astype(
        str) == str(nga_bid), 'AFL_Points_Value'].iloc[0]

    nga_bid_round = df.loc[df.Display_Name_Detailed ==
                           nga_bid, 'Draft_Round'].iloc[0]
    nga_bid_round_int = df.loc[df.Display_Name_Detailed ==
                               nga_bid, 'Draft_Round_Int'].iloc[0]
    nga_bid_team = df.loc[df.Display_Name_Detailed ==
                          nga_bid, 'Current_Owner'].iloc[0]
    nga_bid_pick_no = df.loc[df.Display_Name_Detailed.astype(
        str) == str(nga_bid), 'Overall_Pick'].iloc[0]

    nga_pick_type = 'NGA Bid Match'

    sum_line1 = str(nga_bid_team) + ' have placed a bid on a ' + str(nga_team) + \
        ' NGA player at pick ' + str(nga_bid_pick_no) + ' in ' + nga_bid_round

    # Creating a copy df of that teams available picks to match bid

    df_subset = df_subset[(df_subset.Current_Owner.astype(int) == int(nga_team_id)) & (df_subset.Year.astype(
        int) == int(v_current_year)) & (df_subset.Overall_Pick.astype(float) >= float(nga_bid_pick_no))]

    # Finding out the next pick the club owns in case the bid comes after 40:

    # nga_team_next_pick = df_subset.loc[df_subset.Current_Owner.astype(
    #     int) == int(nga_team_id), 'Display_Name_Detailed'].iloc[0]

    # If the bid is less than pick 41 the it follows the normal points based calculations:

    if int(nga_bid_pick_no) < 41:

        # Defining discounts based off what round the bid came in:
        if nga_bid_round == 'RD1':
            nga_pts_required = float(nga_pts_value) * .8
            sum_line2 = nga_team + ' will require ' + \
                f"{nga_pts_required}" + ' draft points to match bid.'

        else:
            nga_pts_required = float(nga_pts_value) - 197
            sum_line2 = nga_team + ' will require ' + \
                f"{nga_pts_required}" + ' draft points to match bid.'

        df_subset['Cumulative_Pts'] = df_subset.groupby(
            'Current_Owner')['AFL_Points_Value'].transform(pd.Series.cumsum)
        df_subset['Payoff_Diff'] = df_subset['Cumulative_Pts'].astype(
            float) - nga_pts_required
        df_subset['AFL_Pts_Left'] = np.where(
            df_subset['Payoff_Diff'] <= 0,
            0,
            np.where(
                df_subset['Payoff_Diff'] < df_subset['AFL_Points_Value'].astype(
                    float),
                df_subset['Payoff_Diff'],
                df_subset['AFL_Points_Value']
            )
        )

        # creating previous pick rows to compare whether the picks have to be used or not:
        df_subset['AFL_Pts_Left_previous_pick'] = df_subset['AFL_Pts_Left'].shift()
        df_subset['AFL_Pts_Value_previous_pick'] = df_subset['AFL_Points_Value'].shift()

        df_subset['AFL_Pts_Value_previous_pick'] = np.array(
            list(df_subset['AFL_Pts_Value_previous_pick'])).astype(float)
        df_subset.fillna(0)
        df_subset['Action'] = np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'] == 0),
                                       'Pick lost to back of draft',
                                       np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'].astype(float) > 0),
                                                'Pick Shuffled Backwards',
                                                np.where((df_subset['AFL_Pts_Left'] == df_subset['AFL_Points_Value']) & (df_subset['Payoff_Diff'].astype(float) < 0) & (df_subset['AFL_Pts_Value_previous_pick'].fillna(0).astype(float) > 0), 'Points Deficit',
                                                         'No Change')))

        df_subset['Deficit_Amount'] = np.where(
            df_subset['Action'] == 'Points Deficit', df_subset['Payoff_Diff'], np.nan)

        # defining the deficit amount
        try:
            nga_points_deficit = df_subset.loc[df_subset.Action ==
                                               'Points Deficit', 'Deficit_Amount'].iloc[0]

        except:
            nga_points_deficit = []

        # Create lists of changes to make:
        picks_lost = df_subset.loc[df_subset.Action ==
                                   'Pick lost to back of draft', 'Display_Name_Detailed'].to_list()
        picks_shuffled = df_subset.loc[df_subset.Action ==
                                       'Pick Shuffled Backwards', 'Display_Name_Detailed'].to_list()
        pick_deficit = df_subset.loc[df_subset.Action ==
                                     'Points Deficit', 'Display_Name_Detailed'].to_list()

        try:
            picks_shuffled_points_value = df_subset.loc[df_subset.Action ==
                                                        'Pick Shuffled Backwards', 'AFL_Pts_Left'].iloc[0]
            # print(picks_shuffled_points_value)
        except:
            picks_shuffled_points_value = np.nan
            # print(picks_shuffled_points_value)
        carry_over_deficit = nga_points_deficit
        # Step 1: Moving all picks to the back of the draft:

        if len(picks_lost) > 0:
            pick_lost_details = pd.DataFrame(
                columns=['Pick', 'Moves_To', 'New_Points_Value'])

            for pick in picks_lost:
                # Reset the index
                df = df.reset_index(drop=True)
                # Find row number of pick lost
                rowno_picklost = df.index[df.Display_Name_Detailed == pick][0]
                # Find row number of the first pick in the next year

                rowno_startnextyear = df.index[(
                    df.Year.astype(int) == int(v_current_year_plus1))][0]
                # print(rowno_startnextyear)

                # Insert pick to the row before next years draft:
                df = pd.concat([df.iloc[:rowno_startnextyear], df.iloc[[
                               rowno_picklost]], df.iloc[rowno_startnextyear:]]).reset_index(drop=True)
                # Find row number to delete and execute delete:
                rowno_delete = df.index[df.Display_Name_Detailed == pick][0]
                # print(rowno_delete)
                df.drop(rowno_delete, axis=0, inplace=True)
                # Changing the names of some key details:
                # Change system note to describe action
                df['System_Note'].mask(df['Display_Name_Detailed'] == pick,
                                       'NGA bid match: pick lost to back of draft', inplace=True)

                # Change the draft round
                df['Draft_Round'].mask(
                    df['Display_Name_Detailed'] == pick, 'BOD', inplace=True)
                df['Draft_Round_Int'].mask(
                    df['Display_Name_Detailed'] == pick, 99, inplace=True)
                df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick, str(
                    v_current_year) + '-Back of Draft', inplace=True)

                # Reset points value
                df['AFL_Points_Value'].mask(
                    df['Display_Name_Detailed'] == pick, 0, inplace=True)

                # If needing to update pick moves before the inserts
                df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
                library_AFL_Draft_Points = df['AFL_Points_Value']
                df['AFL_Points_Value'] = df['Overall_Pick'].map(
                    library_AFL_Draft_Points).fillna(0)

                # Reset index Again
                df = df.reset_index(drop=True)

                # One line summary:
                print(pick + ' has been lost to the back of the draft.')

                # Update picks lost details df
                pick_lost_details_loop = pd.DataFrame({'Pick': pick,
                                                       'Moves_To': 'End of Draft',
                                                       'New_Points_Value': 0}, index=[0])
                pick_lost_details = pick_lost_details.append(
                    pick_lost_details_loop)

        else:
            pick_lost_details = pd.DataFrame(
                columns=['Pick', 'Moves_To', 'New_Points_Value'])

            # Step 2: Shuffling Pick back to their spot

        if len(picks_shuffled) > 0:

            pick_shuffled = picks_shuffled[0]

            # Find row number of pick shuffled

            rowno_pickshuffled = df.index[df.Display_Name_Detailed ==
                                          pick_shuffled][0]

            # Find the row number of where the pick should be inserted:

            rowno_pickshuffled_to = df[(df.Year.astype(int) == int(
                v_current_year))]['AFL_Points_Value'].astype(float).ge(picks_shuffled_points_value).idxmin()

            # Execute Shuffle
            # Insert pick to the row before next years draft:
            df = pd.concat([df.iloc[:rowno_pickshuffled_to], df.iloc[[
                           rowno_pickshuffled]], df.iloc[rowno_pickshuffled_to:]]).reset_index(drop=True)
            # Find row number to delete and execute delete:
            df.drop(rowno_pickshuffled, axis=0, inplace=True)

            # If needing to update pick numbers after the delete
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
            library_AFL_Draft_Points = df['AFL_Points_Value']
            df['AFL_Points_Value'] = df['Overall_Pick'].map(
                library_AFL_Draft_Points).fillna(0)

            # Reset index Again
            df = df.reset_index(drop=True)

            # Changing the names of some key details:
            # Change system note to describe action
            picks_shuffled_str = "".join(picks_shuffled)
            df['System_Note'].mask(df['Display_Name_Detailed'].astype(
                str) == picks_shuffled_str, 'NGA bid match: pick shuffled backwards', inplace=True)

            # Change the draft round
            # Just take row above? if above and below equal each other, then value, if not take one above.
            # Find row above:
            rowno_new_rd_no = df.index[df.Display_Name_Detailed ==
                                       picks_shuffled_str][0] - 1

            # Fine Round No from row above:
            new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

            # Make Changes
            df['Draft_Round_Int'].mask(
                df['Display_Name_Detailed'] == picks_shuffled_str, new_rd_no, inplace=True)
            df['Draft_Round'].mask(df['Display_Name_Detailed'] ==
                                   picks_shuffled_str, 'RD' + str(int(new_rd_no)), inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == picks_shuffled_str, str(
                v_current_year) + '-RD' + new_rd_no + '-ShuffledBack', inplace=True)

            # Reset points value
            df['AFL_Points_Value'].mask(
                df['Display_Name_Detailed'] == picks_shuffled_str, picks_shuffled_points_value, inplace=True)

            # Summary:
            new_shuffled_pick_no = df.index[df.Display_Name_Detailed ==
                                            picks_shuffled_str][0] + 1
            # print(picks_shuffled + ' will be shuffled back to pick ' + new_shuffled_pick_no.astype(str) + ' in RD' + str(int(new_rd_no)))

            # Summary Dataframe
            pick_shuffle_details = pd.DataFrame(
                {'Pick': picks_shuffled_str, 'Moves_To': 'RD' + str(int(new_rd_no)) + '-Pick' + new_shuffled_pick_no.astype(str), 'New_Points_Value': picks_shuffled_points_value}, index=[0])

        else:
            pick_shuffle_details = []

        # Step 3: Applying the deficit to next year:

        if len(pick_deficit) > 0:
            library_AFL_Draft_Points = df['AFL_Points_Value']
            deficit_subset.rename(
                columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
            deficit_subset = deficit_subset[(deficit_subset.Current_Owner.astype(int) == int(nga_team_id)) & (int(
                deficit_subset.Year[0])+1 == int(v_current_year_plus1)) & (deficit_subset.Draft_Round_Int.astype(int) >= int(nga_bid_round_int))]

            # Finding the first pick in the round to take the points off (and rowno)
            deficit_attached_pick = deficit_subset['Display_Name_Detailed'].iloc[0]
            deficit_pickshuffled_rowno = df.index[df.Display_Name_Detailed ==
                                                  deficit_attached_pick][0]

            # finding the points value of that pick and then adjusting the deficit
            deficit_attached_pts = deficit_subset['AFL_Points_Value']

            deficit_pick_points = deficit_attached_pts + nga_points_deficit

            # Find the row number of where the pick should be inserted:
            deficit_pickshuffled_to = df[(df.Year == v_current_year_plus1)]['AFL_Points_Value'].ge(
                deficit_pick_points.astype(float)).idxmin()

            # Execute pick shuffle
            df = pd.concat([df.iloc[:deficit_pickshuffled_to], df.iloc[[
                           deficit_pickshuffled_rowno]], df.iloc[deficit_pickshuffled_to:]]).reset_index(drop=True)

            # Find row number to delete and execute delete:
            df.drop(deficit_pickshuffled_rowno, axis=0, inplace=True)

            # If needing to update pick numbers after the delete
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1

            df['AFL_Points_Value'] = df['Overall_Pick'].map(
                library_AFL_Draft_Points).fillna(0)

            # Reset index Again
            df = df.reset_index(drop=True)

            # Change system note to describe action
            df['System_Note'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'NGA bid match: Points Deficit',
                                   inplace=True)

            # Change the draft round
            # Just take row above? if above and below equal each other, then value, if not take one above.
            # Find row above:
            rowno_new_rd_no = df.index[df.Display_Name_Detailed ==
                                       deficit_attached_pick][0] - 1

            # Fine Round No from row above:
            new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

            # Make Changes
            df['Draft_Round_Int'].mask(
                df['Display_Name_Detailed'] == deficit_attached_pick, new_rd_no, inplace=True)
            df['Draft_Round'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'RD' + str(int(new_rd_no)),
                                   inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == deficit_attached_pick,
                                  str(v_current_year) + '-RD' + str(int(new_rd_no)) + '-NGA_Deficit', inplace=True)

            # Reset points value
            df['AFL_Points_Value'].mask(
                df['Display_Name_Detailed'] == deficit_attached_pick, deficit_pick_points, inplace=True)

            # Summary:
            # getting the new overall pick number and what round it belongs to:
            deficit_new_shuffled_pick_no = df[df.Display_Name_Detailed ==
                                              deficit_attached_pick].Overall_Pick.iloc[0]
            deficit_new_shuffled_pick_RD_no = df[df.Display_Name_Detailed ==
                                                 deficit_attached_pick].Draft_Round.iloc[0]

            # 2021-RD3-Pick43-Richmond
            pick_deficit_details = pd.DataFrame(
                {'Pick': deficit_attached_pick, 'Moves_To': deficit_new_shuffled_pick_no, 'New_Points_Value': deficit_pick_points}, index=[0])

            print(deficit_attached_pick + ' moves to pick ' +
                  deficit_new_shuffled_pick_no.astype(str) + ' in ' + deficit_new_shuffled_pick_RD_no)

        else:
            pick_deficit_details = []

        ########## EXECUTE INSERT OF PICK TO THE SPOT OF THE BID ##############
        # inserting pick above nga_bid
        # Make the changes to the masterlist:
        rowno = df.index[df['Display_Name_Detailed'] == nga_bid][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(nga_team_id), 'Position'].iloc[0], 'Year': v_current_year,
                            'TeamName': nga_team_id, 'PickType': 'NGA_BidMatch', 'Original_Owner': nga_team_id, 'Current_Owner': nga_team_id,
                             'Previous_Owner': nga_team_id, 'Draft_Round': nga_bid_round, 'Draft_Round_Int': nga_bid_round_int,
                             'Pick_Group': str(v_current_year) + '-' + nga_bid_round + '-NGABidMatch', 'Reason': 'NGA Bid Match',
                             'Pick_Status': 'Used', 'Selected_Player': nga_player}, index=[rowno])

        # Execute Insert
        # i.e stacks 3 dataframes on top of each other

        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)

        # df = df.astype({"TeamName":'int'})
        df = df.iloc[rowno]
        df['id'] = rowno+1
        df['projectid_id'] = pk

        MasterList.objects.filter(id=rowno+1).update(**df)

        ######## #### call update masterlist ###################################

        df = dataframerequest(request, pk)
        updatedf = update_masterlist(df)

        iincreament_id = 1
        for index, updaterow in updatedf.iterrows():
            nga_dict = dict(updaterow)
            team = Teams.objects.get(id=updaterow.TeamName)
            Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
            Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
            previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
            Overall_pickk = nga_dict['Overall_Pick']

            Project1 = Project.objects.get(id=pk)
            nga_dict['Previous_Owner'] = previous_owner
            team = Teams.objects.get(id=updaterow.TeamName)
            nga_dict['TeamName'] = team
            nga_dict['Original_Owner'] = Original_Owner
            nga_dict['Current_Owner'] = Current_Ownerr
            nga_dict['projectid'] = Project1

            nga_dict['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
                None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

            nga_dict['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
                updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(nga_dict['Display_Name'])
            nga_dict['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
                None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
                ' ' + str(Overall_pickk)

            nga_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
                previous_owner + team.ShortName + \
                ')' if Original_Owner != Current_Ownerr else team.ShortName

            nga_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
                previous_owner + team.ShortName + \
                ')' if Original_Owner != Current_Ownerr else team.ShortName

            MasterList.objects.filter(
                id=iincreament_id).update(**nga_dict)

            iincreament_id += 1

            ######## Combine into a summary dataframe: #############
            nga_summaries_list = [pick_lost_details,
                                  pick_shuffle_details, pick_deficit_details]
            nga_summary_df = pd.DataFrame(
                columns=['Pick', 'Moves_To', 'New_Points_Value'])
            for x in nga_summaries_list:
                if len(x) > 0:
                    nga_summary_df = nga_summary_df.append(x)

            nga_summary_dict = nga_summary_df.to_dict(orient="list")

            ######### Exporting Transaction Details: ###############
            current_time = datetime.datetime.now(pytz.timezone(
                'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
            nga_dict = {nga_team: [nga_pick_type,
                                   nga_bid, nga_bid_pick_no, nga_player]}
            # Create Simple description.
            nga_description = 'NGA Bid Match: Pick ' + \
                str(nga_bid_pick_no) + ' ' + str(nga_team) + \
                ' (' + str(nga_player) + ')'

            obj = Project.objects.get(id=pk)

            transaction_details = (
                {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'NGA_Bid_Match',
                 'Transaction_Details': nga_dict,
                 'Transaction_Description': nga_description,
                 'projectId': obj.id
                 })

            Transactions.objects.create(
                Transaction_Number='',
                Transaction_DateTime=current_time,
                Transaction_Type='NGA_Bid_Match',
                Transaction_Details=nga_dict,
                Transaction_Description=nga_description,
                projectId=obj.id

            )
            last_obj = Transactions.objects.latest('id')
            Transactions.objects.filter(id=last_obj.id).update(
                Transaction_Number=last_obj.id)
            call_nga_bid(transaction_details)
            return Response({'success': 'NGA Bid Created Successfuly'}, status=status.HTTP_201_CREATED)


def add_draft_night_selection_inputs(request):
    data = request.data
    team_id = data.get('teamid')
    selected_pick_id = data.get('selected_pick_id')
    player_taken_id = data.get('player_taken_id')
    return selected_pick_id, player_taken_id


@ api_view(['POST'])
@ permission_classes([AllowAny, ])
def add_draft_night_selection(request, pk):
    masterlist = dataframerequest(request, pk)
    current_date = date.today()
    v_current_year = current_date.year
    selected_pick_id, player_taken_id = add_draft_night_selection_inputs(
        request)

    pick_obj = MasterList.objects.get(id=selected_pick_id)
    selected_pick = pick_obj.Display_Name_Detailed
    player_obj = Players.objects.get(id=player_taken_id)
    player_taken = player_obj.Full_Name
    masterlist['Pick_Status'].mask(
        masterlist['Display_Name_Detailed'] == selected_pick, 'Used', inplace=True)
    masterlist['Selected_Player'].mask(
        masterlist['Display_Name_Detailed'] == selected_pick, player_taken, inplace=True)

    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    team_name = masterlist.loc[masterlist.Display_Name_Detailed ==
                               selected_pick, 'Current_Owner'].iloc[0]
    pick_round = masterlist.loc[masterlist.Display_Name_Detailed ==
                                selected_pick, 'Draft_Round'].iloc[0]
    overall_pick = masterlist.loc[masterlist.Display_Name_Detailed ==
                                  selected_pick, 'Overall_Pick'].iloc[0]

    drafted_player_dict = {team_name: [pick_round, overall_pick, player_taken]}
    drafted_description = 'With pick ' + \
        str(overall_pick) + ' ' + str(team_name) + \
        ' have selected ' + str(player_taken)

    # ####################call masterlist ########################################

    # df = dataframerequest(request,pk)

    updatedf = update_masterlist(masterlist)

    iincreament_id = 1
    for index, updaterow in updatedf.iterrows():

        draft_night_dict = dict(updaterow)
        team = Teams.objects.get(id=updaterow.TeamName)
        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = draft_night_dict['Overall_Pick']

        Project1 = Project.objects.get(id=pk)
        draft_night_dict['Previous_Owner'] = previous_owner
        team = Teams.objects.get(id=updaterow.TeamName)
        draft_night_dict['TeamName'] = team
        draft_night_dict['Original_Owner'] = Original_Owner
        draft_night_dict['Current_Owner'] = Current_Ownerr
        draft_night_dict['projectid'] = Project1

        draft_night_dict['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        draft_night_dict['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(draft_night_dict['Display_Name'])

        draft_night_dict['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        draft_night_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        draft_night_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        MasterList.objects.filter(id=iincreament_id).update(**draft_night_dict)

        iincreament_id += 1

    drafted_player_dict = {team_name: [pick_round, overall_pick, player_taken]}
    drafted_description = 'With pick ' + \
        str(overall_pick) + ' ' + str(team_name) + \
        ' have selected ' + str(player_taken)
    Projobj = Project.objects.get(id=pk)
    Proj_id = Projobj.id

    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Drafted_Player',
        Transaction_Details=drafted_player_dict,
        Transaction_Description=drafted_description,
        projectId=Proj_id
    )
    obj = Transactions.objects.latest('id')
    drafted_player_transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Drafted_Player',
         'Transaction_Details': drafted_player_dict,
         'Transaction_Description': drafted_description,
         'projectId': Proj_id
         })
    Transactions.objects.filter(id=obj.id).update(Transaction_Number=obj.id)
    call_add_draft_night_selection(drafted_player_transaction_details)
    return Response({'success': "Add-draft-Night-Selection created successfully"}, status=status.HTTP_201_CREATED)


def call_manual_insert(transactions):
    return transactions


def add_manual_inputs(request, pk):

    data = request.data
    manual_team = data.get('manual_team')
    manual_round = data.get('manual_round')
    manual_insert_instructions = data.get('instructions')
    manual_aligned_pick_id = data.get('manual_aligned_pick')
    reason = data.get('reason')

    manual_aligned_pick = []
    pickqueryset = MasterList.objects.filter(
        id=manual_aligned_pick_id).values()
    manual_aligned_pick = pickqueryset[0]['Display_Name_Detailed']
    df = dataframerequest(request, pk)

    masterlist = df

    manual_insert_unique_pick = masterlist.loc[masterlist.Display_Name_Detailed ==
                                               manual_aligned_pick, 'Unique_Pick_ID'].iloc[0]
    return manual_team, manual_round, manual_insert_instructions, manual_aligned_pick, reason, masterlist, manual_insert_unique_pick


@api_view(['POST'])
@permission_classes([AllowAny])
def AddManualRequest(request, pk):
    current_date = date.today()
    v_current_year = current_date.year
    manual_team, manual_round, manual_insert_instructions, manual_aligned_pick, reason, masterlist, manual_insert_unique_pick = add_manual_inputs(
        request, pk)
    manual_pick_type = 'Manual Insert'
    df = masterlist
    # #### rename column names because database is returning columns fields with id concatenated

    rowno = df.index[df['Display_Name_Detailed'].astype(
        str) == str(manual_aligned_pick)][0]

    line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(manual_team), 'Position'].iloc[0], 'Year': v_current_year,
                         'TeamName': int(manual_team), 'PickType': 'Manual_Insert', 'Original_Owner': manual_team, 'Current_Owner': manual_team,
                         'Previous_Owner': '', 'Draft_Round': manual_round, 'Pick_Group': str(v_current_year) + '-' + 'RD1-Manual', 'Reason': reason},
                        index=[rowno])

    if manual_insert_instructions == 'Before':
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        df = df.iloc[rowno]

        df['id'] = rowno
        df['projectid_id'] = pk

        MasterList.objects.filter(id=rowno).update(**df)
    else:
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno]

        df['id'] = rowno+1
        df['projectid_id'] = pk
        MasterList.objects.filter(id=rowno+1).update(**df)

    df1 = dataframerequest(request, pk)

    # #####  Call update masterlist ######################################

    updatedf = update_masterlist(df1)
    iincreament_id = 1
    for index, updaterow in updatedf.iterrows():

        manual_dict = dict(updaterow)
        team = Teams.objects.get(id=updaterow.TeamName)
        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = manual_dict['Overall_Pick']

        Project1 = Project.objects.get(id=pk)
        manual_dict['Previous_Owner'] = previous_owner
        team = Teams.objects.get(id=updaterow.TeamName)
        manual_dict['TeamName'] = team
        manual_dict['Original_Owner'] = Original_Owner
        manual_dict['Current_Owner'] = Current_Ownerr
        manual_dict['projectid'] = Project1

        manual_dict['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        manual_dict['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(manual_dict['Display_Name'])

        manual_dict['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        manual_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        manual_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        MasterList.objects.filter(id=iincreament_id).update(**manual_dict)

        iincreament_id += 1
    manual_dictt = {}
    manual_dictt[manual_team] = [
        manual_pick_type, manual_round, reason, manual_aligned_pick, manual_insert_unique_pick, manual_insert_instructions]
    manual_description = manual_team + ' received a ' + manual_pick_type + ' Pick'

    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')

    transaction_details = pd.DataFrame(
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Manual_Insert', 'Transaction_Details': manual_dict, 'Transaction_Description': manual_description, 'projectId': pk})

    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Manual_Insert',
        Transaction_Details=manual_dictt,
        Transaction_Description=manual_description,
        projectId=pk
    )

    obj = Transactions.objects.latest('id')
    Transactions.objects.filter(id=obj.id).update(
        Transaction_Number=obj.id)
    call_manual_insert(transaction_details)
    return Response({'success': 'Add Manual created Successfully'}, status=status.HTTP_201_CREATED)


def quick_academy_calculator_inputs(request):
    data = request.data
    academy_team = data.get('academy_team_id')
    academy_pick_type = 'Academy Bid Match'
    academy_bid = data.get('academy_bid')
    academy_player = data.get('academy_player')
    return academy_team, academy_pick_type, academy_bid, academy_player


@api_view(['POST'])
@permission_classes([AllowAny])
def quick_academy_calculator(request, pk):
    current_date = date.today()
    v_current_year = current_date.year
    v_current_year_plus1 = v_current_year + 1

    df = dataframerequest(request, pk)
    deficit_subset = df
    pick_suffled_df = df
    deficit_subset = df.copy()
    pick_deficit_details = []
    academy_team, academy_pick_type, academy_bid, academy_player = quick_academy_calculator_inputs(
        request)
    library_AFL_Draft_Points = df['AFL_Points_Value']

    academy_pick = df.loc[df.index.astype(int) == int(
        academy_bid), 'Display_Name_Detailed'].iloc[0]

    academy_pts_value = df.loc[df.Display_Name_Detailed ==
                               academy_pick, 'AFL_Points_Value'].iloc[0]
    academy_bid_round = df.loc[df.Display_Name_Detailed ==
                               academy_pick, 'Draft_Round'].iloc[0]
    academy_bid_round_int = df.loc[df.Display_Name_Detailed ==
                                   academy_pick, 'Draft_Round_Int'].iloc[0]
    academy_bid_team = df.loc[df.Display_Name_Detailed ==
                              academy_pick, 'Current_Owner'].iloc[0]
    academy_bid_pick_no = df.loc[df.Display_Name_Detailed ==
                                 academy_pick, 'Overall_Pick'].iloc[0]

    academy_team_obj = Teams.objects.get(id=academy_team)
    academy_bid_obj = Teams.objects.get(id=academy_bid_team)
    teamname = academy_bid_obj.TeamNames
    academy_bid_teamname = academy_team_obj.TeamNames
    sum_line1 = str(academy_bid_teamname) + ' have placed a bid on a ' + str(teamname) + \
        ' academy player at pick ' + \
        str(academy_bid_pick_no) + ' in ' + str(academy_bid_round)

    if academy_bid_round == 'RD1':
        academy_pts_required = float(academy_pts_value) * .8
        sum_line2 = academy_bid_teamname + ' will require ' + \
            str(academy_pts_required) + ' draft points to match bid.'

    else:
        academy_pts_required = float(academy_pts_value) - 197
        sum_line2 = academy_bid_teamname + ' will require ' + \
            str(academy_pts_required) + ' draft points to match bid.'

    df_subset = dataframerequest(request, pk)

    if df_subset['Overall_Pick'].isnull().any():
        df_subset['Overall_Pick'] = 1
    else:

        df_subset = df_subset[(df_subset.Current_Owner.astype(int) == int(academy_team)) & (
            df_subset.Year.astype(int) == int(v_current_year)) & (7 >= int(academy_bid_pick_no))]

    df_subset['Cumulative_Pts'] = df_subset.groupby(
        'Current_Owner')['AFL_Points_Value'].transform(pd.Series.cumsum)
    commulative_pts = df_subset['Cumulative_Pts']

    df_subset['Payoff_Diff'] = ''

    if commulative_pts.isnull().any() == False:
        df_subset['Payoff_Diff'] = 0.0
    else:

        df_subset['Payoff_Diff'] = df_subset['Cumulative_Pts'].astype(
            float) - float(academy_pts_required)

    df_subset['AFL_Pts_Left'] = np.where(
        df_subset['Payoff_Diff'].astype(float) <= 0,
        0,
        np.where(
            df_subset['Payoff_Diff'] < df_subset['AFL_Points_Value'].astype(
                float),
            df_subset['Payoff_Diff'],
            df_subset['AFL_Points_Value']
        )
    )

    df_subset['AFL_Pts_Left_previous_pick'] = df_subset['AFL_Pts_Left'].shift()

    df_subset['AFL_Pts_Value_previous_pick'] = df_subset['AFL_Points_Value'].shift()

    df_subset['Action'] = np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'] == 0),
                                   'Pick lost to back of draft',
                                   np.where((df_subset['AFL_Pts_Left'].astype(float) != df_subset['AFL_Points_Value'].astype(float)) & (df_subset['AFL_Pts_Left'].astype(float) > 0),
                                            'Pick Shuffled Backwards',
                                            np.where((df_subset['AFL_Pts_Left'] == df_subset['AFL_Points_Value']) & (df_subset['Payoff_Diff'] < 0) & (df_subset['AFL_Pts_Value_previous_pick'].astype(float) > 0), 'Points Deficit',
                                                     'No Change')))

    df_subset['Deficit_Amount'] = np.where(
        df_subset['Action'] == 'Points Deficit', df_subset['Payoff_Diff'], np.nan)

    try:
        academy_points_deficit = df_subset.loc[df_subset.Action ==
                                               'Points Deficit', 'Deficit_Amount'].iloc[0]
    except:
        academy_points_deficit = []

    picks_lost = df_subset.loc[df_subset.Action ==
                               'Pick lost to back of draft', 'Display_Name_Detailed'].to_list()

    picks_shuffled = df_subset.loc[df_subset.Action ==
                                   'Pick Shuffled Backwards', 'Display_Name_Detailed'].to_list()

    pick_deficit = df_subset.loc[df_subset.Action ==
                                 'Points Deficit', 'Display_Name_Detailed'].to_list()

    try:
        picks_shuffled_points_value = df_subset.loc[df_subset.Action ==
                                                    'Pick Shuffled Backwards', 'AFL_Pts_Left'].iloc[0]
    except:
        picks_shuffled_points_value = np.nan

    carry_over_deficit = academy_points_deficit

    summarydf = df_subset[['Display_Name_Detailed',
                           'AFL_Points_Value', 'AFL_Pts_Left', 'Action', 'Deficit_Amount']]

    if len(picks_lost):
        pick_lost_details = pd.DataFrame(
            columns=['Pick', 'Moves_To', 'New_Points_Value'])

    overall_pick = df['Overall_Pick']
    rowno_picklost = ''
    rowno_startnextyear = ''
    if len(picks_lost) > 0:
        pick_lost_details = pd.DataFrame(
            columns=['Pick', 'Moves_To', 'New_Points_Value'])

        for pick in picks_lost:
            # Reset the index
            df = df.reset_index(drop=True)

            # Find row number of pick lost
            rowno_picklost = df.index[df.Display_Name_Detailed.astype(
                str) == str(pick)][0]

            # Find row number of the first pick in the next year
            rowno_startnextyear = df.index[(df.Year.astype(int) == int(
                v_current_year_plus1)) & (df.Overall_Pick.astype(int) == 1)][0]
            # print(rowno_startnextyear)

    # for pick in picks_lost:
    #     # Reset the index
    #     df = df.reset_index(drop=True)
    #     if df['Display_Name_Detailed'].isnull().any() == False:
    #         rowno_picklost = df.index[df['Display_Name_Detailed'].astype(str) == str(pick) ][0]
    #     else:
    #         rowno_picklost = df.index[df['Display_Name_Detailed'].astype(str) == str(pick) ][0]

    #     if df['Overall_Pick'].isnull().any():
    #         df['Overall_Pick'] = df['Overall_Pick'].fillna(1)

    #         rowno_startnextyear = df.index[(df['Year'].astype(int) == int(v_current_year_plus1)) & (df['Overall_Pick'].astype(int) == 1)]
    #     else:
    #         rowno_startnextyear = df.index[((df['Year'].astype(int)) == int(v_current_year_plus1)) & (df['Overall_Pick'].astype(int) == 1)]
    #     rowno_startnextyear = rowno_startnextyear[1]

        df = pd.concat([df.iloc[:rowno_startnextyear], df.iloc[[
            rowno_picklost]], df.iloc[rowno_startnextyear]]).reset_index(drop=True)

        rowno_delete = df.index[df.Display_Name_Detailed == pick][0]

        df.drop(rowno_delete, axis=0, inplace=True)

        df['System_Note'].mask(df['Display_Name_Detailed'] == pick,
                               'Academy bid match: pick lost to back of draft', inplace=True)

        df['Draft_Round'].mask(df['Display_Name_Detailed']
                               == pick, 'BOD', inplace=True)
        df['Draft_Round_Int'].mask(
            df['Display_Name_Detailed'] == pick, 99, inplace=True)
        df['Pick_Group'].mask(df['Display_Name_Detailed'].astype(
            str) == pick, str(v_current_year) + '-Back of Draft', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(
            df['Display_Name_Detailed'] == pick, 0, inplace=True)

        # If needing to update pick moves before the inserts
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(
            library_AFL_Draft_Points).fillna(0)

        # Reset index Again
        df = df.reset_index(drop=True)

        # One line summary:
        # print(pick + ' has been lost to the back of the draft.')

        # Update picks lost details df
        pick_lost_details_loop = pd.DataFrame({'Pick': pick,
                                               'Moves_To': 'End of Draft',
                                               'New_Points_Value': 0}, index=[0])

        pick_lost_details = pick_lost_details.append(pick_lost_details_loop)

    else:
        pick_lost_details = pd.DataFrame(
            columns=['Pick', 'Moves_To', 'New_Points_Value'])

    if len(picks_shuffled) > 0:
        pick_shuffled = picks_shuffled[0]

        df = pick_suffled_df

        rowno_pickshuffled = df.index[df.Display_Name_Detailed.astype(
            str) == picks_shuffled][0]

        rowno_pickshuffled_to = df[(df.Year.astype(int) == v_current_year)]['AFL_Points_Value'].astype(
            float).ge(picks_shuffled_points_value).idxmin()
        df = pd.concat([df.iloc[:rowno_pickshuffled_to], df.iloc[[
                       rowno_pickshuffled]], df.iloc[rowno_pickshuffled_to:]]).reset_index(drop=True)
        df.drop(rowno_pickshuffled, axis=0, inplace=True)

        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(
            library_AFL_Draft_Points).fillna(0)

        df = df.reset_index(drop=True)

        df['System_Note'].mask(df['Display_Name_Detailed'] == pick_shuffled,
                               'Academy bid match: pick shuffled backwards', inplace=True)

        rowno_new_rd_no = df.index[df.Display_Name_Detailed ==
                                   picks_shuffled][0] - 1

        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int
        df['Draft_Round_Int'].mask(
            df['Display_Name_Detailed'] == pick_shuffled, new_rd_no, inplace=True)
        df['Draft_Round'].mask(df['Display_Name_Detailed']
                               == pick_shuffled, 'RD' + new_rd_no, inplace=True)
        df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick_shuffled, str(
            v_current_year) + '-RD' + new_rd_no + '-ShuffledBack', inplace=True)

        df['AFL_Points_Value'].mask(
            df['Display_Name_Detailed'] == pick_shuffled, picks_shuffled_points_value, inplace=True)

        new_shuffled_pick_no = df.index[df.Display_Name_Detailed.astype(
            str) == picks_shuffled][0] + 1
        print(str(pick_shuffled) + ' will be shuffled back to pick ' +
              str(new_shuffled_pick_no) + ' in RD' + str(new_rd_no))

        pick_shuffle_details = pd.DataFrame(
            {'Pick': str(pick_shuffled), 'Moves_To': 'RD' + str(new_rd_no) + '-Pick' + str(new_shuffled_pick_no), 'New_Points_Value': str(picks_shuffled_points_value)}, index=[0])

    else:
        pick_shuffle_details = []

    # Step 3: Applying the deficit to next year:

    if len(pick_deficit) > 0:

        df = deficit_subset.copy()
        deficit_subset = deficit_subset[(deficit_subset.Current_Owner.astype(int) == int(academy_team)) & (
            deficit_subset.Year.astype(int) == int(v_current_year_plus1)) & (deficit_subset.Draft_Round_Int >= academy_bid_round_int)]

        # Finding the first pick in the round to take the points off (and rowno)
        deficit_attached_pick = deficit_subset['Display_Name_Detailed'].iloc[0]

        deficit_pickshuffled_rowno = df.index[df.Display_Name_Detailed.astype(str) ==
                                              str(deficit_attached_pick)][0]

        # finding the points value of that pick and then adjusting the deficit
        deficit_attached_pts = deficit_subset['AFL_Points_Value'].iloc[0]

        deficit_pick_points = str(deficit_attached_pts) + \
            str(academy_points_deficit)
        # Find the row number of where the pick should be inserted:
        deficit_pickshuffled_to = df[(df.Year.astype(int) == int(v_current_year_plus1))]['AFL_Points_Value'].astype(float).ge(
            float(deficit_pick_points)).idxmin()

        # Execute pick shuffle
        df = pd.concat([df.iloc[:deficit_pickshuffled_to], df.iloc[[
                       deficit_pickshuffled_rowno]], df.iloc[deficit_pickshuffled_to:]]).reset_index(drop=True)

        # Find row number to delete and execute delete:
        df.drop(deficit_pickshuffled_rowno, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(
            library_AFL_Draft_Points).fillna(0)

        # Reset index Again
        df = df.reset_index(drop=True)

        # Change system note to describe action
        df['System_Note'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'Academy bid match: Points Deficit',
                               inplace=True)

        # Change the draft round
        # Just take row above? if above and below equal each other, then value, if not take one above.
        # Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed ==
                                   deficit_attached_pick][0] - 1

        # Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

        # Make Changes
        df['Draft_Round_Int'].mask(
            df['Display_Name_Detailed'] == deficit_attached_pick, new_rd_no, inplace=True)
        df['Draft_Round'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'RD' + str(new_rd_no),
                               inplace=True)
        df['Pick_Group'].mask(df['Display_Name_Detailed'] == deficit_attached_pick,
                              str(v_current_year) + '-RD' + str(new_rd_no) + '-AcademyDeficit', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(
            df['Display_Name_Detailed'] == deficit_attached_pick, deficit_pick_points, inplace=True)

        # Summary:
        # getting the new overall pick number and what round it belongs to:
        deficit_new_shuffled_pick_no = df[df.Display_Name_Detailed ==
                                          deficit_attached_pick].Overall_Pick.iloc[0]
        deficit_new_shuffled_pick_RD_no = df[df.Display_Name_Detailed ==
                                             deficit_attached_pick].Draft_Round.iloc[0]
        pick_deficit_details = pd.DataFrame(
            {'Pick': deficit_attached_pick, 'Moves_To': deficit_new_shuffled_pick_no, 'New_Points_Value': deficit_pick_points}, index=[0])

        print(deficit_attached_pick + ' moves to pick ' +
              deficit_new_shuffled_pick_no.astype(str) + ' in ' + deficit_new_shuffled_pick_RD_no)

    else:
        pick_deficit_details = []

        ########## EXECUTE INSERT OF PICK TO THE SPOT OF THE BID ##############
    # inserting pick above academy_bid

    # Make the changes to the masterlist:
    df = dataframerequest(request, pk)
    rowno = df.index[df['Display_Name_Detailed'].astype(
        str) == str(academy_pick)][0]

    # create the line to insert:
    line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(academy_team), 'Position'].iloc[0], 'Year': v_current_year,
                         'TeamName': academy_team, 'PickType': 'AcademyBidMatch', 'Original_Owner': academy_team, 'Current_Owner': academy_team,
                         'Previous_Owner': '', 'Draft_Round': academy_bid_round, 'Draft_Round_Int': academy_bid_round_int,
                         'Pick_Group': str(v_current_year) + '-' + academy_bid_round + '-AcademyBidMatch', 'Reason': 'Academy Bid Match',
                         'Pick_Status': 'Used', 'Selected_Player': academy_player}, index=[rowno])

    # Execute Insert
    # i.e stacks 3 dataframes on top of each other
    df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                   ).reset_index(drop=True)
    df = df.iloc[rowno]
    df['id'] = rowno
    df['projectid_id'] = pk
    MasterList.objects.filter(id=rowno).update(**df)

    ######## Combine into a summary dataframe: #############
    academy_summaries_list = [pick_lost_details,
                              pick_shuffle_details, pick_deficit_details]
    academy_summary_df = pd.DataFrame(
        columns=['Pick', 'Moves_To', 'New_Points_Value'])
    for x in academy_summaries_list:
        if len(x) > 0:
            academy_summary_df = academy_summary_df.append(x)

    academy_summary_dict = academy_summary_df.to_dict(orient="list")

    ######### Exporting Transaction Details: ###############
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    academy_dict = {academy_team: [
        academy_pick_type, academy_bid, academy_bid_pick_no, academy_player]}

    # Create Simple description.
    academy_description = 'Academy Bid Match: Pick ' + \
        str(academy_bid_pick_no) + ' ' + \
        str(academy_team) + ' (' + str(academy_player) + ')'

    obj = Project.objects.get(id=pk)
    Project_id = obj.id
    transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Academy_Bid_Match',
         'Transaction_Details': [academy_dict],
         'Transaction_Description': academy_description,
         'projectId': Project_id
         }
    )

    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Academy_Bid_Match',
        Transaction_Details=academy_dict,
        Transaction_Description=academy_description,
        projectId=pk
    )

    lastinsertedobj = Transactions.objects.latest('id')
    last_inserted_id = lastinsertedobj.id
    Transactions.objects.filter(id=last_inserted_id).update(
        Transaction_Number=last_inserted_id)
    return Response({'Success': 'Success'}, status=status.HTTP_201_CREATED)

    # ##############  Abhishek Code end ##########################


def Get_Constraints_inputs(request, pk):

    data = request.data
    # userid = data.get('userid')
    userid = data.get('userid')
    Userobj = User.objects.get(id=userid)
    Teamid = Userobj.Teams.id
    Teamobj = Teams.objects.get(id=Teamid)
    v_team_name = Teamobj.id

    df = dataframerequest(request, pk)
    masterlist = df
    # inputs for Function:
    data = request.data
    number_possible_solutions = data.get('number_possible_solutions')
    #### Draft Picks to Be Traded Out ####
    # Constraint 1 - Which exact Picks to include (Display_Name_Detailed)

    c1_type = data.get('c1_type')
    c1_set = data.get('c1_set')

    # Constraint 2 - Which Season to picks are from
    c2_type = data.get('c2_type')
    c2_set = data.get('c2_set')

    # Constraint 3 - Which Draft_Round to send

    c3_type = data.get('c3_type')
    c3_set = data.get('c3_set')

    # Constraint 4 - Minimum draft points value to send

    c4_type = data.get('c4_type')
    c4_set = data.get('c4_set')

    # Constraint 5 - Maximum draft points value to send

    c5_type = data.get('c5_type')
    c5_set = data.get('c5_set')
    #### Draft Picks to be traded in ####
    # Constraint 6 - Which team/s to receive from

    c6_type = data.get('c6_type')
    c6_set = data.get('c6_set')

    # Constraint 7 - Which pick (Display_Name_Detailed) to receive

    c7_type = data.get('c7_type')
    c7_set = data.get('c7_set')

    # Constraint 8 - Which Season to receive

    c8_type = data.get('c8_type')
    c8_set = data.get('c8_set')

    # Constraint 9 - Which Draft_Round to receive

    c9_type = data.get('c9_type')
    c9_set = data.get('c9_set')

    # Constraint 10 - Minimum AFL_Points_Value to receive

    c10_type = data.get('c10_type')
    c10_set = data.get('c10_set')

    # Constraint 11 - Maximum AFL_Points_Value to receive

    c11_type = data.get('c11_type')
    c11_set = data.get('c11_set')
    # Constraint 12 - Max difference of total AFL_Points_Value (Percentage)

    c12_type = data.get('c12_type')
    c12_set = data.get('c12_set')
    # Constraint 13 - Minimum number of draft picks to receive

    c13_type = data.get('c13_type')
    c13_set = data.get('c13_set')
    # Constraint 14 - Maximum number of draft picks to receive"
    c14_type = data.get('c14_type')
    c14_set = data.get('c14_set')

    return number_possible_solutions, c1_type, c1_set, c2_type, c2_set, c3_type, c3_set, c4_type, c4_set, c5_type, c5_set, c6_type, c6_set, c7_type, c7_set, c8_type, c8_set, c9_type, c9_set, c10_type, c10_set, c11_type, c11_set, c12_type, c12_set, c13_type, c13_set, c14_type, c14_set, v_team_name, masterlist, userid


@api_view(['POST'])
@permission_classes([AllowAny])
def trade_optimiser_algorithm(request, pk):

    number_possible_solutions, c1_type, c1_set, c2_type, c2_set, c3_type, c3_set, c4_type, c4_set, c5_type, c5_set, c6_type, c6_set, c7_type, c7_set, c8_type, c8_set, c9_type, c9_set, c10_type, c10_set, c11_type, c11_set, c12_type, c12_set, c13_type, c13_set, c14_type, c14_set, v_team_name, masterlist, userid = Get_Constraints_inputs(
        request, pk)

    results_df = pd.DataFrame(columns=[])
    trade_in_vec = []
    trade_out_vec = []
    sol_index = []
    df = masterlist.fillna(0)
    trade_optimiser_df = masterlist

    # Get set of nodes
    picks = trade_optimiser_df['Display_Name_Detailed'].to_numpy()

    # Get set of nodes
    teams = trade_optimiser_df['Current_Owner'].to_numpy()
    # Get set of nodes
    draft_rounds = trade_optimiser_df['Draft_Round'].to_numpy()

    trade_optimiser_df_team = trade_optimiser_df[trade_optimiser_df["Current_Owner"] == v_team_name]

    trade_optimiser_df_team.set_index('Display_Name_Detailed', inplace=True)
    trade_optimiser_df_team_dict = trade_optimiser_df_team.to_dict()

    trade_optimiser_df_team.reset_index(inplace=True)

    owned_picks = trade_optimiser_df_team['Display_Name_Detailed'].to_numpy()

    value_owned_team = trade_optimiser_df_team["AFL_Points_Value"].sum()

    trade_optimiser_df_to_trade_in = trade_optimiser_df[
        trade_optimiser_df["Current_Owner"] != v_team_name]

    to_trade_in_picks = trade_optimiser_df_to_trade_in['Display_Name_Detailed'].to_numpy(
    )
    trade_optimiser_df_to_trade_in.set_index(
        'Display_Name_Detailed', inplace=True)
    trade_optimiser_df_to_trade_in_dict = trade_optimiser_df_to_trade_in.to_dict()

    trade_optimiser_df_to_trade_in.reset_index(inplace=True)
    teams_to_trade_with = list(
        set(trade_optimiser_df_to_trade_in['Current_Owner'].to_numpy()))

    trade_out_solutions = [{i}
                           for i in range(0, int(number_possible_solutions))]

    trade_in_solutions = [{i}
                          for i in range(0, int(number_possible_solutions))]

    count_solution = [0 for i in range(0, int(number_possible_solutions))]

    for sol in range(0, int(number_possible_solutions)):

        # Importing the docplex.mp.model from the CPLEX as Model
        opt_model = plp.LpProblem(name="MIP Model")

        trade_out = {(i): plp.LpVariable(cat=plp.LpBinary,
                                         name="trade_out_"+str({0}).format(i))
                     for i in owned_picks}
        trade_in = {(i): plp.LpVariable(cat=plp.LpBinary, name="trade_in_"+str({0}).format(i))
                    for i in to_trade_in_picks}
        team_trade_in = {(i): plp.LpVariable(cat=plp.LpBinary,
                                             name="team_trade_in_"+str({0}).format(i))
                         for i in teams_to_trade_with}

        objective = plp.lpSum(
            trade_out[i] for i in owned_picks) + plp.lpSum(trade_in[i] for i in to_trade_in_picks)

        # Defines what wallet is chosen

        c0 = {(i, j):
              opt_model.addConstraint(
                  team_trade_in[i] >= trade_in[j], name="".format(i, j))
              for i in teams_to_trade_with for j in to_trade_in_picks if trade_optimiser_df_to_trade_in_dict['Current_Owner'][j] == i}

        c0_1 = opt_model.addConstraint(plp.lpSum(team_trade_in[i] for i in teams_to_trade_with) == 1,
                                       name="c0_1_"+str({0}))

        # Constraint 1 - Which Display_Name_Detailed to include

        if(len(c1_set) > 0):
            picks_to_trade_out_df = trade_optimiser_df_team[trade_optimiser_df_team['Display_Name_Detailed'].isin(
                list(c1_set))]
            picks_to_trade_out = picks_to_trade_out_df['Display_Name_Detailed'].to_numpy(
            )

            c1 = {(i): opt_model.addConstraint(trade_out[i] == 1,
                                               name="c1_"+str({0}).format(i))
                  for i in picks_to_trade_out}

            if(c1_type == "Fixed"):
                c1_1 = {(i):
                        opt_model.addConstraint(trade_out[i] == 0,
                                                name="c1_1_".format(i))
                        for i in owned_picks if i not in picks_to_trade_out}

             # Constraint 2 - Which Season to send

        if(len(c2_set) > 0):
            picks_to_trade_out_df = trade_optimiser_df_team[trade_optimiser_df_team['Year'].isin(
                c2_set)]
            picks_to_trade_out = picks_to_trade_out_df['Display_Name_Detailed'].to_numpy(
            )
            for y in c2_set:
                c2 = opt_model.addConstraint(plp.lpSum(trade_out[i] for i in owned_picks if trade_optimiser_df_team_dict["Year"][i] == y) >= 1,
                                             name="c2_"+str({0}).format(y))
            if(c2_type == "Fixed"):
                c2_1 = {(i):
                        opt_model.addConstraint(trade_out[i] == 0,
                                                name="c2_1_"+str({0}).format(i))
                        for i in owned_picks if i not in picks_to_trade_out}

           # Constraint 3 - Which Draft_Round to send

        if(len(c3_set) > 0):
            picks_to_trade_out_df = trade_optimiser_df_team[trade_optimiser_df_team['Draft_Round'].isin(
                c3_set)]
            picks_to_trade_out = picks_to_trade_out_df['Display_Name_Detailed'].to_numpy(
            )
            for c in c3_set:

                c2 = opt_model.addConstraint(plp.lpSum(trade_out[i] for i in owned_picks if trade_optimiser_df_team_dict["Draft_Round"][i] == c) >= 1,
                                             name="c2_"+str({0}).format(c))

            if(c3_type == "Fixed"):
                c3_1 = {(i):
                        opt_model.addConstraint(trade_out[i] == 0,
                                                name="c3_1_"+str({0}).format(i))
                        for i in owned_picks if i not in picks_to_trade_out}

        #   Constraint 4 - Minimum value to send

        if(c4_type == "Fixed" or c4_type == "Include"):
            c4 = opt_model.addConstraint(plp.lpSum(trade_out[i]*int(trade_optimiser_df_team_dict["AFL_Points_Value"][i]) for i in owned_picks) >= int(c4_set),
                                         name="c4_"+str({0}))

        # Constraint 5 - Minimum value to send

        if(c5_type == "Fixed" or c5_type == "Include"):
            c5 = opt_model.addConstraint(plp.lpSum(trade_out[i]*int(trade_optimiser_df_team_dict["AFL_Points_Value"][i]) for i in owned_picks) <= int(c5_set),
                                         name="c5_"+str({0}))

            #   Constraint 6 - Current_Owner to receive from

        if(len(c6_set) > 0):
            trade_optimiser_df_to_trade_in_df = trade_optimiser_df_to_trade_in[trade_optimiser_df_to_trade_in['Current_Owner'].isin(
                c6_set)]
            trade_optimiser_df_to_buy_list = trade_optimiser_df_to_trade_in_df['Display_Name_Detailed'].to_numpy(
            )

            c6 = {(i): opt_model.addConstraint(trade_in[i] == 1,
                                               name="c6_"+str({0}).format(i))
                  for i in trade_optimiser_df_to_buy_list}

        # Constraint 7 - Which Display_Name_Detailed to receive

        if(len(c7_set) > 0):
            trade_optimiser_df_to_trade_in_df = trade_optimiser_df_to_trade_in[
                trade_optimiser_df_to_trade_in['Display_Name_Detailed'].isin(c7_set)]
            trade_optimiser_df_to_buy_list = trade_optimiser_df_to_trade_in_df['Display_Name_Detailed'].to_numpy(
            )
            c7 = {(i): opt_model.addConstraint(trade_in[i] == 1,
                                               name="c7_"+str({0}).format(i))
                  for i in trade_optimiser_df_to_buy_list}

            if(c7_type == "Fixed"):
                c7_1 = {(i):
                        opt_model.addConstraint(trade_in[i] == 0,
                                                name="c7_1_"+str({0}).format(i))
                        for i in to_trade_in_picks if i not in trade_optimiser_df_to_buy_list}
        # Constraint 8 - Which Season to receive

        if(len(c8_set) > 0):
            trade_optimiser_df_to_trade_in_df = trade_optimiser_df_to_trade_in[trade_optimiser_df_to_trade_in['Year'].isin(
                c8_set)]
            trade_optimiser_df_to_buy_list = trade_optimiser_df_to_trade_in_df['Display_Name_Detailed'].to_numpy(
            )
            for y in c8_set:
                c8 = opt_model.addConstraint(plp.lpSum(trade_in[i] for i in to_trade_in_picks if trade_optimiser_df_to_trade_in_dict["Year"][i] == y) >= 1,
                                             name="c8_"+str({0}).format(y))

            if(c8_type == "Fixed"):
                c8_1 = {(i):
                        opt_model.addConstraint(trade_in[i] == 0,
                                                name="c8_1_"+str({0}).format(i))
                        for i in to_trade_in_picks if i not in trade_optimiser_df_to_buy_list}

          # Constraint 9 - Which Draft_Round to receive

        if(len(c9_set) > 0):
            trade_optimiser_df_to_trade_in_df = trade_optimiser_df_to_trade_in[trade_optimiser_df_to_trade_in['Draft_Round'].isin(
                c9_set)]

            trade_optimiser_df_to_buy_list = trade_optimiser_df_to_trade_in_df['Display_Name_Detailed'].to_numpy(
            )
            for c in c9_set:
                c9 = opt_model.addConstraint(plp.lpSum(trade_in[i] for i in to_trade_in_picks if trade_optimiser_df_to_trade_in_dict["Draft_Round"][i] == c) >= 1,
                                             name="c9_"+str({0}).format(c))

            if(c9_type == "Fixed"):
                c9_1 = {(i):
                        opt_model.addConstraint(trade_in[i] == 0,
                                                name="".format(i))
                        for i in to_trade_in_picks if i not in trade_optimiser_df_to_buy_list}

        # Constraint 10 - Minimum value to receive
            if(c10_type == "Fixed" or c10_type == "Include"):
                c10 = opt_model.addConstraint(plp.lpSum(trade_in[i]*int(trade_optimiser_df_to_trade_in_dict["AFL_Points_Value"][i]) for i in to_trade_in_picks) >= int(c10_set),
                                              name="c10_"+str({0}))

           # Constraint 11 - Maximum AFL_Points_Value to receive
            if(c11_type == "Fixed" or c11_type == "Include"):
                c11 = opt_model.addConstraint(plp.lpSum(trade_in[i]*int(trade_optimiser_df_to_trade_in_dict["AFL_Points_Value"][i]) for i in to_trade_in_picks) <= int(c11_set),
                                              name="c11_"+str({0}))

        # Constraint 12 - Max difference of total value
        if trade_optimiser_df_to_trade_in["AFL_Points_Value"].isnull().values.any() == False:
            pass
        else:

            if(c12_type == "Fixed" or c12_type == "Include"):

                c12_1 = opt_model.addConstraint(plp.lpSum(trade_out[i]*int(trade_optimiser_df_team_dict["AFL_Points_Value"][i]) for i in owned_picks) <=
                                                (1 + c12_set)*plp.lpSum(
                    trade_in[i]*int(trade_optimiser_df_to_trade_in_dict["AFL_Points_Value"][i]) for i in to_trade_in_picks),
                    name="c12_1_"+str({0}))

                c12_2 = opt_model.addConstraint((1 + c12_set)*plp.lpSum(trade_out[i]*int(trade_optimiser_df_team_dict["AFL_Points_Value"][i]) for i in owned_picks) >=
                                                plp.lpSum(
                    trade_in[i]*int(trade_optimiser_df_to_trade_in_dict["AFL_Points_Value"][i]) for i in to_trade_in_picks),
                    name="c12_2_"+str({0}))

        c_aux = {(ct):
                 opt_model.addConstraint(plp.lpSum(trade_out for i in trade_out_solutions[ct]) + plp.lpSum(trade_in for i in trade_in_solutions)
                                         <= count_solution[ct] - 1,
                                         name="c_aux_{0}".format(ct))
                 for ct in range(0, sol)}
        # Getting the solution
        opt_model.sense = plp.LpMinimize
        opt_model.setObjective(objective)
        # opt_model.solve(plp.PULP_CBC_CMD(msg=False))
        opt_model.solve()

        if(plp.LpStatus[opt_model.status] == 'Optimal'):

            trade_out_picks_sol = ""
            for i in owned_picks:

                if(trade_out[i].varValue == 0):

                    # trade_out_solutions[sol][i] = 1
                    count_solution[sol] += 1
                    if(trade_out_picks_sol == ""):
                        trade_out_picks_sol += i
                    else:
                        trade_out_picks_sol += ", " + i
                    set(trade_out_picks_sol)
            trade_out_vec.append(trade_out_picks_sol)
            trade_in_sol = ""
            for i in to_trade_in_picks:
                if(trade_in[i].varValue == 0):
                    # trade_in_solutions[sol][i] = 1
                    count_solution[sol] += 1
                    if(trade_in_sol == ""):
                        trade_in_sol += i
                    else:
                        trade_in_sol += ", " + i
            trade_in_vec.append(trade_in_sol)
            sol_index.append(sol+1)
        else:
            print("Problem is infeasible")
            break

    results_df["Suggestion"] = sol_index
    results_df["Trade Out"] = trade_out_vec
    results_df["Trade In"] = trade_in_vec

    # Calculations of Points differences
    # Defining points lists
    AFL_Points_Out = []
    AFL_Points_In = []

    for idx, k in enumerate(trade_out_solutions):
        total_pts = 0
        suggestion = idx + 1
        for v in sorted(k):
            if trade_optimiser_df['AFL_Points_Value'].isnull().values.any():
                trade_optimiser_df['AFL_Points_Value'] = trade_optimiser_df['AFL_Points_Value'].fillna(
                    0)
            else:
                pass
            pick_pts = trade_optimiser_df.loc[trade_optimiser_df.Display_Name_Detailed ==
                                              picks[v], 'AFL_Points_Value'].iloc[0]
            total_ptss = int(pick_pts) + int(total_pts)
            AFL_Points_Out.append(total_ptss)

    # Trade In Points:

    for idx, k in enumerate(trade_in_solutions):
        suggestion = idx + 1
        for v in sorted(k):
            if trade_optimiser_df['AFL_Points_Value'].isnull().values.any():
                trade_optimiser_df['AFL_Points_Value'] = trade_optimiser_df['AFL_Points_Value'].fillna(
                    0)
            else:
                pass
            pick_pts = trade_optimiser_df.loc[trade_optimiser_df.Display_Name_Detailed ==
                                              picks[v], 'AFL_Points_Value'].iloc[0]
            total_ptss = int(pick_pts) + int(total_pts)
            AFL_Points_In.append(total_ptss)

    # Add Columns
    # results_df = {}
    results_df['Points Out'] = AFL_Points_Out

    results_df['Points In'] = AFL_Points_In
    # results_df['Points Diff'] = results_df['Points In'] - \
    #     results_df['Points Out']

    results_df['Points_Diff'] = np.array(
        results_df['Points In']) - np.array(results_df['Points Out']).shape
    data_trade_suggestion(results_df)
    return Response({'trade_algorithm': results_df}, status=status.HTTP_201_CREATED)


def data_trade_suggestion(results_df):
    return results_df


@api_view(['GET'])
@permission_classes([AllowAny])
def ConstraintsRquest(request, pk, userid):

    # userid = data.get('user_id')
    Userobj = User.objects.get(id=userid)
    Teamid = Userobj.Teams.id
    Teamobj = Teams.objects.get(id=Teamid)
    v_team_name = Teamobj.id

    masterlist = dataframerequest(request, pk)
    _my_dict = {}

    _my_dict['constraints_1'] = masterlist[masterlist['Current_Owner'].astype(
        int) == int(v_team_name)]['Display_Name_Detailed'].tolist()

    _my_dict['c1_type'] = "Fixed"
    _my_dict['constraints_2'] = masterlist[masterlist['Current_Owner'].astype(
        int) == int(v_team_name)]['Year'].unique().tolist()
    _my_dict['c2_type'] = "Fixed"
    _my_dict['constraints_3'] = masterlist[masterlist['Current_Owner'].astype(
        int) == int(v_team_name)]['Draft_Round'].unique().tolist()
    _my_dict['c3_type'] = "Fixed"
    _my_dict['constraints_4'] = [0]
    _my_dict['c4_type'] = "Fixed"
    _my_dict['constraints_5'] = [99999999]
    _my_dict['c5_type'] = "Fixed"
    _my_dict['constraints_6'] = masterlist[masterlist['Current_Owner'].astype(
        int) != int(v_team_name)]['Current_Owner'].unique().tolist()
    _my_dict['c6_type'] = "Fixed"
    _my_dict['constraints_7'] = masterlist[masterlist['Current_Owner'].astype(
        int) != int(v_team_name)]['Display_Name_Detailed'].unique().tolist()
    _my_dict['c7_type'] = "Fixed"
    _my_dict['constraints_8'] = masterlist[masterlist['Current_Owner'].astype(
        int) != int(v_team_name)]['Year'].unique().tolist()
    _my_dict['c8_type'] = "Fixed"
    _my_dict['constraints_9'] = masterlist[masterlist['Current_Owner'].astype(
        int) != int(v_team_name)]['Draft_Round'].unique().tolist()
    _my_dict['c9_type'] = "Fixed"
    _my_dict['constraints_10'] = [0]
    _my_dict['c10_type'] = "Fixed"
    _my_dict['constraints_11'] = [99999999]
    _my_dict['c11_type'] = "Fixed"
    _my_dict['constraints_12'] = [0.10]
    _my_dict['c12_type'] = "Fixed"
    _my_dict['constraints_13'] = [0]
    _my_dict['c13_type'] = "Fixed"
    _my_dict['constraints_14'] = [10]
    _my_dict['c14_type'] = "Fixed"

    return Response(_my_dict, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def GetFlagPicks(request, pk):

    PicksList = []
    queryobj = MasterList.objects.filter(TeamName_id=pk).values()
    for data in queryobj:
        PicksList.append(data['Display_Name_Detailed'])
    return Response({'PicksList': PicksList}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def GetPickType(request):
    Picktypes = []
    PicksQuery = PicksType.objects.filter().values()
    for types in PicksQuery:
        Picktypes.append(types['pickType'])
    return Response({'Picktype': Picktypes}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def GetRounds(request):
    roundslist = list()
    QuerySet = DraftRound.objects.filter().values()
    for rounds in QuerySet:
        roundslist.append(rounds)
    return Response({'roundslist': roundslist}, status=status.HTTP_201_CREATED)


def get_images(request, shortnames):
    Get_images = []
    sliced_shortnames = shortnames[1:18]

    _queryset = Teams.objects.filter(ShortName__in=sliced_shortnames).values()
    for data in _queryset:
        base_url = request.build_absolute_uri('/').strip("/")
        image_with_path = base_url+'/'+'media'+'/' + data['Image']
        Get_images.append(image_with_path)
    Images = tuple(Get_images)
    return Images


@api_view(['GET'])
@permission_classes([AllowAny])
def Get_Rounds_Pick(request, pk):

    df = dataframerequest(request, pk)

    # df['column'] = np.zeros(len(df))
    # df['column'].describe()
    # df = df[~df.isin([np.nan, np.inf, -np.inf]).any(1)]
    # print( df['column'])
    # exit()
    current_date = date.today()

    v_current_year = current_date.year
    v_current_year_plus1 = v_current_year+1

    Current_Year_Round = {}
    Next_Year_Round = {}
    img = tuple()
    df["Images"] = ""
    # Current Year list
    data_current_rd1_list = []
    data_current_rd2_list = []
    data_current_rd3_list = []
    data_current_rd4_list = []
    data_current_rd5_list = []
    data_current_rd6_list = []

    # Next year list
    data_next_rd1_list = []
    data_next_rd2_list = []
    data_next_rd3_list = []
    data_next_rd4_list = []
    data_next_rd5_list = []
    data_next_rd6_list = []

    current_day = date.today()
    this_year = current_day.year

    data_current_year_rd1 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD1')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'Images', 'AFL_Points_Value']]
    Display_Name_Short = data_current_year_rd1['Display_Name_Short'].astype(
        str).values.flatten().tolist()

    short_name = list(Display_Name_Short)
    overall_pick = data_current_year_rd1['Overall_Pick'].astype(
        str).values.flatten().tolist()

    overall_pick = [x for x in overall_pick]
    current_rd1_team_list = []
    for k in short_name:

        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')

        for data in query:
            team_dict = {}
            team_dict['Image'] = data['Image']
            team_dict['ShortName'] = data['ShortName']
            current_rd1_team_list.append(team_dict.copy())

        for key, values in data_current_year_rd1.iterrows():
            for data in current_rd1_team_list:
                if data['ShortName'] == values['Display_Name_Short']:
                    data_current_year_rd1_dict = {}
                    base_url = request.build_absolute_uri('/').strip("/")
                    image_with_path = base_url+'/'+'media'+'/' + data['Image']
                    data_current_year_rd1_dict['Images'] = image_with_path
                    data_current_year_rd1_dict['Draft_Round'] = values['Draft_Round']
                    data_current_year_rd1_dict['Overall_Pick'] = values['Overall_Pick']
                    data_current_year_rd1_dict['Display_Name_Short'] = values['Display_Name_Short']
                    data_current_year_rd1_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                    data_current_rd1_list.append(
                        data_current_year_rd1_dict.copy())
                    break
    data_current_year_rd1_list = [k for j, k in enumerate(
        data_current_rd1_list) if k not in data_current_rd1_list[j + 1:]]

    current_rd2_team_list = []
    data_current_year_rd2 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD2')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    Display_Name_Short_rd2 = data_current_year_rd2['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    for k in Display_Name_Short_rd2:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')
        for data in query:
            team_dict = {}
            team_dict['Image'] = data['Image']
            team_dict['ShortName'] = data['ShortName']
            current_rd2_team_list.append(team_dict.copy())
        for key, values in data_current_year_rd2.iterrows():
            for data in current_rd2_team_list:
                if data['ShortName'] == values['Display_Name_Short']:

                    data_current_year_rd2_dict = {}
                    base_url = request.build_absolute_uri('/').strip("/")
                    image_with_path = base_url+'/'+'media'+'/' + data['Image']
                    data_current_year_rd2_dict['Images'] = image_with_path
                    data_current_year_rd2_dict['Draft_Round'] = values['Draft_Round']
                    data_current_year_rd2_dict['Overall_Pick'] = values['Overall_Pick']
                    data_current_year_rd2_dict['Display_Name_Short'] = values['Display_Name_Short']
                    data_current_year_rd2_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                    data_current_rd2_list.append(
                        data_current_year_rd2_dict.copy())

                    break
    data_current_year_rd2_list = [k for j, k in enumerate(
        data_current_rd2_list) if k not in data_current_rd2_list[j + 1:]]
    data_current_year_rd3 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD3')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    teams = []
    Display_Name_Short_rd3 = data_current_year_rd3['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    for k in Display_Name_Short_rd3:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')
        for data in query:
            team_dict = {}
            team_dict['Image'] = data['Image']
            team_dict['ShortName'] = data['ShortName']
            teams.append(team_dict.copy())

    for key, values in data_current_year_rd3.iterrows():
        for data in teams:
            if data['ShortName'] == values['Display_Name_Short']:

                data_current_year_rd3_dict = {}
                base_url = request.build_absolute_uri('/').strip("/")
                image_with_path = base_url+'/'+'media'+'/' + data['Image']
                data_current_year_rd3_dict['Images'] = image_with_path
                data_current_year_rd3_dict['Draft_Round'] = values['Draft_Round']
                data_current_year_rd3_dict['Overall_Pick'] = values['Overall_Pick']
                data_current_year_rd3_dict['Display_Name_Short'] = values['Display_Name_Short']
                data_current_year_rd3_dict['AFL_Points_Value'] = values['AFL_Points_Value']

                data_current_rd3_list.append(
                    data_current_year_rd3_dict.copy())
    data_current_year_rd3_list = [k for j, k in enumerate(
        data_current_rd3_list) if k not in data_current_rd3_list[j + 1:]]
    current_rd_4_team_list = []
    data_current_year_rd4 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD4')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    Display_Name_Short_rd4 = data_current_year_rd4['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    for k in Display_Name_Short_rd4:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')
        for data in query:
            teams_dict = {}
            teams_dict['Image'] = data['Image']
            team_dict['ShortName'] = data['ShortName']
            current_rd_4_team_list.append(team_dict.copy())

    for key, values in data_current_year_rd4.iterrows():
        for data in current_rd_4_team_list:
            if data['ShortName'] == values['Display_Name_Short']:

                data_current_year_rd4_dict = {}
                base_url = request.build_absolute_uri('/').strip("/")
                image_with_path = base_url+'/'+'media'+'/' + data['Image']
                data_current_year_rd4_dict['Images'] = image_with_path
                data_current_year_rd4_dict['Draft_Round'] = values['Draft_Round']
                data_current_year_rd4_dict['Overall_Pick'] = values['Overall_Pick']
                data_current_year_rd4_dict['Display_Name_Short'] = values['Display_Name_Short']
                data_current_year_rd4_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                data_current_rd4_list.append(
                    data_current_year_rd4_dict.copy())
                break
    data_current_year_rd4_list = [k for j, k in enumerate(
        data_current_rd4_list) if k not in data_current_rd4_list[j + 1:]]
    current_rd_4_team_list = []
    data_current_year_rd5 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD5')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]

    Display_Name_Short_rd5 = data_current_year_rd5['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    for k in Display_Name_Short_rd5:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')

        for data in query:
            teams_dict = {}
            teams_dict['Image'] = data['Image']
            teams_dict['ShortName'] = data['ShortName']
            current_rd_4_team_list.append(teams_dict.copy())
        for key, values in data_current_year_rd5.iterrows():
            for data in current_rd_4_team_list:
                if data['ShortName'] == values['Display_Name_Short']:

                    data_current_year_rd5_dict = {}
                    base_url = request.build_absolute_uri('/').strip("/")
                    image_with_path = base_url+'/'+'media'+'/' + data['Image']
                    data_current_year_rd5_dict['Images'] = image_with_path
                    data_current_year_rd5_dict['Draft_Round'] = values['Draft_Round']
                    data_current_year_rd5_dict['Overall_Pick'] = values['Overall_Pick']
                    data_current_year_rd5_dict['Display_Name_Short'] = values['Display_Name_Short']
                    data_current_year_rd5_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                    data_current_rd5_list.append(
                        data_current_year_rd5_dict.copy())
                    break
    data_current_year_rd5_list = [k for j, k in enumerate(
        data_current_rd5_list) if k not in data_current_rd5_list[j + 1:]]
    data_current_year_rd6 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD6')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    Display_Name_Short_rd6 = data_current_year_rd6['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    current_rd_6_team_list = []
    for k in Display_Name_Short_rd6:

        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')
        for data in query:
            teams_dict = {}
            teams_dict['Image'] = data['Image']
            teams_dict['ShortName'] = data['ShortName']
            current_rd_6_team_list.append(teams_dict.copy())
        for key, values in data_current_year_rd6.iterrows():

            for data in current_rd_6_team_list:
                if data['ShortName'] == values['AFL_Points_Value']:
                    data_current_year_rd6_dict = {}
                    base_url = request.build_absolute_uri('/').strip("/")
                    image_with_path = base_url+'/'+'media'+'/' + data['Image']
                    data_current_year_rd6_dict['Images'] = image_with_path
                    data_current_year_rd6_dict['Draft_Round'] = values['Draft_Round']
                    data_current_year_rd6_dict['Overall_Pick'] = values['Overall_Pick']
                    data_current_year_rd6_dict['Display_Name_Short'] = values['Display_Name_Short']
                    data_current_year_rd6_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                    data_current_rd6_list.append(
                        data_current_year_rd6_dict.copy())
                    break
    data_current_year_rd6_list = [k for j, k in enumerate(
        data_current_rd6_list) if k not in data_current_rd6_list[j + 1:]]
    # Next Year Round by Round:

    next_year_rd1_images = []
    next_year_rd2_images = []
    next_year_rd3_images = []
    next_year_rd4_images = []
    next_year_rd5_images = []
    next_year_rd6_images = []
    next_year = this_year+1
    data_next_year_rd1 = df[(df.Year.astype(int) == v_current_year_plus1) & (df['Draft_Round'] == 'RD1')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]
    Display_Name_Short_rd1_nextyear = data_next_year_rd1['Display_Name_Short'].astype(
        str).values.flatten().tolist()

    for k in Display_Name_Short_rd1_nextyear:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')
        for data in query:
            dict = {}
            dict['ShortName'] = data['ShortName']
            base_url = request.build_absolute_uri('/').strip("/")
            dict['image_with_path'] = base_url+'/'+'media'+'/' + data['Image']
            next_year_rd1_images.append(dict.copy())

    for key, values in data_current_year_rd5.iterrows():
        for img in next_year_rd1_images:
            if img['ShortName'] == values['Display_Name_Short']:
                data_next_year_rd1_dict = {}
                data_next_year_rd1_dict['Images'] = img['image_with_path']
                data_next_year_rd1_dict['Draft_Round'] = values['Draft_Round']
                data_next_year_rd1_dict['Overall_Pick'] = values['Overall_Pick']
                data_next_year_rd1_dict['Display_Name_Short'] = values['Display_Name_Short']
                data_next_year_rd1_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                data_next_rd1_list.append(
                    data_next_year_rd1_dict.copy())
    data_next_year_rd1_list = [k for j, k in enumerate(
        data_next_rd1_list) if k not in data_next_rd1_list[j + 1:]]
    data_next_year_rd2 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD2')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    Display_Name_Short_rd2_nextyear = data_next_year_rd2['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    for k in Display_Name_Short_rd2_nextyear:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')
        for data in query:
            dict = {}
            dict['ShortName'] = data['ShortName']
            base_url = request.build_absolute_uri('/').strip("/")
            dict['image_with_path'] = base_url+'/'+'media'+'/' + data['Image']
            next_year_rd2_images.append(dict.copy())

    for key, values in data_next_year_rd2.iterrows():
        for img in next_year_rd2_images:
            if img['ShortName'] == values['Display_Name_Short']:
                data_next_year_rd2_dict = {}
                data_next_year_rd2_dict['Images'] = img['image_with_path']
                data_next_year_rd2_dict['Draft_Round'] = values['Draft_Round']
                data_next_year_rd2_dict['Overall_Pick'] = values['Overall_Pick']
                data_next_year_rd2_dict['Display_Name_Short'] = values['Display_Name_Short']
                data_next_year_rd2_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                data_next_rd2_list.append(
                    data_next_year_rd2_dict.copy())
    data_next_year_rd2_list = [k for j, k in enumerate(
        data_next_rd2_list) if k not in data_next_rd2_list[j + 1:]]
    data_next_year_rd3 = df[(df.Year.astype(int) == v_current_year_plus1) & (df['Draft_Round'] == 'RD1')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    Display_Name_Short_rd3_nextyear = data_next_year_rd3['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    for k in Display_Name_Short_rd3_nextyear:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')
        for data in query:
            dict = {}
            dict['ShortName'] = data['ShortName']
            base_url = request.build_absolute_uri('/').strip("/")
            dict['image_with_path'] = base_url+'/'+'media'+'/' + data['Image']
            next_year_rd3_images.append(dict.copy())

    for key, values in data_current_year_rd5.iterrows():

        for img in next_year_rd2_images:
            if img['ShortName'] == values['Display_Name_Short']:
                data_next_year_rd3_dict = {}
                data_next_year_rd3_dict['Images'] = img['image_with_path']
                data_next_year_rd3_dict['Draft_Round'] = values['Draft_Round']
                data_next_year_rd3_dict['Overall_Pick'] = values['Overall_Pick']
                data_next_year_rd3_dict['Display_Name_Short'] = values['Display_Name_Short']
                data_next_year_rd3_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                data_next_rd3_list.append(
                    data_next_year_rd3_dict.copy())
    data_next_year_rd3_list = [k for j, k in enumerate(
        data_next_rd3_list) if k not in data_next_rd3_list[j + 1:]]
    data_next_year_rd4 = df[(df.Year.astype(int) == v_current_year_plus1) & (df.Draft_Round == 'RD4')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    Display_Name_Short_rd4_nextyear = data_next_year_rd4['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    for k in Display_Name_Short_rd4_nextyear:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')
        for data in query:
            dict = {}
            dict['ShortName'] = data['ShortName']
            base_url = request.build_absolute_uri('/').strip("/")
            dict['image_with_path'] = base_url+'/'+'media'+'/' + data['Image']
            next_year_rd4_images.append(dict.copy())

    for key, values in data_current_year_rd5.iterrows():

        for img in next_year_rd2_images:
            if img['ShortName'] == values['Display_Name_Short']:
                data_next_year_rd4_dict = {}
                data_next_year_rd4_dict['Images'] = img['image_with_path']
                data_next_year_rd4_dict['Draft_Round'] = values['Draft_Round']
                data_next_year_rd4_dict['Overall_Pick'] = values['Overall_Pick']
                data_next_year_rd4_dict['Display_Name_Short'] = values['Display_Name_Short']
                data_next_year_rd4_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                data_next_rd4_list.append(
                    data_next_year_rd4_dict.copy())
    data_next_year_rd4_list = [k for j, k in enumerate(
        data_next_rd4_list) if k not in data_next_rd4_list[j + 1:]]
    data_next_year_rd5 = df[(df.Year.astype(int) == v_current_year_plus1) & (df.Draft_Round == 'RD5')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    Display_Name_Short_rd5_nextyear = data_next_year_rd5['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    for k in Display_Name_Short_rd5_nextyear:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')
        for data in query:
            dict = {}
            dict['ShortName'] = data['ShortName']
            base_url = request.build_absolute_uri('/').strip("/")
            dict['image_with_path'] = base_url+'/'+'media'+'/' + data['Image']
            next_year_rd5_images.append(dict.copy())

    for key, values in data_current_year_rd5.iterrows():
        for img in next_year_rd2_images:
            if img['ShortName'] == values['Display_Name_Short']:
                data_next_year_rd5_dict = {}
                data_next_year_rd5_dict['Images'] = img['image_with_path']
                data_next_year_rd5_dict['Draft_Round'] = values['Draft_Round']
                data_next_year_rd5_dict['Overall_Pick'] = values['Overall_Pick']
                data_next_year_rd5_dict['Display_Name_Short'] = values['Display_Name_Short']
                data_next_year_rd5_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                data_next_rd5_list.append(
                    data_next_year_rd5_dict.copy())
    data_next_year_rd5_list = [k for j, k in enumerate(
        data_next_rd5_list) if k not in data_next_rd5_list[j + 1:]]
    data_next_year_rd6 = df[(df.Year.astype(int) == v_current_year_plus1) & (df.Draft_Round == 'RD6')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]
    data_next_year_rd6 = data_next_year_rd6['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    for k in data_next_year_rd6:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')
        for data in query:
            dict = {}
            dict['ShortName'] = data['ShortName']
            base_url = request.build_absolute_uri('/').strip("/")
            dict['image_with_path'] = base_url+'/'+'media'+'/' + data['Image']
            next_year_rd6_images.append(dict.copy())

    for key, values in data_current_year_rd5.iterrows():
        for img in next_year_rd2_images:

            if img['ShortName'] == values['Display_Name_Short']:

                data_next_year_rd6_dict = {}
                data_next_year_rd6_dict['Images'] = img['image_with_path']
                data_next_year_rd6_dict['Draft_Round'] = values['Draft_Round']
                data_next_year_rd6_dict['Overall_Pick'] = values['Overall_Pick']
                data_next_year_rd6_dict['Display_Name_Short'] = values['Display_Name_Short']
                data_next_year_rd6_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                data_next_rd6_list.append(
                    data_next_year_rd6_dict.copy())
    data_next_year_rd6_list = [k for j, k in enumerate(
        data_next_rd6_list) if k not in data_next_rd6_list[j + 1:]]
    # Order of Entry Table
    masterlist = dataframerequest(request, pk)
    data_order_of_entry_list = []
    data_order_of_entry = masterlist[(masterlist.Year.astype(int) == int(v_current_year_plus1))][[
        'TeamName', 'Overall_Pick', 'Club_Pick_Number']].sort_values(by='Overall_Pick')
    data_order_of_entry = pd.crosstab(
        data_order_of_entry.TeamName, data_order_of_entry.Club_Pick_Number, values=data_order_of_entry.Overall_Pick, aggfunc=sum)
    data_order_of_entry_list = []
    array = np.array(data_order_of_entry)

    draft_pick_list = []

    for j in data_order_of_entry.keys():
        draft_pick_list.append(j)

    queryset = Teams.objects.filter().values()
    for k in queryset:
        for val in array:
            for data in val:
                data_order_dict = {}
                teamname = k['TeamNames']
                data_order_dict[teamname] = str(
                    data) + "," + str(draft_pick_list)
                data_order_of_entry_list.append(data_order_dict.copy())

    unique_dict = [k for j, k in enumerate(
        data_order_of_entry_list) if k not in data_order_of_entry_list[j + 1:]]

    # print(len(data_order_of_entry))
    # for  value in data_order_of_entry.keys():
    #     #print(key)
    #     data_order_dict = {}
    #     # data_order_dict['TeamName'] = team_name['TeamNames']
    #     # data_order_dict['Overall_Pick'] = value['Overall_Pick']
    #     data_order_dict['Club_Pick_Number'] = value['Club_Pick_Number']
    #     data_order_of_entry_list.append(data_order_dict.copy())
    # print(data_order_of_entry_list)

    # data_order_of_entry = pd.crosstab(data_order_of_entry.TeamName, data_order_of_entry.Club_Pick_Number, values=data_order_of_entry.Overall_Pick,aggfunc=sum)

    data_order_of_entry.reset_index(drop=True, inplace=True)
    data_order_of_entry_dict = data_order_of_entry.to_dict(orient="index")

    # Draft Assets Graph - Bar Graph

    _dict = {}
    graph_list = []
    data_draft_assets_graph = df.groupby(['Current_Owner_Short_Name', 'Year'])[
        'AFL_Points_Value'].sum()
    dict = data_draft_assets_graph.items()
    for data in dict:

        _dict['shortname'] = list(data).pop(0)[0]
        _dict['Year'] = list(data).pop(0)[1]
        _dict['AFL_POINTS'] = list(data).pop(1)
        graph_list.append(_dict)

    ##### Full List of Draft Picks #####
    data_full_masterlist_list = []
    data_full_masterlist = df[['Year', 'Draft_Round', 'Overall_Pick', 'TeamName',
                               'PickType', 'Original_Owner', 'Current_Owner', 'Previous_Owner', 'AFL_Points_Value', 'Club_Pick_Number']]

    TeamIds = data_full_masterlist['TeamName'].astype(
        int).values.flatten().tolist()
    k = list(TeamIds)
    for ids in k:
        queryset = Teams.objects.filter(id=ids).values()
        for data in queryset:

            for key, values in data_full_masterlist.iterrows():

                masterlist_full_dict = {}
                masterlist_full_dict['Year'] = values['Year']
                masterlist_full_dict['Draft_Round'] = values['Draft_Round']
                masterlist_full_dict['Overall_Pick'] = values['Overall_Pick']
                masterlist_full_dict['TeamName'] = data['TeamNames']
                masterlist_full_dict['PickType'] = values['PickType']
                masterlist_full_dict['Original_Owner'] = data['TeamNames']
                masterlist_full_dict['Current_Owner'] = data['TeamNames']
                masterlist_full_dict['Previous_Owner'] = data['TeamNames']
                masterlist_full_dict['AFL_Points_Value'] = values['AFL_Points_Value']
                masterlist_full_dict['Club_Pick_Number'] = values['Club_Pick_Number']
                data_full_masterlist_list.append(
                    masterlist_full_dict.copy())
                break
    return Response({'this_year': this_year, 'next_year': next_year, 'data_current_year_rd1_list': data_current_year_rd1_list, 'data_current_year_rd2': data_current_year_rd2_list, 'data_current_year_rd3': data_current_year_rd3_list, 'data_current_year_rd4': data_current_year_rd4_list, 'data_current_year_rd5': data_current_year_rd5_list, 'data_current_year_rd6': data_current_year_rd6_list, 'data_next_year_rd1': data_next_year_rd1_list, 'data_next_year_rd2': data_next_year_rd2_list, 'data_next_year_rd3': data_next_year_rd3_list, 'data_next_year_rd4': data_next_year_rd4_list, 'data_next_year_rd5': data_next_year_rd5_list, 'data_next_year_rd6': data_next_year_rd6_list, 'data_full_masterlist': data_full_masterlist_list, 'data_order_of_entry': unique_dict, 'graph_list': graph_list}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def CreateCompany(request):

    Company_obj = request.data
    serializer = MakeCompanySerializer(data=Company_obj)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    fk = serializer.data['projectId']
    ProjectId = Project.objects.filter(id=fk).values('id', 'project_name')
    return Response({'success': 'Company Created Successfuly', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def AddTeamRequest(request):
    TeamObj = request.data
    serializer = TeamSerializer(data=TeamObj)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'success': 'Team Created Successfuly', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def DraftAnalyserRequest(request):
    try:
        Draftrequest = request.data
        serializer = DraftAnalyserSerializer(data=Draftrequest)
        serializer.valid(raiseExceptions=True)
        return Response({'success': 'Trade created successfully'}, statu=status.HTTP_201_CREATED)

    except Exception as e:
        raise e


@ api_view(["POST"])
@ permission_classes([AllowAny, ])
def ProjPlayer(request, format=None):
    serializer = PlayersSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': 'Player has been created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def add_father_son_input(request):

    data = request.data
    fs_player = data.get('playerid')
    fs_teamm = data.get('fs_team')
    fs_bid = data.get('pickid')
    return fs_player, fs_teamm, fs_bid


@api_view(['POST'])
@permission_classes([AllowAny])
def add_father_son(request, pk):
    current_date = date.today()
    v_current_year = current_date.year
    v_current_year_plus1 = v_current_year+1

    fs_player, fs_teamm, fs_bid = add_father_son_input(request)

    teamobj = Teams.objects.get(id=fs_teamm)
    fs_teamname = teamobj.TeamNames

    df = dataframerequest(request, pk)

    # obj=MasterList.objects.get(id=fs_bid)
    # fs_pick=obj.Display_Name_Detailed
    list = []
    queryset = MasterList.objects.filter(id__in=[fs_bid]).values()
    for query in queryset:
        list.append(query['Display_Name_Detailed'])
    fs_pick = "".join(list)

    fs_pts_value = df.loc[df.Display_Name_Detailed ==
                          fs_pick, 'AFL_Points_Value'].iloc[0]
    fs_bid_round = df.loc[df.Display_Name_Detailed ==
                          fs_pick, 'Draft_Round'].iloc[0]
    fs_bid_round_int = df.loc[df.Display_Name_Detailed ==
                              fs_pick, 'Draft_Round_Int'].iloc[0]
    fs_bid_team = df.loc[df.Display_Name_Detailed ==
                         fs_pick, 'Current_Owner'].iloc[0]
    fs_bid_pick_no = df.loc[df.Display_Name_Detailed ==
                            fs_pick, 'Overall_Pick'].iloc[0]

    fs_pick_type = 'Father Son Bid Match'

    sum_line1 = str(fs_bid_team) + ' have placed a bid on a ' + str(fs_teamm) + \
        ' Father Son player at pick ' + \
        str(fs_bid_pick_no) + ' in ' + fs_bid_round

    # Defining discounts based off what round the bid came in:
    if fs_bid_round == 'RD1':
        fs_pts_required = float(fs_pts_value) * .8

        sum_line2 = str(fs_teamname) + ' will require ' + \
            str(fs_pts_required) + ' draft points to match bid.'
    else:
        fs_pts_required = float(fs_pts_value) - 197
        sum_line2 = str(fs_teamname) + ' will require ' + \
            str(fs_pts_required) + ' draft points to match bid.'
    df_subset = df.copy()

    Overall_pick = (df_subset.Overall_Pick).fillna(0)
    if Overall_pick.isnull().values.any() == False:

        df_subset = df_subset[(df_subset.Current_Owner.astype(int) == int(fs_teamm)) & (df_subset.Year.astype(
            int) == int(v_current_year))]
    else:
        df_subset = df_subset[(df_subset.Current_Owner.astype(int) == int(fs_teamm)) & (df_subset.Year.astype(
            int) == int(v_current_year)) & (Overall_pick.astype(int) >= int(fs_bid_pick_no))]

    # Creating the cumulative calculations to determine how the points are repaid:

    df_subset['Cumulative_Pts'] = df_subset.groupby(
        'Current_Owner')['AFL_Points_Value'].transform(pd.Series.cumsum)

    df_subset['Payoff_Diff'] = df_subset['Cumulative_Pts'].astype(
        float) - fs_pts_required
    df_subset['AFL_Pts_Left'] = np.where(
        df_subset['Payoff_Diff'] <= 0,
        0,
        np.where(
            df_subset['Payoff_Diff'] < df_subset['AFL_Points_Value'].astype(
                float),
            df_subset['Payoff_Diff'],
            df_subset['AFL_Points_Value']
        )
    )

    df_subset['AFL_Pts_Left_previous_pick'] = df_subset['AFL_Pts_Left'].shift()
    df_subset['AFL_Pts_Value_previous_pick'] = df_subset['AFL_Points_Value'].shift()

    df_subset['Action'] = np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'] == 0),
                                   'Pick lost to back of draft',
                                   np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'].astype(int) > 0),
                                            'Pick Shuffled Backwards',
                                            np.where((df_subset['AFL_Pts_Left'] == df_subset['AFL_Points_Value']) & (df_subset['Payoff_Diff'] < 0) & (df_subset['AFL_Pts_Value_previous_pick'].astype(float) > 0), 'Points Deficit',
                                                     'No Change')))

    # Add a column for the deficit amount and then define it as a variable:
    df_subset['Deficit_Amount'] = np.where(
        df_subset['Action'] == 'Points Deficit', df_subset['Payoff_Diff'], np.nan)

    try:
        fs_points_deficit = df_subset.loc[df_subset.Action ==
                                          'Points Deficit', 'Deficit_Amount'].iloc[0]
    except:
        fs_points_deficit = []

    # Create lists of changes to make:
    picks_lost = df_subset.loc[df_subset.Action ==
                               'Pick lost to back of draft', 'Display_Name_Detailed'].to_list()

    picks_shuffled = df_subset.loc[df_subset.Action ==
                                   'Pick Shuffled Backwards', 'Display_Name_Detailed'].to_list()
    pick_deficit = df_subset.loc[df_subset.Action ==
                                 'Points Deficit', 'Display_Name_Detailed'].to_list()

    try:
        picks_shuffled_points_value = df_subset.loc[df_subset.Action ==
                                                    'Pick Shuffled Backwards', 'AFL_Pts_Left'].iloc[0]
    except:
        picks_shuffled_points_value = np.nan

    carry_over_deficit = fs_points_deficit

    if len(picks_lost) > 0:
        pick_lost_details = pd.DataFrame(
            columns=['Pick', 'Moves_To', 'New_Points_Value'])

        for pick in picks_lost:
            # Reset the index
            df = df.reset_index(drop=True)

            # Find row number of pick lost
            rowno_picklost = df.index[df.Display_Name_Detailed == pick][0]
            # print(rowno_picklost)

            # Find row number of the first pick in the next year
            rowno_startnextyear = df.index[(df.Year.astype(int) == int(
                v_current_year_plus1)) & (df.Overall_Pick.astype(int) == 1)][0]
            # print(rowno_startnextyear)

            # Insert pick to the row before next years draft:
            df = pd.concat([df.iloc[:rowno_startnextyear], df.iloc[[
                           rowno_picklost]], df.iloc[rowno_startnextyear:]]).reset_index(drop=True)

            # Find row number to delete and execute delete:
            rowno_delete = df.index[df.Display_Name_Detailed == pick][0]
            # print(rowno_delete)
            df.drop(rowno_delete, axis=0, inplace=True)

            # Changing the names of some key details:
            # Change system note to describe action
            df['System_Note'].mask(df['Display_Name_Detailed'] == pick,
                                   'FS bid match: pick lost to back of draft', inplace=True)

            # Change the draft round
            df['Draft_Round'].mask(
                df['Display_Name_Detailed'] == pick, 'BOD', inplace=True)
            df['Draft_Round_Int'].mask(
                df['Display_Name_Detailed'] == pick, 99, inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick, str(
                v_current_year) + '-Back of Draft', inplace=True)

            # Reset points value
            df['AFL_Points_Value'].mask(
                df['Display_Name_Detailed'] == pick, 0, inplace=True)

            # If needing to update pick moves before the inserts
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
            df['AFL_Points_Value'] = df['Overall_Pick'].map(
                library_AFL_Draft_Points).fillna(0)

            # Reset index Again
            df = df.reset_index(drop=True)

            # One line summary:
            print(pick + ' has been lost to the back of the draft.')

            # Update picks lost details df
            pick_lost_details_loop = pd.DataFrame({'Pick': pick,
                                                   'Moves_To': 'End of Draft',
                                                   'New_Points_Value': 0}, index=[0])
            pick_lost_details = pick_lost_details.append(
                pick_lost_details_loop)

    else:
        pick_lost_details = pd.DataFrame(
            columns=['Pick', 'Moves_To', 'New_Points_Value'])

    if len(picks_shuffled) > 0:
        pick_shuffled = picks_shuffled[0]

        # Find row number of pick shuffled
        rowno_pickshuffled = df.index[df.Display_Name_Detailed ==
                                      pick_shuffled][0]

        # Find the row number of where the pick should be inserted:
        rowno_pickshuffled_to = df[(df.Year.astype(int) == v_current_year)]['AFL_Points_Value'].astype(
            float).ge(picks_shuffled_points_value).idxmin()

        # Execute Shuffle
        # Insert pick to the row before next years draft:
        df = pd.concat([df.iloc[:rowno_pickshuffled_to], df.iloc[[
                       rowno_pickshuffled]], df.iloc[rowno_pickshuffled_to:]]).reset_index(drop=True)

        # Find row number to delete and execute delete:
        df.drop(rowno_pickshuffled, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(
            library_AFL_Draft_Points).fillna(0)

        # Reset index Again
        df = df.reset_index(drop=True)

        # Changing the names of some key details:
        # Change system note to describe action
        df['System_Note'].mask(df['Display_Name_Detailed'] == pick_shuffled,
                               'NGA bid match: pick shuffled backwards', inplace=True)

        # Change the draft round
        # Just take row above? if above and below equal each other, then value, if not take one above.
        # Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed ==
                                   pick_shuffled][0] - 1

        # Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

        # Make Changes
        df['Draft_Round_Int'].mask(
            df['Display_Name_Detailed'] == pick_shuffled, new_rd_no, inplace=True)
        df['Draft_Round'].mask(df['Display_Name_Detailed'] ==
                               pick_shuffled, 'RD' + str(int(new_rd_no)), inplace=True)
        df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick_shuffled, str(
            v_current_year) + '-RD' + new_rd_no + '-ShuffledBack', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(
            df['Display_Name_Detailed'] == pick_shuffled, picks_shuffled_points_value, inplace=True)

        # Summary:
        new_shuffled_pick_no = df.index[df.Display_Name_Detailed ==
                                        pick_shuffled][0] + 1
        print(pick_shuffled + ' will be shuffled back to pick ' +
              new_shuffled_pick_no.astype(str) + ' in RD' + str(int(new_rd_no)))

        # Summary Dataframe
        pick_shuffle_details = pd.DataFrame(
            {'Pick': pick_shuffled, 'Moves_To': 'RD' + str(int(new_rd_no)) + '-Pick' + new_shuffled_pick_no.astype(str), 'New_Points_Value': picks_shuffled_points_value}, index=[0])

    else:
        pick_shuffle_details = []

    if len(pick_deficit) > 0:
        deficit_subset = df.copy()
        deficit_subset = deficit_subset[(deficit_subset.Current_Owner.astype(int) == fs_teamm) & (
            deficit_subset.Year.astype(int) == v_current_year_plus1) & (deficit_subset.Draft_Round_Int >= fs_bid_round_int)]

        # Finding the first pick in the round to take the points off (and rowno)
        deficit_attached_pick = deficit_subset['Display_Name_Detailed'].iloc[0]
        deficit_pickshuffled_rowno = df.index[df.Display_Name_Detailed ==
                                              deficit_attached_pick][0]

        # finding the points value of that pick and then adjusting the deficit
        deficit_attached_pts = deficit_subset['AFL_Points_Value'].iloc[0]
        deficit_pick_points = deficit_attached_pts + fs_points_deficit

        # Find the row number of where the pick should be inserted:
        deficit_pickshuffled_to = df[(df.Year.astype(int) == int(
            v_current_year_plus1))]['AFL_Points_Value'].astype(float).ge(deficit_pick_points).idxmin()

        # Execute pick shuffle
        df = pd.concat([df.iloc[:deficit_pickshuffled_to], df.iloc[[
                       deficit_pickshuffled_rowno]], df.iloc[deficit_pickshuffled_to:]]).reset_index(drop=True)

        # Find row number to delete and execute delete:
        df.drop(deficit_pickshuffled_rowno, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(
            library_AFL_Draft_Points).fillna(0)

        # Reset index Again
        df = df.reset_index(drop=True)

        # Change system note to describe action
        df['System_Note'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'FS bid match: Points Deficit',
                               inplace=True)

        # Change the draft round
        # Just take row above? if above and below equal each other, then value, if not take one above.
        # Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed ==
                                   deficit_attached_pick][0] - 1

        # Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

        # Make Changes

        df['Draft_Round_Int'].mask(
            df['Display_Name_Detailed'] == deficit_attached_pick, new_rd_no, inplace=True)

        df['Draft_Round'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'RD' + new_rd_no.round(0).astype(str),
                               inplace=True)

        df['Pick_Group'].mask(df['Display_Name_Detailed'] == deficit_attached_pick,
                              str(v_current_year) + '-RD' + new_rd_no.round(0).astype(str) + '-FS_Deficit', inplace=True)

        # Reset points value

        df['AFL_Points_Value'].mask(
            df['Display_Name_Detailed'] == deficit_attached_pick, deficit_pick_points, inplace=True)

        # Summary:
        # getting the new overall pick number and what round it belongs to:

        deficit_new_shuffled_pick_no = df[df.Display_Name_Detailed ==
                                          deficit_attached_pick].Overall_Pick.iloc[0]

        deficit_new_shuffled_pick_RD_no = df[df.Display_Name_Detailed ==
                                             deficit_attached_pick].Draft_Round.iloc[0]

        # 2021-RD3-Pick43-Richmond
        pick_deficit_details = pd.DataFrame(
            {'Pick': deficit_attached_pick, 'Moves_To': deficit_new_shuffled_pick_no, 'New_Points_Value': deficit_pick_points}, index=[0])

        print(deficit_attached_pick + ' moves to pick ' +
              deficit_new_shuffled_pick_no.astype(str) + ' in ' + deficit_new_shuffled_pick_RD_no)

    else:
        pick_deficit_details = []

    # ////////////////////////  EXECUTE INSERT OF PICK TO THE SPOT OF THE BID ///////////////////////////////////

    # inserting pick above fs_bid

    # Make the changes to the masterlist:

    rowno = df.index[df['Display_Name_Detailed'] == fs_pick][0]
    # create the line to insert:

    line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == int(fs_teamm), 'Position'].iloc[0], 'Year': v_current_year,
                         'TeamName': fs_teamm, 'PickType': 'FS_BidMatch', 'Original_Owner': fs_teamm, 'Current_Owner': fs_teamm,
                         'Previous_Owner': fs_teamm, 'Draft_Round': fs_bid_round, 'Draft_Round_Int': fs_bid_round_int,
                         'Pick_Group': str(v_current_year) + '-' + fs_bid_round + '-FSBidMatch', 'Reason': 'FS Bid Match',
                         'Pick_Status': 'Used', 'Selected_Player': fs_player}, index=[rowno])

    # Execute Insert
    # i.e stacks 3 dataframes on top of each other
    df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                   ).reset_index(drop=True)
    # del df['Previous_Owner_id']
    df = df.iloc[rowno]
    df['id'] = rowno
    df['projectid_id'] = pk

    MasterList.objects.filter(id=rowno).update(**df)

    # /////////////////////////// Called Update masterlist //////////////////////////////////////

    df = dataframerequest(request, pk)
    updatedf = update_masterlist(df)
    iincreament_id = 1
    for index, updaterow in updatedf.iterrows():
        fs_dict = dict(updaterow)
        team = Teams.objects.get(id=updaterow.TeamName)
        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        Overall_pickk = fs_dict['Overall_Pick']

        Project1 = Project.objects.get(id=pk)
        fs_dict['Previous_Owner'] = previous_owner
        team = Teams.objects.get(id=updaterow.TeamName)
        fs_dict['TeamName'] = team
        fs_dict['Original_Owner'] = Original_Owner
        fs_dict['Current_Owner'] = Current_Ownerr
        fs_dict['projectid'] = Project1

        fs_dict['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        fs_dict['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(fs_dict['Display_Name'])
        fs_dict['Display_Name_Mini'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else team.ShortName + \
            ' ' + str(Overall_pickk)

        fs_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        fs_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        # MasterList(**row1).save()

        MasterList.objects.filter(id=iincreament_id).update(**fs_dict)

        iincreament_id += 1

    ######## Combine into a summary dataframe: #############

    fs_summaries_list = [pick_lost_details,
                         pick_shuffle_details, pick_deficit_details]
    fs_summary_df = pd.DataFrame(
        columns=['Pick', 'Moves_To', 'New_Points_Value'])
    for x in fs_summaries_list:
        if len(x) > 0:
            fs_summary_df = fs_summary_df.append(x)

    fs_summary_dict = fs_summary_df.to_dict(orient="list")

    ######### Exporting Transaction Details: ###############
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    fs_dict = {fs_teamm: [fs_pick_type, fs_bid, fs_bid_pick_no, fs_player]}

    # Create Simple description.
    fs_description = 'Father Son Bid Match: Pick ' + \
        str(fs_bid_pick_no) + ' ' + str(fs_teamname) + \
        ' (' + str(fs_player) + ')'

    proj_obj = Project.objects.get(id=pk)

    transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'FS_Bid_Match',
         'Transaction_Details': fs_dict,
         'Transaction_Description': fs_description,
         'projectId': proj_obj.id
         })

    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='FS_Bid_Match',
        Transaction_Details=fs_dict,
        Transaction_Description=fs_description,
        projectId=proj_obj.id

    )
    lastinsertedId = Transactions.objects.latest('id')
    Transactions.objects.filter(id=lastinsertedId.id).update(
        Transaction_Number=lastinsertedId.id)

    ########## EXPORT TRANSACTION OF DRAFT SELECTION ###########
    # Create Drafted Player dict

    drafted_player_dict = {fs_teamm: [fs_bid_round, fs_bid_pick_no, fs_player]}
    drafted_description = 'With pick ' + \
        str(fs_bid_pick_no) + ' ' + str(fs_teamname) + \
        ' have selected ' + str(fs_player)

    drafted_player_transaction_details = pd.DataFrame(
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Drafted_Player',
         'Transaction_Details': drafted_player_dict,
         'Transaction_Description': drafted_description})

    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Drafted_Player',
        Transaction_Details=drafted_player_dict,
        Transaction_Description=drafted_description,
        projectId=proj_obj.id

    )

    lastinsertedId = Transactions.objects.latest('id')
    Transactions.objects.filter(id=lastinsertedId.id).update(
        Transaction_Number=lastinsertedId.id)
    call_add_father_son(transaction_details)
    call_drafted_player(drafted_player_transaction_details)
    return Response("Success", status=status.HTTP_201_CREATED)

    #  //////////////////////////////////  GET Requests ///////////////////////////////////////////


# ///////////////////////// webpage dashbaord api //////////////////////////////////////////////

@ api_view(['GET'])
@ permission_classes([AllowAny])
def dashboard_request(request, pk):
    _dashboard = {}
    masterlist = dataframerequest(request, pk)
    players = playerdataframe(request, pk)
    trades = tradesdataframe(request, pk)

    transactions = transactionsdataframe(request, pk)
    current_day = date.today()
    proj_obj = Project.objects.get(id=pk)
    v_team_name = proj_obj.teamid
    v_current_year = current_day.year
    v_current_year_plus1 = v_current_year+1
    dict = {}
    # Current Year Picks to a List:
    _dashboard['data_current_year_club_picks_data'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year)) & (
        masterlist.Current_Owner.astype(int) == int(v_team_name))].Display_Name_Mini.to_list()
    # Next Year Picks to a List:
    _dashboard['data_next_year_club_picks'] = masterlist[(masterlist.Year.astype(int) == int(v_current_year_plus1)) & (
        masterlist.Current_Owner.astype(int) == int(v_team_name))].Display_Name_Mini.to_dict().values()

    # Dashboard Page masterlist:

    data_dashboard_masterlist = []
    Draft_Round_Int = []
    queryset = MasterList.objects.filter(
        Draft_Round_Int__in=['1', '2', '3', '4', '5']).values()
    for k in queryset:
        Draft_Round_Int = k['id']
    df_list = []
    obj = MasterList.objects.filter(
        Draft_Round_Int__in=['1', '2', '3', '4', '5']).values()
    for data in obj:
        df_list.append(data)
    masterlist2 = pd.DataFrame(df_list)
    data_dashboard_masterlist_data = masterlist2[[
        'Year', 'Overall_Pick', 'Display_Name_Short', 'AFL_Points_Value']]

    Display_Name_Short = data_dashboard_masterlist_data['Display_Name_Short'].astype(
        str).values.flatten().tolist()
    images_data = []
    for k in Display_Name_Short:
        query = Teams.objects.filter(ShortName=k).values('Image', 'ShortName')

        for data in query:
            team_dict = {}
            base_url = request.build_absolute_uri('/').strip("/")
            team_dict['image_with_path'] = base_url + \
                '/'+'media'+'/' + data['Image']
            team_dict['ShortName'] = data['ShortName']
            images_data.append(team_dict.copy())

    if masterlist['Draft_Round_Int'].all() <= 5:
        for key, value in data_dashboard_masterlist_data.iterrows():
            for img in images_data:
                if img['ShortName'] == value['Display_Name_Short']:
                    dict['Year'] = value['Year']
                    dict['Overall_Pick'] = value['Overall_Pick']
                    dict['Display_Name_Short'] = value['Display_Name_Short']
                    dict['AFL_Points_Value'] = value['AFL_Points_Value']
                    dict['Images'] = img['image_with_path']
                    data_dashboard_masterlist.append(dict.copy())
    unique_dict = [k for j, k in enumerate(
        data_dashboard_masterlist) if k not in data_dashboard_masterlist[j + 1:]]

    data_dashboard_draftboard = []
    data_dashboard_draftboard_data = players[['FirstName', 'LastName',
                                              'Position_1', 'Rank']].sort_values(by='Rank', ascending=True)
    for key, value in data_dashboard_draftboard_data.iterrows():
        dict['FirstName'] = value['FirstName']
        dict['LastName'] = value['LastName']
        dict['Position_1'] = value['Position_1']
        dict['Rank'] = value['Rank']
        data_dashboard_draftboard.append(dict.copy())

    data_dashboard_trade_offers_list = []
    data_dashboard_trade_offers_data = trades[[
        'Trade_Partner', 'Trading_Out', 'Trading_In', 'Points_Diff']]
    for key, values in data_dashboard_trade_offers_data.iterrows():
        dict = {}
        dict['Trade_Partner'] = values['Trade_Partner']
        dict['Trading_Out'] = values['Trading_Out']
        dict['Trading_In'] = values['Trading_In']
        dict['Points_Diff'] = values['Points_Diff']
        data_dashboard_trade_offers_list.append(dict.copy())
    # Dashboard Page Transactions
    transaction_list = []
    data_transaction_list = transactions[[
        'Transaction_Number', 'Transaction_Type', 'Transaction_Description']]
    for key, value in data_transaction_list.iterrows():
        dict = {}

        dict['Transaction_Number'] = value['Transaction_Number']
        dict['Transaction_Type'] = value['Transaction_Type']
        dict['Transaction_Description'] = value['Transaction_Description']
        transaction_list.append(dict.copy())

    next_team_to_pick1 = masterlist[(
        masterlist.Pick_Status != 'Used')]['Current_Owner'].iloc[0]

    Team_Obj = Teams.objects.get(id=next_team_to_pick1)
    _dashboard['next_team_to_pick'] = Team_Obj.TeamNames
    return Response({'data': _dashboard, 'transaction_list': transaction_list, 'data_dashboard_masterlist': unique_dict, 'data_dashboard_draftboard': data_dashboard_draftboard, 'data_dashboard_trade_offers': data_dashboard_trade_offers_list}, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def ProjectDetailsRequest(request, pk):
    project = Project.objects.filter(id=pk).values()
    masterlist = MasterList.objects.filter(projectid=pk).count()

    return Response({'ProjectDetails': project, 'MasterlistCount': masterlist}, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny, ])
def LogoutRequest(request):
    if request.session['userId']:
        # ///url = request.build_absolute_uri()
        request.session['userId'] = 0
        # / ////return HttpResponseRedirect(redirect_to='')
        res = "You have been logged out !"
        return Response(res, status=status.HTTP_403_FORBIDDEN)


@ api_view(['GET'])
@ permission_classes([AllowAny, ])
def GETProjectRequest(request):
    data_dict = Project.objects.filter().values()
    return Response(data_dict, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def CompanyListRequest(request):
    CompanyList = list()
    data_dict = Company.objects.filter().values()
    for data in data_dict:
        PorjectName = Project.objects.filter(
            id=data['projectId_id']).values('project_name')
        data['projectId_id'] = PorjectName[0].copy()
        CompanyList.append(data)
        print(data['projectId_id'])
    return Response(CompanyList, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def UserListRequest(request):
    data_dict = User.objects.filter().values()
    return Response(data_dict, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def TeamRequest(request):
    imgQuery = Teams.objects.all()
    serializer = ListImageSerializer(
        imgQuery, many=True, context={'request': request})

    return Response({
        'status': True,
        'data': serializer.data})


@ api_view(['GET'])
@ permission_classes([AllowAny])
def GetPlayer(request):
    data_dict = Players.objects.filter().values()
    return Response(data_dict, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def LadderRequest(request):
    LadderList = list()
    Ladder = LocalLadder.objects.filter().values()

    for ladderrr in Ladder:
        Team = Teams.objects.filter(
            id=ladderrr['teamname_id']).values('id', 'TeamNames')
        ladderrr['teamname_id'] = Team[0].copy()
        Project_name = Project.objects.filter(
            id=ladderrr['projectId_id']).values('id', 'project_name')
        ladderrr['projectId_id'] = Project_name[0].copy()
        LadderList.append(ladderrr)
    return Response({"data": LadderList, "TeamName": ladderrr['teamname_id']}, status=status.HTTP_200_OK)


@ api_view(['POST'])
@ permission_classes([AllowAny, ])
def GETMasterListRequest(request, pk):
    response = request.data
    offset = int(response['offset'])
    limit = 20
    Masterrecord = []
    data_dict = MasterList.objects.filter(projectid_id=pk).values()[
        offset:offset+limit]

    data_count = MasterList.objects.filter(projectid_id=pk).values().count()

    PagesCount = data_count/20

    Count = math.ceil(PagesCount)

    for masterlistdata in data_dict:
        TeamNamesList = Teams.objects.filter(
            id=masterlistdata['TeamName_id']).values('id', 'TeamNames', 'ShortName')
        ShortNames = Teams.objects.filter(
            id=masterlistdata['TeamName_id']).values('id', 'TeamNames')
        masterlistdata['TeamName_id'] = TeamNamesList[0].copy()
        masterlistdata['Original_Owner_id'] = ShortNames[0].copy()
        masterlistdata['Current_Owner_id'] = ShortNames[0].copy()

        ProjectQuery = Project.objects.filter(
            id=pk).values('id', 'project_name')

        masterlistdata['projectId_id'] = ProjectQuery[0].copy()
        Masterrecord.append(masterlistdata)

    return Response({'data': Masterrecord, 'PagesCount': Count}, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def ShowTeamRequest(request):
    data = Teams.objects.filter().values()
    print(data)
    return Response(data)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def TeamsRequest(request):
    imgobj = Teams.objects.all()

    serializer = ListImageSerializer(
        imgobj, many=True, context={'request': request})
    return Response({
        'status': True,
        'data': serializer.data})


@ api_view(['GET'])
@ permission_classes([AllowAny])
def CheckMasterlistrequest(request):
    MasterlisId = list()
    MasterList1dict = MasterList.objects.filter().values()
    for masterdata in MasterList1dict:
        MasterlisId.append(masterdata['projectId_id'])
    if len(MasterlisId) > 0:
        return Response('True')
    else:
        return Response('False')


@ api_view(['GET'])
@ permission_classes([AllowAny])
def GetTradeRequest(request, pk):

    Pick1List = []
    mydict = {}
    picksvalue = []
    team1Dict = Teams.objects.filter(id=pk).values('id', 'TeamNames')
    TeamName = team1Dict[0]['TeamNames']
    Teamid = team1Dict[0]['id']

    Pick1dict = MasterList.objects.filter(TeamName_id=Teamid).values(
        'id', 'Display_Name_Detailed').distinct()

    for pick1data in Pick1dict:
        Pick1List.append(pick1data)

    for data in Pick1List:
        mydict['value'] = data.pop('id')
        mydict['label'] = data.pop('Display_Name_Detailed')
        picksvalue.append(mydict.copy())

    return Response({'TeamList1': TeamName, 'PicksList': picksvalue}, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def Gettradev2Req(request, pk):
    trade = AddTradev2.objects.filter(id=pk).values()
    return Response({'TeamList1': trade}, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def GetFlagsRequest(request):

    imgQuery = Teams.objects.all()

    serializer = ListImageSerializer(
        imgQuery, many=True, context={'request': request})
    return Response({
        'status': True,
        'data': serializer.data})


# ##########################   Delete Api ##########################


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeleteMasterListRequest(request, pk):
    MasterList.objects.filter(projectId=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeleteLocalLadderRequest(self, pk):
    LocalLadder.objects.get(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeleteProjectRequest(request, pk):
    Project.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeleteLadderRecordRequest(request, pk):
    LocalLadder.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeleteTeamRequest(request, pk):
    Teams.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeleteCompanyRequest(request, pk):
    Company.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeleteAddTradeRequest(request, pk):
    AddTradev2.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)
