from array import array               
from ast import Add
from dataclasses import replace
from distutils.command.config import dump_file
from doctest import master
# from locale import D_FMT
# from locale import D_T_FMT
from logging import raiseExceptions
from re import M, T
# from socket import MSG_EOR
from tabnanny import verbose
from telnetlib import TELNET_PORT
from urllib import response
from django.http import Http404, HttpResponse
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from RestApi.settings import SECRET_KEY
from .serializers import (
    LocalLaddderSerializer,
    CreateProjectSerializer,
    MakeCompanySerializer,
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


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 500)

#########################################  POST Requests ###############################################################

unique_id = uuid.uuid4().hex[:6].upper()


class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def post(self, request):
        C_Name = Company.objects.filter().values('id', 'Name')
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        last_inserted_id = serializer.data['id']

        User.objects.filter(id=last_inserted_id).update(uui=unique_id)
        return Response({'success': 'User Created Successfuly'}, status=status.HTTP_201_CREATED)

def dataframerequest(request,pk):
    list = []
    df_re = MasterList.objects.filter(projectid=pk).values() 
    for df_val in df_re:
        list.append(df_val)
    df = pd.DataFrame(list)
    df.rename(columns = {'Current_Owner_id':'Current_Owner'}, inplace = True)
    return df

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
        
                user_details['token'] = token
    
                f = open('RestApp/userfile.py', 'w')
                testfile = File(f)
                testfile.write(str(user[0].id))
                testfile.close
                f.close
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
    print(TeamNames)
    NamesDict = {
        "Names": TeamNames
    }
    fk = serializer.data['projectId']
    ProjectId = Project.objects.filter(id=fk).values('id', 'project_name')
    print(ProjectId)
    return Response({'success': 'LocalLadder Created Successfuly', 'data': serializer.data, "NamesDict": NamesDict, 'Projectid': ProjectId}, status=status.HTTP_201_CREATED)


def import_ladder_dragdrop(library_team_dropdown_list, library_AFL_Team_Names, v_current_year, v_current_year_plus1):

    ladder_current_year = pd.DataFrame(
        library_team_dropdown_list, columns=['TeamName'])

    ladder_current_year['Position'] = np.arange(len(ladder_current_year)) + 1

    ladder_current_year['Year'] = v_current_year

    ladder_current_year = ladder_current_year[['TeamName', 'Year', 'Position']]

    ladder_current_year_plus1 = ladder_current_year.copy()
    print(library_team_dropdown_list)
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

    AddTradev2.objects.create(
        Team1=team1,
        Team1_Pick1=team1_pick1Id,
        Team1_Pick2=team1pick2Id,
        Team1_Pick3=team1_pick3Id,
        Team2=team2,
        Team2_Pick1=team2pick1Id,
        Team2_Pick2=team2pick2Id,
        Team2_Pick3=team2_pick3Id
    )

    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Trade',
        Transaction_Details=TradePicks,
        Transaction_Description=trade_description,
        projectId=pId,
        Type = 'Add-Trade-V2'

    )
    pk = Transactions.objects.latest('id')
    message_count = Transactions.objects.filter().count()
    Transactions.objects.filter(id=pk.id).update(
        Transaction_Number=message_count)

    return Response({'success': 'Trade and Trasactions Created'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny, ])
def add_trade_v2_request(request):

    # define lists of picks and players traded out:
    # team1 trading out
    team1_trades_picks = []
    team1_trades_players = []

    # team2 trading out:

    team2_trades_picks = []
    team2_trades_players = []
    team1picks = []
    team2picks = []
    team2currentowner = []
    picks_trading_out_team1 = []
    picks_trading_out_team2 = []
    # TEAM 1 TRADING OUT ######################## = []
    data = request.data
    Teamid1 = data['Team1']
    Teamid2 = data['Team2']
    picks_trading_out_team1_obj = data['Team1_Pick1']

    # picks_trading_out_team1 = picks_trading_out_team1_obj[0]['value']
    picks_trading_out_team1 = picks_trading_out_team1_obj

    # players_trading_out_team1_no = data['Team1_Players_no']
    players_trading_out_team1 = data['Team1_players'] or ''
    picks_trading_out_team2_obj = data['Team2_Pick2']
    # picks_trading_out_team2 = picks_trading_out_team2_obj[0]['value']
    picks_trading_out_team2 = picks_trading_out_team2_obj

    # players_trading_out_team2_no = data['Team2_Players_no']
    players_trading_out_team2 = data['Team2_players'] or ''


    teamobj = Teams.objects.filter(id=Teamid1).values('id', 'TeamNames')
    team1id = teamobj[0]['id']
    picks_trading_out_team1_len = len(str(picks_trading_out_team1))

    players_trading_out_team1_len = len(players_trading_out_team1) or ''

    if picks_trading_out_team1_len:

        team1picksobj = MasterList.objects.filter(Current_Owner=team1id).values(
            'id', 'Display_Name_Detailed', 'Current_Owner')
        team1currentowner = team1picksobj[0]['Current_Owner']
        for teamspicks in team1picksobj:
            team1picks.append(teamspicks['Display_Name_Detailed'])
        team1picks = set(team1picks)

        for i in range(picks_trading_out_team1_len):
            pick_trading_out_obj = MasterList.objects.filter(
                id=picks_trading_out_team1).values('Display_Name_Detailed')
            for pickslist1 in pick_trading_out_obj:
                team1_trades_picks.append(pickslist1['Display_Name_Detailed'])
    else:
        pass

    if players_trading_out_team1_len or players_trading_out_team1_len == '':
        for i in range(players_trading_out_team1_len or 0):
            # player_trading_out_team1 = Players.objects.filter(id__in = players_trading_out_team1).values('FirstName')

            team1_trades_players.append(players_trading_out_team2)
    else:
        pass

    team2obj = Teams.objects.filter(id=Teamid2).values('id', 'TeamNames')
    team2id = team2obj[0]['id']
    picks_trading_out_team2_len = len(str(picks_trading_out_team2))
    players_trading_out_team2_len = len(players_trading_out_team2) or ''

    if picks_trading_out_team2_len:
        team2picksobj = MasterList.objects.filter(id=picks_trading_out_team1).values(
            'id', 'Display_Name_Detailed', 'Current_Owner')
        team2currentowner = team2picksobj[0]['Current_Owner']
        for team2pickss in team2picksobj:
            team2_trades_picks.append(team2pickss['Display_Name_Detailed'])

    if players_trading_out_team2_len or players_trading_out_team2_len == '':

        for i in range(players_trading_out_team2_len or 0):

            team2_trades_players.append(players_trading_out_team2)
    else:
        pass

  # Trade facilitation - Swapping current owner names & Applying Most Recent Owner First:

    ##### Team 1 receiving from Team 2 #####
    # Loop for each pick that team 2 is trading out to team 1:

    for team2pickout in team2_trades_picks:
        if team2pickout is not None:
            MasterList.objects.filter(Display_Name_Detailed=team2pickout).update(
                Previous_Owner=team2currentowner)
            MasterList.objects.filter(
                Display_Name_Detailed=team2pickout).update(Current_Owner=team1id)

    for team1pickout in team1_trades_picks:
        if team1pickout is not None:
            MasterList.objects.filter(Display_Name_Detailed=team2pickout).update(
                Previous_Owner=team1currentowner)
            MasterList.objects.filter(
                Display_Name_Detailed=team2pickout).update(Current_Owner=team2id)

    team1_out = team1_trades_players + team1_trades_picks
    team2_out = team2_trades_players + team2_trades_picks

    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    trade_data = []
    trade_dict = {Teamid1: team1_out, Teamid2: team2_out}

    for key, values in trade_dict.items():
        for i in values:
            result = ' ' + key + ' - ' + i
            trade_data.append(result)
    trade_str = ''.join(str(e) for e in trade_data)
 
    trade_description = Teamid1 + ' traded ' + \
        ','.join(str(e) for e in team1_out) + ' & ' + Teamid2 + \
        ' traded ' + ','.join(str(e) for e in team2_out)
                
    projectIdd = MasterList.objects.filter(
        id__in=[Teamid1, Teamid2]).values('projectid')
    pId = projectIdd[0]['projectid']
    

    Team_id1 = Teams.objects.get(id=Teamid1)
    Team_id2 = Teams.objects.get(id=Teamid2)
    masterpick1 = MasterList.objects.get(id=picks_trading_out_team1)
    masterpick2 = MasterList.objects.get(
        id=picks_trading_out_team2)

    AddTradev2.objects.create(
        Team1=Team_id1,
        Team1_Pick1_no=masterpick1,
        Team1_player_no=picks_trading_out_team1,
        Team1_Player_Name=players_trading_out_team1,
        Team2=Team_id2,
        Team2_Pick1_no=masterpick2,
        Team2_Player_Name=players_trading_out_team2,
        Team2_player_no=picks_trading_out_team2,
        projectid=pId
    )

    Transactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Trade',
        Transaction_Details=trade_str,
        Transaction_Description=trade_description,
        projectId=pId,
        Type= 'Add-Trade-v2'
    )

    pk = Transactions.objects.latest('id')
    row_count = Transactions.objects.filter().count()
    Transactions.objects.filter(id=pk.id).update(Transaction_Number=row_count)

    return Response({'success': 'Trade and Trasactions Created'}, status=status.HTTP_201_CREATED)

def add_trade_v3_inputs(request,pk):

    team1_trades_picks = []
    team1_trades_players = []
    team2_trades_picks = []
    team2_trades_players =[]


    data = request.data
    team1 = data['teamid1']
    player1 = data['player1']
    team2 = data['teamid2']
    player2 = data['player2']
    pickid1 = data['pickid1']
    pickid2 = data['pickid2']

    df = dataframerequest(request,pk)
    masterlist = df
    picks_trading_out_team1 = pickid1
    players_trading_out_team1 = str(len(player1))

    #Getting the pick(s) name for the pick(s) traded out:
    if int(picks_trading_out_team1) > 0:
        #Priniting the available picks for team 1 to trade out
        for i in range(len(picks_trading_out_team1)):         
            pick_trading_out_team1_obj = MasterList.objects.filter(Current_Owner_id=team1).values()
            for pick_trading_out_team1 in pick_trading_out_team1_obj:
                team1_trades_picks.append(pick_trading_out_team1['Display_Name_Detailed'])
    else:
        pass 

    #Getting the pick(s) name for the pick(s) traded out:
    if int(players_trading_out_team1) > 0:
        #Priniting the available picks for team 1 to trade out
        for i in range(int(players_trading_out_team1)):            
            player_trading_out_team1_obj = Players.objects.filter(id=player1).values()
            for player_trading_out_team1 in player_trading_out_team1_obj:

                team1_trades_players.append(player_trading_out_team1['Full_Name'])
    else:
        pass         

    picks_trading_out_team2 = pickid2
    players_trading_out_team2 = str(len(player2))

    if int(picks_trading_out_team2) > 0:

    #Priniting the available picks for team 1 to trade out
        for i in range(len(picks_trading_out_team2)):         
            pick_trading_out_team2_obj = MasterList.objects.filter(Current_Owner=team2).values()
            for pick_trading_out_team1 in pick_trading_out_team2_obj:
                team2_trades_picks.append(pick_trading_out_team1['Display_Name_Detailed'])
    else:
        pass 

    #Getting the pick(s) name for the pick(s) traded out:
    if int(players_trading_out_team2) > 0:
        #Priniting the available picks for team 1 to trade out
        for i in range(int(players_trading_out_team2)):            
            player_trading_out_team1_obj = Players.objects.filter(id=player2).values()
            for player_trading_out_team2 in player_trading_out_team1_obj:
                team2_trades_players.append(player_trading_out_team2['Full_Name'])
    else:
        pass       
    return masterlist, team1, team2,team1_trades_picks,team1_trades_players, team2_trades_picks,team2_trades_players

@api_view(['POST'])
@permission_classes([AllowAny, ])
def add_trade_v3(request,pk):

    ################### TRADE EXECUTION ############################
        
    # Trade facilitation - Swapping current owner names & Applying Most Recent Owner First:
    
    ##### Team 1 receiving from Team 2 #####
    #Loop for each pick that team 2 is trading out to team 1:

    masterlist, team1, team2,team1_trades_picks,team1_trades_players, team2_trades_picks,team2_trades_players = add_trade_v3_inputs(request,pk)
    current_date = date.today()
    v_current_year = current_date.year
    for team2pickout in team2_trades_picks:
        #Changing the previous owner name
        masterlist.rename(columns = {'Previous_Owner_id':'Previous_Owner'}, inplace = True)
        masterlist.rename(columns = {'Current_Owner_id':'Current_Owner'}, inplace = True)
        masterlist['Previous_Owner'].mask(masterlist['Display_Name_Detailed'] == team2pickout, masterlist['Current_Owner'], inplace=True)
        #Executing change of ownership
        masterlist['Current_Owner'].mask(masterlist['Display_Name_Detailed'] == team2pickout, team1, inplace=True)

    ##### Team 2 receiving from Team 1 #####
    #Loop for each pick that team 1 is trading out to team 2:
    for team1pickout in team1_trades_picks:
        #Changing the previous owner name
        masterlist['Previous_Owner'].mask(masterlist['Display_Name_Detailed'] == team1pickout, masterlist['Current_Owner'], inplace=True)
        #print( masterlist['Previous_Owner'])
        #Executing change of ownership
        masterlist['Current_Owner'].mask(masterlist['Display_Name_Detailed'] == team1pickout, team2, inplace=True)    

    # ###########  Call Update masterlist ############
    udpatedf = update_masterlist(masterlist)

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

        # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
        #     previous_owner + team.ShortName + \
        #     ')' if Original_Owner != Current_Ownerr else team.ShortName
        # df.reset_index(drop=False)

        # print(row1['Display_Name_Mini'])
        # exit()
        trade_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        trade_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        MasterList(**trade_dict).save()   

    ################### RECORDING TRANSACTION ############################
    #Summarising what each team traded out:
    team1_out = team1_trades_players +  team1_trades_picks
    team2_out = team2_trades_players +  team2_trades_picks
    
    # variables for transactions dict
    current_time = datetime.datetime.now(pytz.timezone('Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    
    #Creating a dict of what each team traded out
    trade_dict = {team1: team1_out , team2: team2_out}
    trade_dict_full = {team1: [team1_trades_players,team1_trades_picks] , team2: [team2_trades_players,team2_trades_picks]}
    
    #Creating a written description
    trade_description = team1 + ' traded ' + ','.join(str(e) for e in team1_out) + ' & ' + team2 + ' traded ' + ','.join(str(e) for e in team2_out)

     # Exporting trade to the transactions df
    Proj_obj = Project.objects.get(id=pk)
    project_id = Proj_obj.id
    transaction_details = pd.DataFrame(
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Trade',
         'Transaction_Details': [trade_dict_full],
         'Transaction_Description': trade_description,
         'Type':'Add-Trade-V3',
         'projectId':project_id
         })
    transactions_obj = Transactions.objects.latest('id')
    last_Transations_id = transactions_obj.id
    Transactions.objects.filter(id=last_Transations_id).update(Transaction_Number=last_Transations_id)
    return Response({'success': 'Add-Trade-v3 Created Successfuly'}, status=status.HTTP_201_CREATED)


def update_masterlist(df):
    library_AFL_Draft_Pointss = []
    library_AFL_Team_Names = []

    Team = Teams.objects.filter().values('id', 'TeamNames', 'ShortName')
    for teamdata in Team:
        library_AFL_Team_Names.append(teamdata['id'])

    PointsQueryset = library_AFL_Draft_Points.objects.filter().values('points')

    for pointss in list(PointsQueryset):

        library_AFL_Draft_Pointss.append(pointss['points'])

    df.rename(columns = {'Current_Owner_id':'Current_Owner'}, inplace = True)
    df.rename(columns = {'Original_Owner_id':'Original_Owner'}, inplace = True)
    df.rename(columns = {'TeamName_id':'TeamName'}, inplace = True)
    df.rename(columns = {'Previous_Owner_id':'Previous_Owner'}, inplace = True)


    df['Overall_Pick'] = df.groupby('Year').cumcount() + 1

    ss = enumerate(library_AFL_Draft_Pointss)
    library_AFL_Draf = dict(ss)
    df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draf).fillna(0)

    df['Unique_Pick_ID'] = df['Year'].astype(str) + '-' + df['Draft_Round'].astype(
        str) + '-' + df['PickType'].astype(str) + '-' + df['Original_Owner'].astype(str)

    df['Club_Pick_Number'] = df.groupby(
        ['Year', 'Current_Owner']).cumcount() + 1
    df['Display_Name'] = df['Current_Owner']
    df['Display_Name_Detailed'] = df['Current_Owner']

    return df


def CreateMasterListRequest(request, pk):
    print('hello')
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
            df['Draft_Round_Int'] = (df.groupby(['Year', 'Current_Owner']).cumcount() + 1).astype(int)
     
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
                print(row1)
                team = Teams.objects.get(id=updaterow.TeamName)
                teamsobj = Teams.objects.filter().values('ShortName')
                for teams_short_list in teamsobj:
                    ShortNames.append(teams_short_list['ShortName'])


                Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
                Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
                previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
                Overall_pickk = row1['Overall_Pick']

                Project1 = Project.objects.get(id=updaterow.projectid)
                df['Previous_Owner'] = previous_owner
                team = Teams.objects.get(id=updaterow.TeamName)
                row1['TeamName'] = team
                row1['Original_Owner'] = Original_Owner
                row1['Current_Owner'] = Current_Ownerr
                row1['projectid'] = Project1
                # row1['Overall_Pick'] = *Overall_pickk

                row1['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
                    None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

                row1['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
                    updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(row1['Display_Name'])

                # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
                #     previous_owner + team.ShortName + \
                #     ')' if Original_Owner != Current_Ownerr else team.ShortName
                # df.reset_index(drop=False)

                # print(row1['Display_Name_Mini'])
                # exit()
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

# CreateMasterListRequest('MasterList/',4)

@api_view(['POST'])
@permission_classes([AllowAny, ])
def ProjNameDescRequest(request):
    Projectdata = request.data
    serializer = CreateProjectSerializer(data=Projectdata)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    pk = Project.objects.latest('id').id
    CreateMasterListRequest(request, pk)
    return Response({'success': 'Project Created Successfuly', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def PriorityPickrRequest(request):

    current_date = date.today()
    v_current_year = current_date.year

    pp_team = []
    pp_dict = {}
    arr = []
    pp_aligned_pick = []
    pp_description = []

    data = request.data
    Idd = data['teamid']
    reason = data['reason']
    
    p_type = data['pick_type']
    pp_id = data['ppid']

    pp_round = ''

    project_Id = data['projectId']

    pp_insert_instructions = data['pp_insert_instructions']

    MasterListobj = MasterList.objects.filter(id=Idd).values()

    pp_team_id = MasterListobj[0]['TeamName_id']

    for teamsid in MasterListobj:
        pp_team.append(teamsid['TeamName_id'])

    Pickobj = MasterList.objects.filter(id=pp_id).values()
    pp_aligned_pick = Pickobj[0]['Display_Name_Detailed']


    for picks in Pickobj:
        arr.append(picks)

    df = dataframerequest(request,project_Id)

    pp_pick_type_re = PicksType.objects.filter(
        pickType=p_type).values('id', 'pickType')

    pp_pick_type = pp_pick_type_re[0]['pickType']

    if pp_pick_type == 'Start of Draft':
        pp_dict = {}

        rowno = df.id[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD1-Standard')][0]
  

        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority',
                             'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id, 'Previous_Owner': '',
                             'Draft_Round': 'RD1',
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + pp_pick_type, 'Reason': reason}, index=[rowno])

  
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']
        df = df.iloc[1]

        df['id'] = rowno+1
        df['Original_Owner_id'] = Idd
        df['Current_Owner_id'] = Idd
        df['TeamName_id'] = Idd
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = project_Id
        pp_dict['pp_team'] = [pp_pick_type]
        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'

        pp_dict['pp_team'] = [pp_pick_type]
        pp_dict['pp_team'] = [pp_pick_type, reason]
        pp_description = str(pp_team) + 'received a ' + \
            str(pp_pick_type) + ' Priority Pick'

        MasterList.objects.filter(id=rowno+1).update(**df)


    if pp_pick_type == 'First Round':
        
        rowno = ''
  
        pick_list = df.id[df['Display_Name_Detailed'] == pp_aligned_pick]
        for num in pick_list:
   
            if num == int(pp_id):
                
                rowno = num

        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName_id': pp_team_id, 'PickType': 'Priority', 'Original_Owner_id': pp_team_id, 'Current_Owner_id': pp_team_id,
                             'Previous_Owner': '', 'Draft_Round': pp_round,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + pp_pick_type},
                            index=[rowno])

        if pp_insert_instructions == 'Before':

            df = pd.concat([df.loc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)

            df = df.iloc[rowno+1]


            df['id'] = rowno
            df['Original_Owner_id'] = Idd
            df['Current_Owner_id'] = Idd
            df['TeamName_id'] = Idd
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = project_Id

            MasterList.objects.filter(id=rowno).update(**df)

        else:

            df = pd.concat([df.loc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = project_Id
            del df['Previous_Owner']
       
            MasterList.objects.filter(id=rowno+1).update(**df)

    if pp_pick_type == 'End of First Round':
        pp_dict = {}
        arr = []
        df.reset_index(drop=True, inplace=True)
        rowno = df.id[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD1-Standard')].iloc[-1]


        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': int(pp_team_id), 'PickType': 'Priority',
                             'Original_Owner': int(pp_team_id), 'Current_Owner': int(pp_team_id), 'Previous_Owner': '',
                             'Draft_Round': 'RD1',
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + pp_pick_type}, index=[rowno])

        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno+1]

        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']

        df['id'] = rowno
        df['Original_Owner_id'] = Idd
        df['Current_Owner_id'] = Idd
        df['TeamName_id'] = Idd
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = project_Id

        MasterList.objects.filter(id=rowno).update(**df)

        pp_dict['pp_team'] = [pp_pick_type]
        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'


    if pp_pick_type == 'Start of Second Round':
        pp_dict = {}
        arr = []

        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD2-Standard')][0]


        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority',
                             'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id, 'Previous_Owner': '',
                             'Draft_Round': 'RD2',
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type}, index=[rowno])
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        df = df.iloc[1]

        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']

        df['id'] = rowno+1
        df['Original_Owner_id'] = Idd
        df['Current_Owner_id'] = Idd
        df['TeamName_id'] = Idd
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = project_Id
        pp_dict['pp_team'] = [pp_pick_type]
        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'

        MasterList.objects.filter(id=rowno).update(**df)

    if pp_pick_type == 'Second Round':

        rowno = ''
        pick_list = df.id[df['Display_Name_Detailed'] == pp_aligned_pick]
        for num in pick_list:
 
            if num == int(pp_id):
                rowno = num


        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority', 'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id,
                             'Previous_Owner': '', 'Draft_Round': pp_round,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type},
                            index=[rowno])

        if pp_insert_instructions == 'Before':
            pp_dic = {}
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
   
            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno
            df['Original_Owner_id'] = Idd
            df['Current_Owner_id'] = Idd
            df['TeamName_id'] = Idd
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = project_Id


            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno]
            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno+1
            df['Original_Owner_id'] = Idd
            df['Current_Owner_id'] = Idd
            df['TeamName_id'] = Idd
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = project_Id
        

            MasterList.objects.filter(id=rowno+1).update(**df)
            pp_dict['pp_team'] = [pp_pick_type, pp_round,
                                  pp_aligned_pick, pp_insert_instructions]
            pp_description = str(pp_team) + ' received a ' + \
                str(pp_pick_type) + ' Priority Pick'

    if pp_pick_type == 'End of Second Round':

        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD2-Standard')][-1]

        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority',
                             'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id, 'Previous_Owner': '',
                             'Draft_Round': 'RD2',
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type}, index=[rowno])

        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno+1]

        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']

        df['id'] = rowno+1
        df['Original_Owner_id'] = Idd
        df['Current_Owner_id'] = Idd
        df['TeamName_id'] = Idd
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = project_Id

        MasterList.objects.filter(id=rowno).update(**df)

        pp_dict['pp_team'] = [pp_pick_type]

        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'

    if pp_pick_type == 'Third Round':
        rowno = ''

        pp_id_df = df.id[df['Display_Name_Detailed'] == pp_aligned_pick]
 
        for num in pp_id_df:
            if num == int(pp_id):
                rowno = num
 

        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority', 'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id,
                             'Previous_Owner': '', 'Draft_Round': pp_round,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type},
                            index=[rowno])
        if pp_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]

            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno
            df['Original_Owner_id'] = Idd
            df['Current_Owner_id'] = Idd
            df['TeamName_id'] = Idd
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = project_Id
            pp_dict['pp_team'] = [pp_pick_type, pp_round,
                                  pp_aligned_pick, pp_insert_instructions]
            pp_description = str(pp_team) + ' received a ' + \
                str(pp_pick_type) + ' Priority Pick'


            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno]
            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno+1
            df['Original_Owner_id'] = Idd
            df['Current_Owner_id'] = Idd
            df['TeamName_id'] = Idd
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = project_Id

            MasterList.objects.filter(id=rowno+1).update(**df)
            pp_dict['pp_team'] = [pp_pick_type, pp_round,
                                  pp_aligned_pick, pp_insert_instructions]
            pp_description = str(pp_team) + ' received a ' + \
                str(pp_pick_type) + ' Priority Pick'

    if pp_pick_type == 'Custom Fixed Position':
    

        rowno = df.id[df['Display_Name_Detailed'] == pp_aligned_pick].iloc[0]
        
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority', 'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id,
                             'Previous_Owner': '', 'Draft_Round': 'RD3',
                             'Pick_Group': str(v_current_year) + '-' + pp_round + '-Priority-' + pp_pick_type},
                            index=[rowno])

        if pp_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]).reset_index(drop=True)

            df = df.iloc[rowno]
 

            del df['TeamName_id']
            del df['Current_Owner_id']
            del df['Previous_Owner_id']
            del df['Original_Owner_id']

            df['id'] = rowno
            df['Original_Owner'] = Idd
            df['Current_Owner'] = Idd
            df['Previous_Owner'] = Idd
            df['TeamName'] = Idd
            df['projectid_id'] = project_Id
          
            MasterList.objects.filter(id=rowno).update(**df)
        else:
            df = pd.concat([df.iloc[:rowno + 1], line, df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]

            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno+1
            df['Original_Owner_id'] = Idd
            df['Previous_Owner_id'] = Idd 
            df['Current_Owner_id'] = Idd
            df['TeamName_id'] = Idd
            df['projectid_id'] = project_Id

            MasterList.objects.filter(id=rowno+1).update(**df)

    pp_dict = {}

    new_df = []
    Queryset = MasterList.objects.filter(projectid_id=project_Id).values()
    for picks in Queryset:
        new_df.append(picks)

    df1 = pd.DataFrame(new_df)
    df1.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    df1.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    df1.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)
    
    Original_Owner = Teams.objects.get(id=Idd)
    Current_Ownerr = Teams.objects.get(id=Idd)
    previous_owner = Teams.objects.get(id=Idd)
    team = Teams.objects.get(id=Idd)

    
    udpatedf = update_masterlist(df1)
    udpatedf = udpatedf.drop('id', 1)
    udpatedf = udpatedf.drop('projectid_id', 1)
    udpatedf = udpatedf.drop('Previous_Owner_id', 1)

    iincreament_id =1
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

        # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
        #     previous_owner + team.ShortName + \
        #     ')' if Original_Owner != Current_Ownerr else team.ShortName
        # df.reset_index(drop=False)

        # print(row1['Display_Name_Mini'])
        # exit()
        academy_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        academy_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        # MasterList(**row1).save()   
        model_dictionary = {
            'Year':academy_dict['Year'],
            'PickType':academy_dict['PickType'],
            'TeamName':academy_dict['TeamName'],
            'Position':academy_dict['Position'],
            'Original_Owner':academy_dict['Original_Owner'],
            'Current_Owner':academy_dict['Current_Owner'],
            'Previous_Owner':academy_dict['Previous_Owner'],
            'Draft_Round':academy_dict['Draft_Round'],
            'Draft_Round_Int':academy_dict['Draft_Round_Int'],
            'Pick_Group':academy_dict['Pick_Group'],
            'System_Note':academy_dict['System_Note'],
            'User_Note':academy_dict['User_Note'],
            'Reason':academy_dict['Reason'],
            'Overall_Pick':academy_dict['Overall_Pick'],
            'AFL_Points_Value':academy_dict['AFL_Points_Value'],
            'Unique_Pick_ID':academy_dict['Unique_Pick_ID'],
            'Club_Pick_Number':academy_dict['Club_Pick_Number'],
            'Display_Name':academy_dict['Display_Name'],
            'Display_Name_Short':academy_dict['Display_Name_Short'],
            'Display_Name_Detailed':academy_dict['Display_Name_Detailed'],
            'Display_Name_Mini':academy_dict['Display_Name_Mini'],
            'Current_Owner_Short_Name':academy_dict['Current_Owner_Short_Name'],
            'Pick_Status':academy_dict['Pick_Status'],
            'Selected_Player':academy_dict['Selected_Player'],
            'projectid':academy_dict['projectid']
        }
    
        
        MasterList.objects.filter(id=iincreament_id).update(**model_dictionary)
        
        iincreament_id +=1
          
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    pp_dict['pp_team'] = [pp_round, pp_aligned_pick, pp_insert_instructions]

    PriorityTransactions.objects.create(
        Transaction_Number='',
        Transaction_DateTime=current_time,
        Transaction_Type='Priority_Pick',
        # Transaction_Details=[pp_dict],
        Transaction_Description=pp_description,
        projectId=project_Id

    )
    pk = PriorityTransactions.objects.latest('id')
    row_count = PriorityTransactions.objects.filter().count()
    PriorityTransactions.objects.filter(
        id=pk.id).update(Transaction_Number=row_count)
    PriorityPick.objects.create(
        Team=team,
        reason=reason,
        pp_insert_instructions=pp_insert_instructions,
        round=pp_round,
        projectid=project_Id
    )

    return Response({'success': 'Priority Pick Created Successfuly'}, status=status.HTTP_201_CREATED)




@api_view(['POST'])
@permission_classes([AllowAny])
def AcademyBidRequest(request, pk):
    projectid = pk
    current_date = date.today()
    v_current_year = current_date.year
    v_current_year_plus1 = v_current_year+1
    masterlist = []
    dfobj = MasterList.objects.filter(projectid=projectid).values()
    for df_data in dfobj:
        masterlist.append(df_data)
    df = pd.DataFrame(masterlist)

    transactions = []
    
    transactionsqueryset = Transactions.objects.filter().values()
    for tran_deta in transactionsqueryset:
        transactions.append(tran_deta)
    
    df2  = pd.DataFrame(transactions)
    
    df_original = df.copy()
    df2_original = df2.copy()   
    
    df.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    df.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    df.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)

    data = request.data
    
    academy_player = data['player']

    teamid = data['team']

    teamQurerySet = Teams.objects.filter(id=teamid).values('id','TeamNames')

    academy_team = teamQurerySet[0]['TeamNames']
    academy_team_id = teamQurerySet[0]['id']

    academy_pick_type = 'Academy Bid Match'
    
    pick_id = data['pickid']
    
    PickQueryset = MasterList.objects.filter(id=pick_id).values('Display_Name_Detailed')
    
    academy_bid = PickQueryset[0]['Display_Name_Detailed']
    
    academy_pts_value = df.loc[df.Display_Name_Detailed == academy_bid, 'AFL_Points_Value'].iloc[0]
    academy_bid_round = df.loc[df.Display_Name_Detailed == academy_bid, 'Draft_Round'].iloc[0]
    academy_bid_round_int = df.loc[df.Display_Name_Detailed == academy_bid, 'Draft_Round_Int'].iloc[0]
    academy_bid_team = df.loc[df.Display_Name_Detailed ==
                              academy_bid, 'Current_Owner'].iloc[0]
    academy_bid_pick_no = df.loc[df.Display_Name_Detailed ==
                                 academy_bid, 'Overall_Pick'].iloc[0]

    sum_line1 = str(academy_bid_team) + ' have placed a bid on a ' + str(academy_team) + \
        ' academy player at pick ' + str(academy_bid_pick_no) + ' in ' + str(academy_bid_round)


    # Defining discounts based off what round the bid came in:
    
    if academy_bid_round == 'RD1':
        academy_pts_required = int(academy_pts_value) * .8
        sum_line2 = academy_team +' will require ' + str(academy_pts_required) + ' draft points to match bid.'
    else:
        academy_pts_required = int(academy_pts_value) -197
        sum_line2 = academy_team +' will require ' + str(academy_pts_required) + ' draft points to match bid.'
    
    # Creating a copy df of that teams available picks to match bid
    df_subset = df.copy()

    df_subset = df_subset[(df_subset.Current_Owner == academy_team_id) & (df_subset.Year.astype(int) == v_current_year) & (df_subset.Overall_Pick >= academy_bid_pick_no)]

    
    # Creating the cumulative calculations to determine how the points are repaid:

    
    df_subset['Cumulative_Pts'] = df_subset.groupby('Current_Owner')['AFL_Points_Value'].transform(pd.Series.cumsum)
    
        
    df_subset['Payoff_Diff'] = df_subset['Cumulative_Pts'].astype(float) - academy_pts_required

    df_subset['AFL_Pts_Left'] = np.where(
    df_subset['Payoff_Diff'] <= 0,
                                0,
            np.where(
                    df_subset['Payoff_Diff'].astype(float) < df_subset['AFL_Points_Value'].astype(float),
                    df_subset['Payoff_Diff'],
                    df_subset['AFL_Points_Value']
                )
            )
    
    #creating previous pick rows to compare whether the picks have to be used or not:
    df_subset['AFL_Pts_Left_previous_pick'] = df_subset['AFL_Pts_Left'].shift()

    df_subset['AFL_Pts_Value_previous_pick'] = df_subset['AFL_Points_Value'].shift()
    
    df_subset['Action'] =  np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left']== 0),
                    'Pick lost to back of draft',
                    np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'].astype(int)>0),
                    'Pick Shuffled Backwards',
                    np.where((df_subset['AFL_Pts_Left'] == df_subset['AFL_Points_Value']) & (df_subset['Payoff_Diff'] < 0) & (df_subset['AFL_Pts_Value_previous_pick'].astype(float) > 0)
                    ,'Points Deficit',
                    'No Change')))
    
    df_subset['Deficit_Amount'] = np.where(df_subset['Action'] == 'Points Deficit', df_subset['Payoff_Diff'],np.nan)
        #defining the deficit amount
    try:
        academy_points_deficit = df_subset.loc[df_subset.Action == 'Points Deficit', 'Deficit_Amount'].iloc[0]

    except:
        academy_points_deficit = []


        
      #Create lists of changes to make:

    picks_lost = df_subset.loc[df_subset.Action == 'Pick lost to back of draft', 'Display_Name_Detailed'].to_list()
    picks_shuffled = df_subset.loc[df_subset.Action == 'Pick Shuffled Backwards', 'Display_Name_Detailed'].to_list()

    pick_deficit = df_subset.loc[df_subset.Action == 'Points Deficit', 'Display_Name_Detailed']

    try:
        picks_shuffled_points_value = df_subset.loc[df_subset.Action == 'Pick Shuffled Backwards', 'AFL_Pts_Left'].iloc[0]
    except:
        picks_shuffled_points_value = np.nan
    carry_over_deficit = academy_points_deficit
    
    
    #Executing The Academy Bid:
    # 3 Steps: Picks moving to back of draft, Pick getting shuffled backwards, and then if a pick has carryover deficit.

     # Step 1: Moving all picks to the back of the draft:
        

    if len(picks_lost) > 0  :
            pick_lost_details = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])

            for pick in picks_lost:
                # Reset the index
                df = df.reset_index(drop=True)
                #Find row number of pick lost
                rowno_picklost = df.index[df.Display_Name_Detailed == pick][0]
                #print(rowno_picklost)
                
                #Find row number of the first pick in the next year
         
                rowno_start = df.index[((df.Year.astype(int)+1)[0] == v_current_year_plus1) & (df.Overall_Pick.astype(int)== 1)]
                #Insert pick to the row before next years draft:
                rowno_startnextyear = rowno_start[1]
                
                df = pd.concat([df.iloc[:rowno_startnextyear], df.iloc[[rowno_picklost]], df.iloc[rowno_startnextyear:]]).reset_index(drop=True)
                #Find row number to delete and execute delete:
                rowno_delete = df.index[df.Display_Name_Detailed == pick][0]
                #print(rowno_delete)
                df.drop(rowno_delete, axis=0, inplace=True)

                #Changing the names of some key details:
                #Change system note to describe action

                df['System_Note'].mask(df['Display_Name_Detailed'] == pick, 'Academy bid match: pick lost to back of draft', inplace=True)

                #Change the draft round
                df['Draft_Round'].mask(df['Display_Name_Detailed'] == pick, 'BOD', inplace=True)
                df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == pick, 99, inplace=True)
                df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick, str(v_current_year) + '-Back of Draft', inplace=True)

                #Reset points value
                df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == pick, 0, inplace=True)

                # If needing to update pick moves before the inserts
                df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
                df['AFL_Points_Value'] = df['Overall_Pick'].map(df['AFL_Points_Value']).fillna(0)

                #Reset index Again
                df = df.reset_index(drop=True)
                
                #One line summary:
                # print(pick + ' has been lost to the back of the draft.')
                
                #Update picks lost details df
                pick_lost_details_loop = pd.DataFrame({'Pick': pick,
                    'Moves_To': 'End of Draft',
                    'New_Points_Value': 0},index=[0])
                pick_lost_details = pick_lost_details.append(pick_lost_details_loop)

    else:
        pick_lost_details = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])

    if len(picks_shuffled) > 0:
        pick_shuffled = picks_shuffled[0]

        # Find row number of pick shuffled
        rowno_pickshuffled = df.index[df.Display_Name_Detailed == pick_shuffled][0]
        # Find the row number of where the pick should be inserted:
        rowno_pickshuffled_to = df[(df.Year.astype(int) == v_current_year)]['AFL_Points_Value'].astype(float).ge(picks_shuffled_points_value).idxmin()



        #Execute Shuffle
        # Insert pick to the row before next years draft:
        df = pd.concat([df.iloc[:rowno_pickshuffled_to], df.iloc[[rowno_pickshuffled]], df.iloc[rowno_pickshuffled_to:]]).reset_index(drop=True)

        # Find row number to delete and execute delete:
        df.drop(rowno_pickshuffled, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(df['AFL_Points_Value']).fillna(0)

        # Reset index Again
        df = df.reset_index(drop=True)

        # Changing the names of some key details:
        # Change system note to describe action
        df['System_Note'].mask(df['Display_Name_Detailed'] == pick_shuffled, 'Academy bid match: pick shuffled backwards', inplace=True)

        # Change the draft round
        #Just take row above? if above and below equal each other, then value, if not take one above.
        #Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed == pick_shuffled][0] - 1

        #Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

        #Make Changes
        # df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == pick_shuffled, new_rd_no,inplace=True)
        df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == pick_shuffled, str(new_rd_no), inplace=True)
        
        df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick_shuffled, str(v_current_year) + '-RD'+ str(new_rd_no) + '-ShuffledBack', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == pick_shuffled, picks_shuffled_points_value, inplace=True)


        #Summary:
        new_shuffled_pick_no = df.index[df.Display_Name_Detailed == pick_shuffled][0] + 1
        # print(pick_shuffled + ' will be shuffled back to pick ' + new_shuffled_pick_no.astype(str) + ' in RD' + str(new_rd_no))

        #Summary Dataframe
        pick_shuffle_details = pd.DataFrame(
            {'Pick': pick_shuffled, 'Moves_To':  str(new_rd_no) + '-Pick' + new_shuffled_pick_no.astype(str), 'New_Points_Value': picks_shuffled_points_value},index=[0])

    else:
        pick_shuffle_details = []   
        
        # Step 3: Applying the deficit to next year:
        
    if len(pick_deficit) > 0:
        deficit_subset = df.copy()
        deficit_subset = deficit_subset[(deficit_subset.Current_Owner == academy_team_id) & (deficit_subset.Year.astype(int) == v_current_year_plus1) & (deficit_subset.Draft_Round >= academy_bid_round_int)]

        #Finding the first pick in the round to take the points off (and rowno)

        deficit_attached_pick = deficit_subset['Display_Name_Detailed'].iloc[0]
        deficit_pickshuffled_rowno = df.index[df.Display_Name_Detailed == deficit_attached_pick][0]


        #finding the points value of that pick and then adjusting the deficit
        deficit_attached_pts = deficit_subset['AFL_Points_Value'].iloc[0]
        
        
        deficit_pick_points =   float(deficit_attached_pts) + academy_points_deficit

        # Find the row number of where the pick should be inserted:
        deficit_pickshuffled_to = df[(df.Year.astype(int) == v_current_year_plus1)]['AFL_Points_Value'].astype(float).ge(deficit_pick_points).idxmin()

        #Execute pick shuffle
        df = pd.concat([df.iloc[:deficit_pickshuffled_to], df.iloc[[deficit_pickshuffled_rowno]], df.iloc[deficit_pickshuffled_to:]]).reset_index(drop=True)

        # Find row number to delete and execute delete:
        df.drop(deficit_pickshuffled_rowno, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draft_Points).fillna(0)
        # Reset index Again
        df = df.reset_index(drop=True)

        # Change system note to describe action   
        df['System_Note'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'Academy bid match: Points Deficit',
                               inplace=True)

        # Change the draft round
        # Just take row above? if above and below equal each other, then value, if not take one above.
        # Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed == deficit_attached_pick][0] - 1

        # Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int
     

        # Make Changes
        df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, new_rd_no, inplace=True)
        df['Draft_Round'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'RD' + str(new_rd_no),
                               inplace=True)
        df['Pick_Group'].mask(df['Display_Name_Detailed'] == deficit_attached_pick,
                              str(v_current_year) + '-RD' + str(new_rd_no) + '-AcademyDeficit', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, deficit_pick_points , inplace=True)

        # Summary: 
        #getting the new overall pick number and what round it belongs to:
        deficit_new_shuffled_pick_no = df[df.Display_Name_Detailed == deficit_attached_pick].Overall_Pick.iloc[0]
        deficit_new_shuffled_pick_RD_no = df[df.Display_Name_Detailed == deficit_attached_pick].Draft_Round.iloc[0]

        #2021-RD3-Pick43-Richmond
        pick_deficit_details = pd.DataFrame(
            {'Pick': deficit_attached_pick, 'Moves_To': deficit_new_shuffled_pick_no, 'New_Points_Value': deficit_pick_points},index=[0])

        # print(deficit_attached_pick + ' moves to pick ' + deficit_new_shuffled_pick_no.astype(str) + ' in ' + deficit_new_shuffled_pick_RD_no)

    else:
        pick_deficit_details = []

    ########## EXECUTE INSERT OF PICK TO THE SPOT OF THE BID ##############
    #inserting pick above academy_bid

    # Make the changes to the masterlist:
    rowno = df.index[df['Display_Name_Detailed'] == academy_bid][0]
    # create the line to insert:
 
    line = pd.DataFrame({'Position': df.loc[df.TeamName.astype(int) == academy_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                         'TeamName': academy_team_id, 'PickType': 'AcademyBidMatch', 'Original_Owner': academy_team_id, 'Current_Owner': academy_team_id,
                         'Previous_Owner': '', 'Draft_Round': academy_bid_round, 'Draft_Round_Int': academy_bid_round_int,
                         'Pick_Group': str(v_current_year) + '-' + academy_bid_round + '-AcademyBidMatch','Reason': 'Academy Bid Match',
                         'Pick_Status':'Used','Selected_Player': academy_player}, index=[rowno])
    
    # Execute Insert
    #i.e stacks 3 dataframes on top of each other
    df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]).reset_index(drop=True)
    
    # MasterList.objects.filter(projectid_id=pk).delete()

    udpatedf = update_masterlist(df)


    # udpatedf = udpatedf.drop('id', 1)
    udpatedf['id'] = udpatedf['id'].fillna(0) 
    udpatedf['id'] = udpatedf['id'].astype(int)
    udpatedf = udpatedf.drop('projectid_id', 1)
    udpatedf = udpatedf.drop('Previous_Owner_id', 1)

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
        team = Teams.objects.get(id=updaterow.TeamName)
        row1['TeamName'] = team
        row1['Original_Owner'] = Original_Owner
        row1['Current_Owner'] = Current_Ownerr
        row1['projectid'] = Project1

        row1['Display_Name'] = str(Current_Ownerr)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner != Current_Ownerr else Current_Ownerr.TeamNames

        row1['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(row1['Display_Name'])

        # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
        #     previous_owner + team.ShortName + \
        #     ')' if Original_Owner != Current_Ownerr else team.ShortName
        # df.reset_index(drop=False)

        # print(row1['Display_Name_Mini'])
        # exit()
        row1['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        row1['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName  
        
        model_dictionary = {
            'Year':row1['Year'],
            'PickType':row1['PickType'],
            'TeamName':row1['TeamName'],
            'Position':row1['Position'],
            'Original_Owner':row1['Original_Owner'],
            'Current_Owner':row1['Current_Owner'],
            'Previous_Owner':row1['Previous_Owner'],
            'Draft_Round':row1['Draft_Round'],
            'Draft_Round_Int':row1['Draft_Round_Int'],
            'Pick_Group':row1['Pick_Group'],
            'System_Note':row1['System_Note'],
            'User_Note':row1['User_Note'],
            'Reason':row1['Reason'],
            'Overall_Pick':row1['Overall_Pick'],
            'AFL_Points_Value':row1['AFL_Points_Value'],
            'Unique_Pick_ID':row1['Unique_Pick_ID'],
            'Club_Pick_Number':row1['Club_Pick_Number'],
            'Display_Name':row1['Display_Name'],
            'Display_Name_Short':row1['Display_Name_Short'],
            'Display_Name_Detailed':row1['Display_Name_Detailed'],
            'Display_Name_Mini':row1['Display_Name_Mini'],
            'Current_Owner_Short_Name':row1['Current_Owner_Short_Name'],
            'Pick_Status':row1['Pick_Status'],
            'Selected_Player':row1['Selected_Player'],
            'projectid':row1['projectid']
        }
    
        
        MasterList.objects.filter(id=iincreament_id).update(**model_dictionary)
        
        iincreament_id +=1
           
    
     ######## Combine into a summary dataframe: #############
        
        academy_summaries_list = [pick_lost_details,pick_shuffle_details,pick_deficit_details]
        

        academy_summary_df = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])

    for x in academy_summaries_list:
        if len(x) > 0:
            academy_summary_df = academy_summary_df.append(x)

    academysummery_list = []
    academy_summary_dict = academy_summary_df.to_dict(orient="list")
    
    for key , value in academy_summary_dict.items():
        for i in value:
            
            result = ' ' + key + ' - ' + str(i)
            academysummery_list.append(result)
    academy_summary_str = ''.join(str(e) for e in academy_summaries_list)

    ######### Exporting Transaction Details: ###############
    
    current_time = datetime.datetime.now(pytz.timezone('Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    academy_dict = {academy_team: [academy_pick_type, academy_bid, academy_bid_pick_no, academy_player]}
    academy_data = []
    for key, values in academy_dict.items():
        for i in values:
            result = ' ' + key + ' - ' + i
            academy_data.append(result)
    academy_str = ''.join(str(e) for e in academy_data)


    instance_obj = Project.objects.get(id=pk)

    transaction_details = (
    {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Academy_Bid_Match',
        'Transaction_Details': academy_str,
        'Transaction_Description': academy_summary_str,
        'Type':'AcademyBid',
        'projectId':instance_obj.id
        })

    Transactions(**transaction_details).save()
    obj = Transactions.objects.latest('id')
    count = Transactions.objects.filter().count()
    Transactions.objects.filter(id = obj.id ).update(Transaction_Number=count)
    return Response({'success': 'Academy Bid has Created'}, status=status.HTTP_201_CREATED)    
    
    
    
def academy_bid_inputs(request,pk):

    masterlist = dataframerequest(request,pk)
    data = request.data
    academy_player = data['player']
    academy_team = data['team']
    academy_bid = data['pickid']
    return masterlist,academy_player, academy_team, academy_bid
    
    
@api_view(['POST'])
@permission_classes([AllowAny])
def academy_bid_v2(request,pk):
    current_time = date.today()
    v_current_year = current_time.year
    v_current_year_plus1 = v_current_year + 1

    masterlist,academy_player, academy_team, academy_bid = academy_bid_inputs(request,pk)

    df_original = masterlist
    df = masterlist
    library_AFL_Draft_Points = df['AFL_Points_Value']
    
      # Details of the bid
    picklist = []
    df.rename(columns = {'Current_Owner_id':'Current_Owner'}, inplace = True)
    queryset=MasterList.objects.filter(id__in=academy_bid).values()
    for pick_data in queryset:
        picklist.append(pick_data['Display_Name_Detailed'])
    fa_pick = "".join(picklist)
    academy_pts_value = df.loc[df.Display_Name_Detailed == fa_pick, 'AFL_Points_Value'].iloc[0]
    academy_bid_round = df.loc[df.Display_Name_Detailed == fa_pick, 'Draft_Round'].iloc[0]
    academy_bid_round_int = df.loc[df.Display_Name_Detailed == fa_pick, 'Draft_Round_Int'].iloc[0]
    academy_bid_team = df.loc[df.Display_Name_Detailed == fa_pick, 'Current_Owner'].iloc[0]
    academy_bid_pick_no = df.loc[df.Display_Name_Detailed == fa_pick, 'Overall_Pick'].iloc[0]
    academy_pick_type = 'Academy Bid Match'
    
    sum_line1 = str(academy_bid_team) + ' have placed a bid on a ' + str(academy_team) +' academy player at pick ' + str(academy_bid_pick_no) + ' in ' + str(academy_bid_round)
    
    # Defining discounts based off what round the bid came in:
    if academy_bid_round == 'RD1':
        academy_pts_required = float(academy_pts_value) * .8
        sum_line2 = str(academy_team) +' will require ' + str(academy_pts_required) + ' draft points to match bid.'
    else:
        academy_pts_required = academy_pts_value -197
        sum_line2 = str(academy_team) +' will require ' + str(academy_pts_required) + ' draft points to match bid.'
        
    # Creating a copy df of that teams available picks to match bid
    df_subset = df.copy()
    df_subset = df_subset[(df_subset.Current_Owner.astype(int) == int(academy_team)) & (df_subset.Year.astype(int) == int(v_current_year)) & (df_subset.Overall_Pick >= academy_bid_pick_no)]
    
    
      # Creating the cumulative calculations to determine how the points are repaid:
    df['AFL_Points_Value'] = df['AFL_Points_Value'].apply(lambda x: float(x.split()[0].replace(',', '')))


    df_subset['Payoff_Diff'] = df_subset['AFL_Points_Value'].astype(float) - float(academy_pts_required)
    df_subset['AFL_Pts_Left'] = np.where(
        df_subset['Payoff_Diff'] <= 0,
        0,
        np.where(
             df_subset['Payoff_Diff'].astype(float) < df_subset['AFL_Points_Value'].astype(float),
             df_subset['Payoff_Diff'],
             df_subset['AFL_Points_Value']
        )
    )
    #creating previous pick rows to compare whether the picks have to be used or not:
    df_subset['AFL_Pts_Left_previous_pick'] = df_subset['AFL_Pts_Left'].shift()
    df_subset['AFL_Pts_Value_previous_pick'] = df_subset['AFL_Points_Value'].shift()

    
    df_subset['Action'] =  np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value'])  & (df_subset['AFL_Pts_Left']== 0),
                    'Pick lost to back of draft',
                    np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'].astype(int)>0),
                    'Pick Shuffled Backwards',
                    np.where((df_subset['AFL_Pts_Left'] == df_subset['AFL_Points_Value']) & (df_subset['Payoff_Diff'] < 0) & (df_subset['AFL_Pts_Value_previous_pick'].astype(float) > 0)
                    ,'Points Deficit',
                    'No Change')))
    #Add a column for the deficit amount and then define it as a variable:
    df_subset['Deficit_Amount'] = np.where(df_subset['Action'] == 'Points Deficit', df_subset['Payoff_Diff'],np.nan)
    #defining the deficit amount
    try:
        academy_points_deficit = df_subset.loc[df_subset.Action == 'Points Deficit', 'Deficit_Amount'].iloc[0]

    except:
        academy_points_deficit = []
    
    
     #Create lists of changes to make:
    picks_lost = df_subset.loc[df_subset.Action == 'Pick lost to back of draft', 'Display_Name_Detailed'].to_list()

    picks_shuffled = df_subset.loc[df_subset.Action == 'Pick Shuffled Backwards', 'Display_Name_Detailed'].to_list()
    pick_deficit = df_subset.loc[df_subset.Action == 'Points Deficit', 'Display_Name_Detailed'].to_list()
    
    
    
    try:
        picks_shuffled_points_value = df_subset.loc[df_subset.Action == 'Pick Shuffled Backwards', 'AFL_Pts_Left'].iloc[0]

    except:
        picks_shuffled_points_value = np.nan

    carry_over_deficit = academy_points_deficit

    
     # Step 1: Moving all picks to the back of the draft:
     
    if len(picks_lost) > 0:
        pick_lost_details = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])

        for pick in picks_lost:
            # Reset the index
            df = df.reset_index(drop=True)

            #Find row number of pick lost

            
            rowno_picklost = df.index[df.Display_Name_Detailed == pick][0]


            #Find row number of the first pick in the next year
            rowno_startnextyear = df.index[(df.Year.astype(int) == int(v_current_year_plus1)) & (df.Overall_Pick.astype(float) == 1)][0]

            #print(rowno_startnextyear)

            #Insert pick to the row before next years draft:
            df = pd.concat([df.iloc[:rowno_startnextyear], df.iloc[[rowno_picklost]], df.iloc[rowno_startnextyear:]]).reset_index(drop=True)
         
            #Find row number to delete and execute delete:
    
            rowno_delete = df.index[df.Display_Name_Detailed == pick][0]
            #print(rowno_delete)
            df.drop(rowno_delete, axis=0, inplace=True)


            #Changing the names of some key details:
            #Change system note to describe action
            df['System_Note'].mask(df['Display_Name_Detailed'] == pick, 'Academy bid match: pick lost to back of draft', inplace=True)

            #Change the draft round
            df['Draft_Round'].mask(df['Display_Name_Detailed'] == pick, 'BOD', inplace=True)
            df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == pick, 99, inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick, str(v_current_year) + '-Back of Draft', inplace=True)

            #Reset points value
            df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == pick, 0, inplace=True)

            # If needing to update pick moves before the inserts
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
            df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draft_Points).fillna(0)

            #Reset index Again
            df = df.reset_index(drop=True)
            
            #One line summary:
            # print(pick + ' has been lost to the back of the draft.')
            
            #Update picks lost details df
            pick_lost_details_loop = pd.DataFrame({'Pick': pick,
                 'Moves_To': 'End of Draft',
                 'New_Points_Value': 0},index=[0])
            pick_lost_details = pick_lost_details.append(pick_lost_details_loop)

    else:
        pick_lost_details = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])


    if len(picks_shuffled) > 0:
    
        pick_shuffled = picks_shuffled[0]

        # Find row number of pick shuffled
        rowno_pickshuffled = df.index[df.Display_Name_Detailed == pick_shuffled][0]

        # Find the row number of where the pick should be inserted:
        rowno_pickshuffled_to = df[(df.Year.astype(int) == int(v_current_year))]['AFL_Points_Value'].astype(float).ge(picks_shuffled_points_value).idxmin()
 
        #Execute Shuffle
        # Insert pick to the row before next years draft:
        df = pd.concat([df.iloc[:rowno_pickshuffled_to], df.iloc[[rowno_pickshuffled]], df.iloc[rowno_pickshuffled_to:]]).reset_index(drop=True)
     
        # Find row number to delete and execute delete:
        df.drop(rowno_pickshuffled, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draft_Points).fillna(0)

        # Reset index Again
        df = df.reset_index(drop=True)

        # Changing the names of some key details:
        # Change system note to describe action
        df['System_Note'].mask(df['Display_Name_Detailed'] == pick_shuffled, 'Academy bid match: pick shuffled backwards', inplace=True)

        # Change the draft round
        #Just take row above? if above and below equal each other, then value, if not take one above.
        #Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed == pick_shuffled][0] - 1
        #Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int
        
        #Make Changes
        df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == pick_shuffled, new_rd_no,inplace=True)
        
        df['Draft_Round'].mask(df['Display_Name_Detailed'] == pick_shuffled, 'RD' + str(int(new_rd_no)), inplace=True)
        df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick_shuffled, str(v_current_year) + '-RD'+ str(int(new_rd_no)) + '-ShuffledBack', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == pick_shuffled, picks_shuffled_points_value, inplace=True)


        #Summary:
        new_shuffled_pick_no = df.index[df.Display_Name_Detailed == pick_shuffled][0] + 1
        print(pick_shuffled + ' will be shuffled back to pick ' + new_shuffled_pick_no.astype(str) + ' in RD' + str(int(new_rd_no)))

        #Summary Dataframe
        pick_shuffle_details = pd.DataFrame(
            {'Pick': pick_shuffled, 'Moves_To': 'RD' + str(int(new_rd_no)) + '-Pick' + new_shuffled_pick_no.astype(str), 'New_Points_Value': picks_shuffled_points_value},index=[0])

    else:
        pick_shuffle_details = []
        
       # Step 3: Applying the deficit to next year:
    # pick_deficit = '2022-RD1-Pick1-Adelaide Crows'
    if len(pick_deficit) > 0:
        deficit_subset = df.copy()

        deficit_subset = deficit_subset[(deficit_subset.Current_Owner.astype(int) == int(academy_team)) & (deficit_subset.Year.astype(int) == int(v_current_year_plus1)) & (deficit_subset.Draft_Round_Int.astype(int) >= int(academy_bid_round_int))]

        #Finding the first pick in the round to take the points off (and rowno)

        deficit_attached_pick = deficit_subset['Display_Name_Detailed'].iloc[0]
        deficit_pickshuffled_rowno = df.index[df.Display_Name_Detailed == deficit_attached_pick][0]


        #finding the points value of that pick and then adjusting the deficit
        deficit_attached_pts = deficit_subset['AFL_Points_Value'].iloc[0]
        academy_points_deficit_as_float = np.array(list(academy_points_deficit)).astype(float)
    
        deficit_pick_points =   deficit_attached_pts + academy_points_deficit_as_float

        # Find the row number of where the pick should be inserted:

        deficit_pickshuffled_to = df[(int(df.Year[0])+1 == int(v_current_year_plus1))]['AFL_Points_Value'].astype(float).ge(deficit_pick_points).idxmin()

        #Execute pick shuffle
        df = pd.concat([df.iloc[:deficit_pickshuffled_to], df.iloc[[deficit_pickshuffled_rowno]], df.iloc[deficit_pickshuffled_to:]]).reset_index(drop=True)

        # Find row number to delete and execute delete:
        df.drop(deficit_pickshuffled_rowno, axis=0, inplace=True)

        # If needing to update pick numbers after the delete
        df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
        df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draft_Points).fillna(0)

        # Reset index Again
        df = df.reset_index(drop=True)

        # Change system note to describe action
        df['System_Note'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'Academy bid match: Points Deficit',
                               inplace=True)

        # Change the draft round
        # Just take row above? if above and below equal each other, then value, if not take one above.
        # Find row above:
        rowno_new_rd_no = df.index[df.Display_Name_Detailed == deficit_attached_pick][0] - 1

        # Fine Round No from row above:
        new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

        # Make Changes
        df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, new_rd_no, inplace=True)
        df['Draft_Round'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'RD' + new_rd_no.round(0).astype(str),
                               inplace=True)
        df['Pick_Group'].mask(df['Display_Name_Detailed'] == deficit_attached_pick,
                              str(v_current_year) + '-RD' + new_rd_no.round(0).astype(str) + '-AcademyDeficit', inplace=True)

        # Reset points value
        df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, deficit_pick_points , inplace=True)

        # Summary:
        #getting the new overall pick number and what round it belongs to:
        deficit_new_shuffled_pick_no = df[df.Display_Name_Detailed == deficit_attached_pick].Overall_Pick.iloc[0]
        deficit_new_shuffled_pick_RD_no = df[df.Display_Name_Detailed == deficit_attached_pick].Draft_Round.iloc[0]

        #2021-RD3-Pick43-Richmond
        pick_deficit_details = pd.DataFrame(
            {'Pick': deficit_attached_pick, 'Moves_To': deficit_new_shuffled_pick_no, 'New_Points_Value': deficit_pick_points},index=[0])

        print(deficit_attached_pick + ' moves to pick ' + deficit_new_shuffled_pick_no.astype(str) + ' in ' + deficit_new_shuffled_pick_RD_no)

    else:
        pick_deficit_details = []
        
        
    ########## EXECUTE INSERT OF PICK TO THE SPOT OF THE BID ##############
    #inserting pick above academy_bid

    # Make the changes to the masterlist:
    rowno = df.index[df['Display_Name_Detailed'] == fa_pick][0]

    
    # create the line to insert:
    line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(academy_team), 'Position'].iloc[0], 'Year': v_current_year,
                         'TeamName': academy_team, 'PickType': 'AcademyBidMatch', 'Original_Owner': academy_team, 'Current_Owner': academy_team,
                         'Previous_Owner': '', 'Draft_Round': academy_bid_round, 'Draft_Round_Int': academy_bid_round_int,
                         'Pick_Group': str(v_current_year) + '-' + academy_bid_round + '-AcademyBidMatch','Reason': 'Academy Bid Match',
                         'Pick_Status':'Used','Selected_Player': academy_player}, index=[rowno])
    

    # Execute Insert
    #i.e stacks 3 dataframes on top of each other
    df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]).reset_index(drop=True)
    df = df.iloc[rowno]
    
    del df['Original_Owner']
    del df['Current_Owner']
    del df['Previous_Owner']
    del df['TeamName']

    df['id'] = rowno
    df['Original_Owner_id'] = academy_team
    df['Current_Owner_id'] = academy_team
    df['TeamName_id'] = academy_team
    df['Previous_Owner_id'] = ''
    df['projectid_id'] = pk
    MasterList.objects.filter(id=rowno).update(**df)
    new_df = []
    Queryset = MasterList.objects.filter(projectid_id=pk).values()
    for picks in Queryset:
        new_df.append(picks)

    df1 = pd.DataFrame(new_df)
    df1.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    df1.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    df1.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)
    updatedf = update_masterlist(df1)
    iincreament_id = 1
    for index,updaterow in updatedf.iterrows():
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

        # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
        #     previous_owner + team.ShortName + \
        #     ')' if Original_Owner != Current_Ownerr else team.ShortName
        # df.reset_index(drop=False)

        # print(row1['Display_Name_Mini'])
        # exit()
        academy_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        academy_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        # MasterList(**row1).save()   
        model_dictionary = {
            'Year':academy_dict['Year'],
            'PickType':academy_dict['PickType'],
            'TeamName':academy_dict['TeamName'],
            'Position':academy_dict['Position'],
            'Original_Owner':academy_dict['Original_Owner'],
            'Current_Owner':academy_dict['Current_Owner'],
            'Previous_Owner':academy_dict['Previous_Owner'],
            'Draft_Round':academy_dict['Draft_Round'],
            'Draft_Round_Int':academy_dict['Draft_Round_Int'],
            'Pick_Group':academy_dict['Pick_Group'],
            'System_Note':academy_dict['System_Note'],
            'User_Note':academy_dict['User_Note'],
            'Reason':academy_dict['Reason'],
            'Overall_Pick':academy_dict['Overall_Pick'],
            'AFL_Points_Value':academy_dict['AFL_Points_Value'],
            'Unique_Pick_ID':academy_dict['Unique_Pick_ID'],
            'Club_Pick_Number':academy_dict['Club_Pick_Number'],
            'Display_Name':academy_dict['Display_Name'],
            'Display_Name_Short':academy_dict['Display_Name_Short'],
            'Display_Name_Detailed':academy_dict['Display_Name_Detailed'],
            'Display_Name_Mini':academy_dict['Display_Name_Mini'],
            'Current_Owner_Short_Name':academy_dict['Current_Owner_Short_Name'],
            'Pick_Status':academy_dict['Pick_Status'],
            'Selected_Player':academy_dict['Selected_Player'],
            'projectid':academy_dict['projectid']
        }
    
        
        MasterList.objects.filter(id=iincreament_id).update(**model_dictionary)
        
        iincreament_id +=1

    ######## Combine into a summary dataframe: #############
    academy_summaries_list = [pick_lost_details,pick_shuffle_details,pick_deficit_details]

    academy_summary_df = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])
    for x in academy_summaries_list:
        if len(x) > 0:
            academy_summary_df = academy_summary_df.append(x)
    academy_summary_dict = academy_summary_df.to_dict(orient="list")

    ######### Exporting Transaction Details: ###############
    current_time = datetime.datetime.now(pytz.timezone('Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    academy_dict = {academy_team: [academy_pick_type, academy_bid, academy_bid_pick_no, academy_player]}

    ###Create Simple description.
    academy_description = 'Academy Bid Match: Pick '+ str(academy_bid_pick_no) + ' ' + str(academy_team) + ' (' + str(academy_player) + ')'

    obj = Project.objects.get(id=pk)
    
    drafted_player_dict = {academy_team: [academy_bid_round, academy_bid_pick_no,academy_player]}
    drafted_description = 'With pick ' + str(academy_bid_pick_no) + ' ' + str(academy_team) + ' have selected ' + str(academy_player)
   
    obj = Project.objects.get(id=pk)
    drafted_player_transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Drafted_Player',
         'Transaction_Details': [drafted_player_dict],
         'Transaction_Description': drafted_description,
         'projectId':obj.id,
         'Type':'Academy-Bid-V2'
         })
    
    Transactions(**drafted_player_transaction_details).save()
    
    lastinserted_obj = Transactions.objects.latest('id')
    Transactions.objects.filter(Transaction_Number=lastinserted_obj).update()
    
    return Response({'success': 'Academy-Bid-v2 has been Created'}, status=status.HTTP_201_CREATED)    
    

@api_view(['POST'])
@permission_classes([AllowAny])
def add_FA_compansation_request(request,pk):
    
    project_id = pk
    current_date = date.today()
    v_current_year = current_date.year
    v_current_year_plus1 = v_current_year+1

    df = dataframerequest(request,pk)

    data = request.data
    fa_team = data['teamid']
    reason = data['reason']
    types = data['type']
    pickId = data['pickid']
    fa_insert_instructions = data['instructions']
    
    fa_team_name = []
    teams_queryset = Teams.objects.filter(id=int(fa_team)).values()
    for teams_data in teams_queryset:
        fa_team_name.append(teams_data['TeamNames'])
    
    
    fa_pick_type_list = []
    type_query = PicksType.objects.filter(pickType=types).values()
    for types_data in type_query:
        fa_pick_type_list.append(types_data['pickType'])
        
    fa_pick_type = "".join(fa_pick_type_list)

    pick_queryset = MasterList.objects.filter(id=pickId).values()
    fa_aligned_pick_list = []
    for picksdata in pick_queryset:
        fa_aligned_pick_list.append(picksdata['Display_Name_Detailed'])
    fa_aligned_pick = "".join(fa_aligned_pick_list)
    
    if fa_pick_type == 'Start of Draft':
        
        fa_dict = {}
        # Find the first row that is a standard pick:
        
        rowno = df.id[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD1-Standard')].iloc[0]
     
        # create the line to insert:

        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,'TeamName': fa_team,  'PickType': 'FA_Compensation',
                    'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                    'Draft_Round': 'RD1',
                    'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason':reason}, index=[rowno])
        
        # Execute Insert above the rowno


        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        
        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']
        df = df.iloc[rowno]

        df['id'] = rowno
        df['Original_Owner_id'] = fa_team
        df['Current_Owner_id'] = fa_team
        df['TeamName_id'] = fa_team
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = pk
        
        MasterList.objects.filter(id=rowno).update(**df)

        
        fa_round = 'RD1'
        # Update transactions
        fa_dict = fa_team_name + [fa_pick_type, fa_round, reason ,
                             fa_aligned_pick, fa_insert_instructions]

        fa_description = str(fa_team_name) + ' received a ' + \
            str(fa_pick_type) + ' FA Compensation Pick'
            
            
    if fa_pick_type == 'First Round':

        
        fa_round = 'RD1'

        
        fa_aligned_pick = "".join(fa_aligned_pick_list)
        
        rowno = df.id[df['Display_Name_Detailed'] == fa_aligned_pick][0]

        # create the line to insert:
        
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': '', 'Draft_Round': fa_round, 'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason':reason}, index=[rowno])
        
        # Execute Insert
        
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]


            df['id'] = rowno
            df['Original_Owner_id'] = fa_team
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['Previous_Owner_id'] = ''
            df['projectid'] = pk
            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]
            del df['Previous_Owner']
            del df['Original_Owner_id']
            del df['Current_Owner_id']
            # del df['Original_Owner_id']
            
            df['id'] = rowno+1
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = pk
            
            MasterList.objects.filter(id=rowno+1).update(**df)

            
        fa_dict = {}
        # Update Transactions List
        fa_dict = fa_team_name + [fa_pick_type, fa_round, reason ,
                             fa_aligned_pick, fa_insert_instructions]
            
        fa_description = fa_team_name + ' received a ' + \
            fa_pick_type + ' FA Compensation Pick'

    if fa_pick_type == 'End of First Round':
        # Find the last row that is a standard pick:
        
        rowno = df.index[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD1-Standard')][-1]
     
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team),         'Position'].iloc[0], 'Year': v_current_year,
                             'Team_Name': fa_team, 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD1', 'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason':reason}, index=[rowno])
        # Execute Insert below the rowno
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        
        df = df.iloc[rowno+1]    
        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        # del df['TeamName']

        df['id'] = rowno+1
        df['Original_Owner_id'] = fa_team
        df['Current_Owner_id'] = fa_team
        df['TeamName_id'] = fa_team
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = pk


        MasterList.objects.filter(id=rowno+1).update(**df)

        # Update transactions
        fa_dict = {}
        fa_dict = fa_team_name + [fa_pick_type, reason]

        fa_description = fa_team_name + ' received a ' + \
            fa_pick_type + ' FA Compensation Pick'

    if fa_pick_type == 'Start of Second Round':
        
            # Find the first row that is a standard pick in the 2nd round:
        rowno = df.index[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD2-Standard')][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'Pick_Type': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD2',
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason':reason}, index=[rowno])

        # Execute Insert above the rowno
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
        
        df = df.iloc[rowno]

        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']

        df['id'] = rowno
        df['Original_Owner_id'] = fa_team
        df['Current_Owner_id'] = fa_team
        df['TeamName_id'] = fa_team
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = pk


        MasterList.objects.filter(id=rowno).update(**df)
 

        fa_round = 'RD1'
        fa_dict = {}
        # Update transactions
        fa_dict = fa_team_name + [fa_pick_type, fa_round, reason ,
                             fa_aligned_pick, fa_insert_instructions]
        fa_description = fa_team_name + ' received a ' + \
            fa_pick_type + ' FA Compensation Pick'
        
        
        
    if fa_pick_type == 'Second Round':
            
        # Get Details
        fa_team_picks = df['Display_Name_Detailed'].tolist()

        fa_round = 'RD2'

        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        
        rowno = df.id[df['Display_Name_Detailed'] == fa_aligned_pick][0]
 
        
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                            'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                            'Previous_Owner': '', 'Draft_Round': fa_round, 'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason':reason},
                            index=[rowno])

        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                        ).reset_index(drop=True)
            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno
            df['Original_Owner_id'] = fa_team
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = pk
     

            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                        df.iloc[rowno + 1:]]).reset_index(drop=True)
            
            df = pd.concat([df.iloc[:rowno + 1], line,df.iloc[rowno + 1:]]).reset_index(drop=True)
            
            df = df.iloc[rowno+1]
            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno+1
            df['Original_Owner_id'] = fa_team
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = pk
            
            MasterList.objects.filter(id=rowno+1).update(**df)
  

        # Update Transactions List
        fa_dict= {}
        fa_dict = fa_team_name + [fa_pick_type, fa_round, reason ,
                             fa_aligned_pick, fa_insert_instructions]
        fa_description = fa_team_name + ' received a ' + \
            fa_pick_type + ' FA Compensation Pick'
            
     
     
    if fa_pick_type == 'End of Second Round':
            # Find the last row that is a standard pick:
        rowno = df.index[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD2-Standard')][-1]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD2','Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert below the rowno
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        
        df = df.iloc[rowno+1]

        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']

        df['id'] = rowno
        df['Original_Owner_id'] = fa_team
        df['Current_Owner_id'] = fa_team
        df['TeamName_id'] = fa_team
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = pk 

        MasterList.objects.filter(id=rowno).update(**df)
        
        # Update transactions
        fa_round = 'RD2'
        fa_aligned_pick = ''
        fa_unique_pick = ''
        fa_insert_instructions = ''
        fa_dict = {fa_team: [fa_pick_type, fa_round, reason,
                             fa_aligned_pick, fa_unique_pick, fa_insert_instructions]}
        fa_description = fa_team + ' received a ' + fa_pick_type + ' FA Compensation Pick' + '(' + reason + ')'
     
     
            
            
    if fa_pick_type == 'Third Round':
            # Get Details
        fa_team_picks = df['Display_Name_Detailed'].tolist()

        fa_round = 'RD3'
    
        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        rowno = df.id[df['Display_Name_Detailed'] == fa_aligned_pick][0]
 
        
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team,'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': '', 'Draft_Round': fa_round, 'Pick_Group': str(v_current_year) + '-' + 'RD3-Priority-' + fa_pick_type, 'Reason':reason},
                            index=[rowno])

        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]

            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno
            df['Original_Owner_id'] = fa_team
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            
            df = df.iloc[rowno+1]
            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno+1
            df['Original_Owner_id'] = fa_team
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = pk
    
            MasterList.objects.filter(id=rowno+1).update(**df)
        # Update Transactions List
        fa_dict={}
        fa_dict = fa_team_name + [fa_pick_type, fa_round, reason ,
                             fa_aligned_pick, fa_insert_instructions]
        fa_description = fa_team_name + ' received a ' + \
            fa_pick_type + ' FA Compensation Pick'
            
    
    if fa_pick_type == 'Custom Fixed Position':
        fa_round = 'RD5'
        fa_dict = {}
        # find row number of the aligned pick:
        rowno = df.id[df['Display_Name_Detailed'] == fa_aligned_pick][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': int(fa_team), 'PickType': 'FA_Compensation', 'Original_Owner': int(fa_team), 'Current_Owner': int(fa_team),
                             'Previous_Owner': '', 'Draft_Round': fa_round,
                             'Pick_Group': str(v_current_year) + '-' + fa_round + '-Priority-' + fa_pick_type, 'Reason':reason},
                            index=[rowno])

        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            
            df = df.iloc[rowno]
 

            del df['TeamName_id']
            del df['Current_Owner_id']
            del df['Previous_Owner_id']
            del df['Original_Owner_id']

            df['id'] = rowno
            df['Original_Owner'] = fa_team
            df['Current_Owner'] = fa_team
            df['Previous_Owner'] = fa_team
            df['TeamName'] = fa_team
            df['projectid_id'] = pk
          
            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            
            df = df.iloc[rowno+1]

            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno+1
            df['Original_Owner_id'] = fa_team
            df['Previous_Owner_id'] = fa_team 
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['projectid_id'] = pk 
            MasterList.objects.filter(id=rowno+1).update(**df)


        # Update Transactions List
        fa_dict={}
        fa_dict = fa_team_name + [fa_pick_type, fa_round, reason ,
                             fa_aligned_pick, fa_insert_instructions]
        
        fa_description = str(fa_team_name) + ' received a ' + \
            str(fa_pick_type) + ' FA Compensation Pick'
            
    new_df = []
    Queryset = MasterList.objects.filter(projectid_id=pk).values()
    for picks in Queryset:
        new_df.append(picks)

    df1 = pd.DataFrame(new_df)
    df1.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    df1.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    df1.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)

    
    
    udpatedf = update_masterlist(df1)
    udpatedf = udpatedf.drop('id', 1)
    udpatedf = udpatedf.drop('projectid_id', 1)
    udpatedf = udpatedf.drop('Previous_Owner_id', 1)


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

        # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
        #     previous_owner + team.ShortName + \
        #     ')' if Original_Owner != Current_Ownerr else team.ShortName
        # df.reset_index(drop=False)

        # print(row1['Display_Name_Mini'])
        # exit()
        row1['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        row1['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName  
        
        model_dictionary = {
            'Year':row1['Year'],
            'PickType':row1['PickType'],
            'TeamName':row1['TeamName'],
            'Position':row1['Position'],
            'Original_Owner':row1['Original_Owner'],
            'Current_Owner':row1['Current_Owner'],
            'Previous_Owner':row1['Previous_Owner'],
            'Draft_Round':row1['Draft_Round'],
            'Draft_Round_Int':row1['Draft_Round_Int'],
            'Pick_Group':row1['Pick_Group'],
            'System_Note':row1['System_Note'],
            'User_Note':row1['User_Note'],
            'Reason':row1['Reason'],
            'Overall_Pick':row1['Overall_Pick'],
            'AFL_Points_Value':row1['AFL_Points_Value'],
            'Unique_Pick_ID':row1['Unique_Pick_ID'],
            'Club_Pick_Number':row1['Club_Pick_Number'],
            'Display_Name':row1['Display_Name'],
            'Display_Name_Short':row1['Display_Name_Short'],
            'Display_Name_Detailed':row1['Display_Name_Detailed'],
            'Display_Name_Mini':row1['Display_Name_Mini'],
            'Current_Owner_Short_Name':row1['Current_Owner_Short_Name'],
            'Pick_Status':row1['Pick_Status'],
            'Selected_Player':row1['Selected_Player'],
            'projectid':row1['projectid']
        }  
        
        MasterList.objects.filter(id=iincreament_id).update(**model_dictionary)
        
        iincreament_id +=1
        
    current_time = datetime.datetime.now(pytz.timezone('Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    
    fa_dict = {}
    
    fa_dict['fa_team'] =  [fa_round,fa_aligned_pick,fa_insert_instructions]
    f_list = []
    for key , value in fa_dict.items():
        for i in value:
            result = ' ' + key + ' - ' + str(i)
            f_list.append(result)
    fa_str = ''.join(str(e) for e in f_list)

    # Exporting trade to the transactions df
    transaction_details = ( 
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'FA_Compensation', 'Transaction_Details': fa_str, 'Transaction_Description': fa_description,'projectId':pk,'Type':'FA-Compansations'})

    Transactions(**transaction_details).save()
    obj = Transactions.objects.latest('id')
    count = Transactions.objects.filter().count()
    Transactions.objects.filter(id = obj.id ).update(Transaction_Number=count)

    return Response({'success': 'Add-FA-compansation Created Successfuly'}, status=status.HTTP_201_CREATED)



def add_FA_compensation_inputs_request(request,pk):
    
    projectid = pk
    
    masterlist = dataframerequest(request,pk)

    data = request.data
    
     #Ask for team Name:
    fa_team = data['teamid']
    #Ask for FA Type
    fa_pick_type = data['type']
    
    #Ask for FA reason
    reason = data['reason']
    
    fa_round = data['round']
    
    pick_id = data['pickid']
    fa_insert_instructions = data['instructions']
    
     #Define the teams current picks
     
    fa_team_picks = masterlist[masterlist['Current_Owner_id'].astype(int) ==int(fa_team)]['Display_Name_Detailed'].tolist()

    #define a blank round & aligned pick as it will either be made here or within function
    
    fa_aligned_pick_list = []
    # fa_round = ''
    fa_unique_pick = ''
    # fa_insert_instructions = ''
    
    MasterlistQuerySet  = MasterList.objects.filter(id=pick_id).values()
    
    for masterlist_data in MasterlistQuerySet :
        fa_aligned_pick_list.append(masterlist_data['Display_Name_Detailed'])
    
    fa_aligned_pick = "".join(fa_aligned_pick_list)
    
    #ask for extra details depending on pick type:
    if fa_pick_type == 'Custom Fixed Position':
        
        fa_unique_pick = masterlist.loc[masterlist.Display_Name_Detailed == fa_aligned_pick, 'Unique_Pick_ID'].iloc[0]
        
    if fa_pick_type == 'First Round' or fa_pick_type == 'Second Round' or fa_pick_type == 'Third Round':
        
        fa_unique_pick = masterlist.loc[masterlist.Display_Name_Detailed == fa_aligned_pick, 'Unique_Pick_ID'].iloc[0]
        
    return masterlist,pick_id,fa_team, fa_pick_type, fa_round, reason, fa_aligned_pick,fa_unique_pick, fa_insert_instructions
      

@api_view(['POST'])
@permission_classes([AllowAny])
def add_FA_compensation_v2(request,pk):
    
    
    current_date = date.today()
    v_current_year = current_date.year
    masterlist,fa_team,pick_id, fa_pick_type, fa_round, reason, fa_aligned_pick,fa_unique_pick, fa_insert_instructions = add_FA_compensation_inputs_request(request,pk)
    df =masterlist

    if fa_pick_type == 'Start of Draft':
        # Find the first row that is a standard pick:
        rowno = df.id[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD1-Standard')][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': int(fa_team), 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD1','Draft_Round_Int': 1,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason': reason }, index=[rowno])
        
        # Execute Insert above the rowno
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       )
        
        
        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']
        df = df.iloc[1]

        df['id'] = rowno
        df['Original_Owner_id'] = fa_team
        df['Current_Owner_id'] = fa_team
        df['TeamName_id'] = fa_team
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = pk

        # Update transactions
        fa_round = 'RD1'
        # fa_aligned_pick = ''
        # fa_unique_pick = ''
        # fa_insert_instructions = ''
        fa_dict = {}
        fa_dict['fa_team'] =  [fa_pick_type, fa_round, reason,
                             fa_aligned_pick, fa_unique_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + ' FA Compensation Pick' + '(' + str(reason) + ')'
        MasterList.objects.filter(id=rowno).update(**df)
        
    if fa_pick_type == 'First Round':
        # Make the changes to the masterlist:
        rowno = df.index[df['Display_Name_Detailed'] == fa_aligned_pick][0]
        fa_unique_pick = df.loc[df.Display_Name_Detailed == fa_aligned_pick, 'Unique_Pick_ID'].iloc[0]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team,  'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': '', 'Draft_Round': 'RD1', 'Draft_Round_Int': 1,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])
        # Execute Insert
        #i.e stacks 3 dataframes on top of each other
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            
            df = df.iloc[rowno]


            df['id'] = rowno
            df['Original_Owner_id'] = fa_team
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['Previous_Owner_id'] = ''
            df['projectid'] = pk
            MasterList.objects.filter(id=rowno).update(**df)

        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = pd.concat([df.loc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno+1]
            df['id'] = rowno+1
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = pk
            del df['Previous_Owner']
       
            MasterList.objects.filter(id=rowno+1).update(**df)


        # Update transactions
        fa_round = 'RD1'
        
        fa_dict={}
        fa_dict['fa_team'] =  [fa_pick_type, fa_round, reason,fa_aligned_pick, fa_unique_pick, fa_insert_instructions]

        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + ' FA Compensation Pick' + '(' + reason + ')'
        
        
    if fa_pick_type == 'End of First Round':
        # Find the last row that is a standard pick:
        rowno = df.index[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD1-Standard')][-1]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD1','Draft_Round_Int': 1,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert below the rowno
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)   
        df = df.iloc[rowno+1]    
        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']

        df['id'] = rowno+1
        df['Original_Owner_id'] = fa_team
        df['Current_Owner_id'] = fa_team
        df['TeamName_id'] = fa_team
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = pk


        MasterList.objects.filter(id=rowno+1).update(**df)

        # Update transactions
        fa_round = 'RD1'
        fa_aligned_pick = ''
        fa_unique_pick = ''
        fa_insert_instructions = ''
        fa_dict = {}
        fa_dict['fa_team'] =  [fa_pick_type, fa_round, reason,
                             fa_aligned_pick, fa_unique_pick, fa_insert_instructions]

        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + ' FA Compensation Pick' + '(' + reason + ')'
        
    if fa_pick_type == 'Start of Second Round':
        # Find the first row that is a standard pick in the 2nd round:
        rowno = df.id[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD2-Standard')][0]

        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD2','Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert above the rowno
        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)

        df = df.iloc[rowno]

        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']

        df['id'] = rowno
        df['Original_Owner_id'] = fa_team
        df['Current_Owner_id'] = fa_team
        df['TeamName_id'] = fa_team
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = pk

        

        MasterList.objects.filter(id=rowno).update(**df)
    

        # Update transactions
        fa_round = 'RD2'
        fa_aligned_pick = ''
        fa_unique_pick = ''
        fa_insert_instructions = ''
        fa_dict = {}
        fa_dict['fa_team'] =  [fa_pick_type, fa_round, reason,fa_aligned_pick, fa_unique_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + ' FA Compensation Pick' + '(' + reason + ')'
        
        
    if fa_pick_type == 'Second Round':
        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        rowno = df.id[df['Display_Name_Detailed'] == fa_aligned_pick][0]
        fa_unique_pick = df.loc[df.Display_Name_Detailed == fa_aligned_pick, 'Unique_Pick_ID'].iloc[0]
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': '', 'Draft_Round': 'RD2', 'Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])
        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
   
            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno
            df['Original_Owner_id'] = fa_team
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = pk
     

            # MasterList.objects.filter(id=rowno).update(**df)
            
        else:
            
            df = pd.concat([df.iloc[:rowno + 1], line,
            df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]
            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno+1
            df['Original_Owner_id'] = fa_team
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = pk
         

            MasterList.objects.filter(id=rowno+1).update(**df)
            
        # Update Transactions List
        fa_round = 'RD2'
        
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,fa_aligned_pick, fa_unique_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + ' FA Compensation Pick' + '(' + reason + ')'
        
    if fa_pick_type == 'End of Second Round':
        # Find the last row that is a standard pick:

        rowno = df.id[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD2-Standard')].iloc[-1]
   
        fa_dict= {}
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,fa_aligned_pick, fa_unique_pick, fa_insert_instructions]

 
        # create the line to insert:
        
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team,'PickType': 'FA_Compensation',
                             'Original_Owner': fa_team, 'Current_Owner': fa_team, 'Previous_Owner': '',
                             'Draft_Round': 'RD2','Draft_Round_Int': 2,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + fa_pick_type, 'Reason': reason}, index=[rowno])
        # Execute Insert below the rowno
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno+1]

        del df['Original_Owner']
        del df['Current_Owner']
        del df['Previous_Owner']
        del df['TeamName']

        df['id'] = rowno
        df['Original_Owner_id'] = fa_team
        df['Current_Owner_id'] = fa_team
        df['TeamName_id'] = fa_team
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = pk

        MasterList.objects.filter(id=rowno).update(**df)

        # display(df)

        # Update transactions
        fa_round = 'RD2'
        fa_aligned_pick = ''
        fa_unique_pick = ''
        fa_insert_instructions = ''
        
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + ' FA Compensation Pick' + '(' + reason + ')'
        
        
    if fa_pick_type == 'Third Round':
        # Make the changes to the masterlist:
        # find row number of the aligned pick:
                
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,         
                             'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': '', 'Draft_Round': 'RD3', 'Draft_Round_Int': 3,
                             'Pick_Group': str(v_current_year) + '-' + 'RD3-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])

        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]

            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno
            df['Original_Owner_id'] = fa_team
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = pk
            MasterList.objects.filter(id=rowno).update(**df)
            
        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[rowno+1]
            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno+1
            df['Original_Owner_id'] = fa_team
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = pk

            MasterList.objects.filter(id=rowno+1).update(**df)
            
        # Update Transactions List
        fa_round = 'RD3'
        
        fa_dict={}
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,fa_aligned_pick, fa_unique_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + ' FA Compensation Pick' + '(' + reason + ')'
        
    if fa_pick_type == 'Custom Fixed Position':
        # Make the changes to the masterlist:
        # find row number of the aligned pick:
        rowno = df.id[df['Display_Name_Detailed'] == fa_aligned_pick][0]

        
        # create the line to insert:
        fa_unique_pick = df.loc[df.Display_Name_Detailed == fa_aligned_pick, 'Unique_Pick_ID'].iloc[0]

        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fa_team), 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': fa_team, 'PickType': 'FA_Compensation', 'Original_Owner': fa_team, 'Current_Owner': fa_team,
                             'Previous_Owner': '', 'Draft_Round': fa_round, 
                             'Pick_Group': str(v_current_year) + '-' + fa_round + '-Priority-' + fa_pick_type, 'Reason': reason},
                            index=[rowno])
        # Execute Insert
        if fa_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[rowno]
 

            del df['TeamName_id']
            del df['Current_Owner_id']
            del df['Previous_Owner_id']
            del df['Original_Owner_id']

            df['id'] = rowno
            df['Original_Owner'] = fa_team
            df['Current_Owner'] = fa_team
            df['Previous_Owner'] = fa_team
            df['TeamName'] = fa_team
            df['projectid_id'] = pk

          
            MasterList.objects.filter(id=rowno).update(**df)
        else:
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            
            df = df.iloc[rowno+1]

            del df['Original_Owner']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['TeamName']

            df['id'] = rowno+1
            df['Original_Owner_id'] = fa_team
            df['Previous_Owner_id'] = fa_team 
            df['Current_Owner_id'] = fa_team
            df['TeamName_id'] = fa_team
            df['projectid_id'] = pk
            
            MasterList.objects.filter(id=rowno+1).update(**df)

        # Update Transactions List

        
    
        fa_dict={}
        fa_dict['fa_team'] = [fa_pick_type, fa_round, reason,fa_aligned_pick, fa_unique_pick, fa_insert_instructions]
        fa_description = str(fa_team) + ' received a ' + str(fa_pick_type) + ' FA Compensation Pick' + '(' + reason + ')'  
    
    
    
        new_df = []
   
    Queryset = MasterList.objects.filter(projectid_id=pk).values()
    for picks in Queryset:
        new_df.append(picks)

    df1 = pd.DataFrame(new_df)
    df1.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    df1.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    df1.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)

    
    
    udpatedf = update_masterlist(df1)
    udpatedf = udpatedf.drop('id', 1)
    udpatedf = udpatedf.drop('projectid_id', 1)
    udpatedf = udpatedf.drop('Previous_Owner_id', 1)


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

        # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
        #     previous_owner + team.ShortName + \
        #     ')' if Original_Owner != Current_Ownerr else team.ShortName
        # df.reset_index(drop=False)

        # print(row1['Display_Name_Mini'])
        # exit()
        FA_v2_data['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        FA_v2_data['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName  
    
        model_dictionary = {
            'Year':FA_v2_data['Year'],
            'PickType':FA_v2_data['PickType'],
            'TeamName':FA_v2_data['TeamName'],
            'Position':FA_v2_data['Position'],
            'Original_Owner':FA_v2_data['Original_Owner'],
            'Current_Owner':FA_v2_data['Current_Owner'],
            'Previous_Owner':FA_v2_data['Previous_Owner'],
            'Draft_Round':FA_v2_data['Draft_Round'],
            'Draft_Round_Int':FA_v2_data['Draft_Round_Int'],
            'Pick_Group':FA_v2_data['Pick_Group'],
            'System_Note':FA_v2_data['System_Note'],
            'User_Note':FA_v2_data['User_Note'],
            'Reason':FA_v2_data['Reason'],
            'Overall_Pick':FA_v2_data['Overall_Pick'],
            'AFL_Points_Value':FA_v2_data['AFL_Points_Value'],
            'Unique_Pick_ID':FA_v2_data['Unique_Pick_ID'],
            'Club_Pick_Number':FA_v2_data['Club_Pick_Number'],
            'Display_Name':FA_v2_data['Display_Name'],
            'Display_Name_Short':FA_v2_data['Display_Name_Short'],
            'Display_Name_Detailed':FA_v2_data['Display_Name_Detailed'],
            'Display_Name_Mini':FA_v2_data['Display_Name_Mini'],
            'Current_Owner_Short_Name':FA_v2_data['Current_Owner_Short_Name'],
            'Pick_Status':FA_v2_data['Pick_Status'],
            'Selected_Player':FA_v2_data['Selected_Player'],
            'projectid':FA_v2_data['projectid']
        }
    
        
        MasterList.objects.filter(id=iincreament_id).update(**model_dictionary)
        
        iincreament_id +=1
        
     # variables for transactions dict
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    
    fa_dict = {fa_team : [fa_round,fa_aligned_pick,fa_insert_instructions]}
    fa_list = []
    for key,value in fa_dict.items():
        for i in value:
            result = ' ' + key + ' ' + i
            fa_list.append(result)
    fa_str = "".join(fa_list)
    
    # Exporting trade to the transactions df
    FA_v2_transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Priority_Pick', 'Transaction_Details': fa_str, 'Transaction_Description': fa_description,'projectId':pk,'Type':'FA-Compansations-v2'})

    Transactions(**FA_v2_transaction_details).save()
    obj = Transactions.objects.latest('id')
    count = Transactions.objects.filter().count()
    Transactions.objects.filter(id = obj.id ).update(Transaction_Number=count)
    return Response({'success': 'add_FA_compensation_v2 has been Created'}, status=status.HTTP_201_CREATED)    
    
    # ##################### Code Done by Abhishek ########################
    
def add_potential_trade(request, pk):
   
    df = []
    dfobj = MasterList.objects.filter(projectid=pk).values()
    for df_data in dfobj:
        df.append(df_data)
        
    masterlist = pd.DataFrame(df)
    
    data=request.data
    v_team_name = data['teamid']
    Trade_Partner=data['Trade_Partner']
    Trading_Out_Num=data['Trading_Out_Num']
    Trading_Out_Num_Player=data['Trading_Out_Num_Player']
    pick_out_idd = data['pick_trading_out']
    player_trading_out = data['player_trading_out']
    pick_in_id = data['pick_trading_in']
    Trading_In_Num = data['Trading_In_Num']
    Trading_In_Num_Player = data['Trading_In_Num_Player']
    player_trading_in = data['player_trading_in']
    Trading_Out={}
    Trading_Out_Simple=[]
    total_points_out = 0
    total_points_in = 0
    
    pick_trading_out_list = []
    pick_trading_in_list = []
    
    Trading_Out_Num_len = int(Trading_Out_Num)
    Trading_In_Num = int(Trading_Out_Num_Player)
    Trading_In_Num_Player_Num = int(Trading_In_Num_Player)
    
    MasterQuerytset = MasterList.objects.filter(id__in = [pick_out_idd,pick_in_id]).values()

    

    
    for masterlist_data in MasterQuerytset:
        if masterlist_data['id'] == int(pick_out_idd):
            pick_trading_out_list.append(masterlist_data['Display_Name_Detailed'])
        elif masterlist_data['id']==int(pick_in_id):
            pick_trading_in_list.append(masterlist_data['Display_Name_Detailed'])
        
        
    pick_trading_out = "".join(pick_trading_out_list)
    pick_trading_in = "".join(pick_trading_in_list)
    
    if Trading_Out_Num is not None:
        for i in range(Trading_Out_Num_len):
         
            points_trading_out = masterlist.loc[masterlist.Display_Name_Detailed == pick_trading_out, 'AFL_Points_Value'].iloc[0]
            pick_out_id = masterlist.loc[masterlist.Display_Name_Detailed == pick_trading_out, 'Unique_Pick_ID'].iloc[0]

      
            Trading_Out[pick_out_id] = [points_trading_out,pick_out_id]
            Trading_Out_Simple.append(pick_trading_out)
       
    else:
        pass
    
    
    
    #Ask for which players to trade out:
    if Trading_Out_Num_Player is not None:
        for i in range(Trading_In_Num):
            
            Trading_Out['Player'] = [player_trading_out,0]
            Trading_Out_Simple.append(player_trading_out)
    
    Trading_In = dict()
    Trading_In_Simple = []
       #print picks of trade partner
    
    if Trading_Out_Num is not None:
        for i in range(Trading_In_Num):
  
            points_trading_in = masterlist.loc[masterlist.Display_Name_Detailed == pick_trading_in, 'AFL_Points_Value'].iloc[0]
            pick_in_id = masterlist.loc[masterlist.Display_Name_Detailed == pick_trading_in, 'Unique_Pick_ID'].iloc[0]
            Trading_In[pick_in_id] = [pick_trading_in, points_trading_in]
            Trading_In_Simple.append(pick_trading_in)
            
    else:
        pass
   
    if Trading_In_Num_Player is not None:
            for i in range(Trading_In_Num_Player_Num):
                Trading_In['Player'] = [player_trading_in,0]

    #loop to get the points for each pick going out  


    for v in Trading_Out.values():
        
        total_points_out += int(v[0])

    #loop to get the points for each pick coming in
    
    for v in Trading_In.values():
            total_points_in += int(v[1])
    


 
    # print("You will be trading out " + str(total_points_out) + "pts out and receiving " + str(total_points_in) + "pts in.")
    total_points_diff = total_points_in - total_points_out
    
    note = data['notes']
    
    Trading_In_Simple_str = "".join(Trading_In_Simple)
    Trading_In_Out_str = "".join(Trading_Out_Simple)
    Trading_In_str = "".join(Trading_In)
    Trading_Out_list = []
    for trade_out_data in Trading_Out:
        Trading_Out_list.append(trade_out_data)
    Trading_Out_as_str = "".join(Trading_Out_list)
    
    trades = pd.DataFrame({'Trade_Partner': Trade_Partner, 'Trading_Out' : [Trading_Out_Simple],'Trading_In': [Trading_In_Simple],
                            'Points_Out': total_points_out,'Points_In': total_points_in
                            ,  'Points_Diff':total_points_diff,  'Notes':note, 'System_Out':[Trading_Out],'System_In':[Trading_In]},index=[0])
    
    # trades = pd.concat([trades,append_df])
    
    return trades,masterlist,v_team_name
    

@api_view(['POST'])
@permission_classes([AllowAny])
def update_potential_trade(request, pk):
    trades_updated = ''
    trades,masterlist,v_team_name = add_potential_trade(request,pk)
    if trades.empty:
        pass
    else:
        #creating the new trades df to reaplace the old trades at the end of function
        trades_updated = pd.DataFrame(columns=['Trade_Partner', 'Trading_Out',
                                               'Trading_In','Points_Out','Points_In' , 'Points_Diff',  'Notes', 'System_Out','System_In','Warning'])
         # looping over each row to extract the keys and return their current position & value:
         
        for _, row in trades.iterrows():   

            Trading_Out = dict()
            Trading_In = dict()
            Trading_Out_Simple = []
            Trading_In_Simple = []
            Trade_Warning = []

            Trade_Partner = row.Trade_Partner
            Notes = row.Notes
         
            ##### Picks Traded Out ######
            #converting string back to a dictionary:
            d =  ast.literal_eval(str(row.System_Out))
            for k in d:
                unique_pick_id = k
                if unique_pick_id == 'Player':
                

                    for player in d.values():
                        
                        player_trading_out = player[0]
                        
                        Trading_Out['Player'] = [player_trading_out, 0]
                    
                        Trading_Out_Simple.append(player_trading_out)
                        
                                   
                else:                   
                    updated_pick_name = masterlist.loc[masterlist.Unique_Pick_ID == unique_pick_id, 'Display_Name_Detailed'].iloc[0]


                    masterlist.rename(columns = {'Current_Owner_id':'Current_Owner'}, inplace = True)
                    
                    masterlist.rename(columns = {'Previous_Owner_id':'Previous_Owner'}, inplace = True)
                    updated_pick_pts = masterlist.loc[masterlist.Unique_Pick_ID == unique_pick_id, 'AFL_Points_Value'].iloc[0]
                    
                    updated_pick_owner = masterlist.loc[masterlist.Unique_Pick_ID == unique_pick_id, 'Current_Owner'].iloc[0]
                    updated_recent_owner = masterlist.loc[masterlist.Unique_Pick_ID == unique_pick_id, 'Previous_Owner'].iloc[0]
                    if updated_pick_owner != v_team_name or updated_recent_owner == Trade_Partner:
                        warning = 'Trade is no longer valid'
                    else:
                        warning = ''
       
                    #Appending to dictionaries

                    Trade_Warning.append(warning)
                    Trading_In[unique_pick_id] = [updated_pick_name, updated_pick_pts]
                    
                    Trading_In_Simple.append(updated_pick_name)
                    
            total_points_out = 0
            total_points_in = 0           


            #loop to get the points for each pick going out
            for v in Trading_Out.values():
                total_points_out += int(v[1])

            #loop to get the points for each pick coming in
            for v in Trading_In.values():
                total_points_in += int(v[1])

            # Calculations for pick difference
            total_points_diff = total_points_in - total_points_out
            
            
            Trading_In_Simple_str = "".join(Trading_In_Simple)
            Trading_In_Out_str = "".join(Trading_Out_Simple)
            Trading_In_str = "".join(Trading_In)
            Trade_Warning_as_str = "".join(Trade_Warning)
            Trading_Out_list = []
            for trade_out_data in Trading_Out:
                Trading_Out_list.append(trade_out_data)
            Trading_Out_as_str = "".join(Trading_Out_list)
            
            

            # Creating a new row to add to the updated trad
    append_df = pd.DataFrame({'Trade_Partner': Trade_Partner, 'Trading_Out' :Trading_In_Out_str,'Trading_In': Trading_In_Simple_str,
                    'Points_Out': total_points_out,'Points_In': total_points_in
                    ,  'Points_Diff':total_points_diff,  'Notes':Notes, 'System_Out':Trading_Out_as_str,'System_In':Trading_In_str
                    ,'Warning':Trade_Warning_as_str},index=[0])

    # trades_updated = pd.concat([trades_updated,append_df])
        # print(trades_updated)
    Tarde_dict = {}
    for index, updaterow in append_df.iterrows():
        Tarde_dict = dict(updaterow)
        print(Tarde_dict)
    # Trades(**Tarde_dict).save()
                        
    return Response("You will be trading out " + str(total_points_out) + "pts out and receiving " + str(total_points_in) + "pts in.", status=status.HTTP_200_OK)
            
            
        # return trades_updated, trades
        
        
        
        
        #################################### Code done by Abhishek #############################################################

def add_father_son_input(request):

    data=request.data 
    fs_player=data['player']
    fs_team=data['teamid']
    fs_bid=data['pickid']
    
    return fs_player,fs_team,fs_bid

@api_view(['POST'])
@permission_classes([AllowAny])
def add_father_son(request,pk):
    current_date = date.today()
    v_current_year = current_date.year
    v_current_year_plus1 = v_current_year+1

    fs_player,fs_team,fs_bid = add_father_son_input(request)

    teamobj = Teams.objects.get(id=fs_team)
    fs_teamname = teamobj.TeamNames

    df = dataframerequest(request,pk)

    # obj=MasterList.objects.get(id=fs_bid)
    # fs_pick=obj.Display_Name_Detailed
    list=[]
    queryset=MasterList.objects.filter(id__in=fs_bid).values()
    for query in queryset:
        list.append(query['Display_Name_Detailed'])
    fs_pick = "".join(list)
    df.rename(columns = {'Current_Owner_id':'Current_Owner'}, inplace = True)

    fs_pts_value = df.loc[df.Display_Name_Detailed == fs_pick, 'AFL_Points_Value'].iloc[0]
    fs_bid_round = df.loc[df.Display_Name_Detailed == fs_pick, 'Draft_Round'].iloc[0]
    fs_bid_round_int = df.loc[df.Display_Name_Detailed == fs_pick, 'Draft_Round_Int'].iloc[0]
    fs_bid_team = df.loc[df.Display_Name_Detailed == fs_pick, 'Current_Owner'].iloc[0]
    fs_bid_pick_no = df.loc[df.Display_Name_Detailed == fs_pick, 'Overall_Pick'].iloc[0]

    fs_pick_type = 'Father Son Bid Match'
    
    
    sum_line1 = str(fs_bid_team) + ' have placed a bid on a ' + str(fs_team) +' Father Son player at pick ' + str(fs_bid_pick_no) + ' in ' + fs_bid_round

    # Defining discounts based off what round the bid came in:
    if fs_bid_round == 'RD1':
        fs_pts_required = float(fs_pts_value) * .8

        sum_line2 = str(fs_teamname) +' will require ' + str(fs_pts_required) + ' draft points to match bid.'
        print(sum_line2)
    else:
        fs_pts_required = float(fs_pts_value) -197
        sum_line2 = str(fs_teamname) +' will require ' + str(fs_pts_required) + ' draft points to match bid.'
        print(sum_line2)
        
    df_subset = df.copy()

    df_subset = df_subset[(df_subset.Current_Owner.astype(int) == int(fs_team)) & (df_subset.Year.astype( int) == int(v_current_year)) & (df_subset.Overall_Pick.astype(int) >= int(fs_bid_pick_no))]

      # Creating the cumulative calculations to determine how the points are repaid:
   
    df_subset['Cumulative_Pts'] = df_subset.groupby('Current_Owner')['AFL_Points_Value'].transform(pd.Series.cumsum)


    df_subset['Payoff_Diff'] = df_subset['Cumulative_Pts'].astype(float) - fs_pts_required   
    df_subset['AFL_Pts_Left'] = np.where(
        df_subset['Payoff_Diff'] <= 0,
        0,
        np.where(
             df_subset['Payoff_Diff'] < df_subset['AFL_Points_Value'].astype(float),
             df_subset['Payoff_Diff'],
             df_subset['AFL_Points_Value']
        )
    )
    
    
    df_subset['AFL_Pts_Left_previous_pick'] = df_subset['AFL_Pts_Left'].shift()
    df_subset['AFL_Pts_Value_previous_pick'] = df_subset['AFL_Points_Value'].shift()
    

    df_subset['Action'] =  np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left']== 0),
                    'Pick lost to back of draft',
                    np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'].astype(int)>0),
                    'Pick Shuffled Backwards',
                    np.where((df_subset['AFL_Pts_Left'] == df_subset['AFL_Points_Value']) & (df_subset['Payoff_Diff'] < 0) & (df_subset['AFL_Pts_Value_previous_pick'].astype(float) > 0)
                    ,'Points Deficit',
                    'No Change')))
    
    
      #Add a column for the deficit amount and then define it as a variable:
    df_subset['Deficit_Amount'] = np.where(df_subset['Action'] == 'Points Deficit', df_subset['Payoff_Diff'],np.nan)
    
    
    
    try:
        fs_points_deficit = df_subset.loc[df_subset.Action == 'Points Deficit', 'Deficit_Amount'].iloc[0]
    except:
        fs_points_deficit = []

    #Create lists of changes to make:
    picks_lost = df_subset.loc[df_subset.Action == 'Pick lost to back of draft', 'Display_Name_Detailed'].to_list()
    
    picks_shuffled = df_subset.loc[df_subset.Action == 'Pick Shuffled Backwards', 'Display_Name_Detailed'].to_list()
    pick_deficit = df_subset.loc[df_subset.Action == 'Points Deficit', 'Display_Name_Detailed'].to_list()
    
    try:
        picks_shuffled_points_value = df_subset.loc[df_subset.Action == 'Pick Shuffled Backwards', 'AFL_Pts_Left'].iloc[0]
    except:
        picks_shuffled_points_value = np.nan

    carry_over_deficit = fs_points_deficit
    

    
    if len(picks_lost) > 0:
        pick_lost_details = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])

        for pick in picks_lost:
            # Reset the index
            df = df.reset_index(drop=True)

            #Find row number of pick lost
            rowno_picklost = df.index[df.Display_Name_Detailed == pick][0]
            #print(rowno_picklost)

            #Find row number of the first pick in the next year
            rowno_startnextyear = df.index[(df.Year.astype(int) == int(v_current_year_plus1)) & (df.Overall_Pick.astype( int) == 1)][0]
            #print(rowno_startnextyear)

            #Insert pick to the row before next years draft:
            df = pd.concat([df.iloc[:rowno_startnextyear], df.iloc[[rowno_picklost]], df.iloc[rowno_startnextyear:]]).reset_index(drop=True)

            #Find row number to delete and execute delete:
            rowno_delete = df.index[df.Display_Name_Detailed == pick][0]
            #print(rowno_delete)
            df.drop(rowno_delete, axis=0, inplace=True)

            #Changing the names of some key details:
            #Change system note to describe action
            df['System_Note'].mask(df['Display_Name_Detailed'] == pick, 'FS bid match: pick lost to back of draft', inplace=True)

            #Change the draft round
            df['Draft_Round'].mask(df['Display_Name_Detailed'] == pick, 'BOD', inplace=True)
            df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == pick, 99, inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick, str(v_current_year) + '-Back of Draft', inplace=True)

            #Reset points value
            df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == pick, 0, inplace=True)

            # If needing to update pick moves before the inserts
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
            df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draft_Points).fillna(0)

            #Reset index Again
            df = df.reset_index(drop=True)
            
            #One line summary:
            print(pick + ' has been lost to the back of the draft.')
            
            #Update picks lost details df
            pick_lost_details_loop = pd.DataFrame({'Pick': pick,
                 'Moves_To': 'End of Draft',
                 'New_Points_Value': 0},index=[0])
            pick_lost_details = pick_lost_details.append(pick_lost_details_loop)
            
        
            
    else:
        pick_lost_details = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])
    
    
    
    if len(picks_shuffled) > 0:
            pick_shuffled = picks_shuffled[0]

            # Find row number of pick shuffled
            rowno_pickshuffled = df.index[df.Display_Name_Detailed == pick_shuffled][0]

            # Find the row number of where the pick should be inserted:
            rowno_pickshuffled_to = df[(df.Year.astype(int) == v_current_year)]['AFL_Points_Value'].astype(float).ge(picks_shuffled_points_value).idxmin()

            #Execute Shuffle
            # Insert pick to the row before next years draft:
            df = pd.concat([df.iloc[:rowno_pickshuffled_to], df.iloc[[rowno_pickshuffled]], df.iloc[rowno_pickshuffled_to:]]).reset_index(drop=True)

            # Find row number to delete and execute delete:
            df.drop(rowno_pickshuffled, axis=0, inplace=True)

            # If needing to update pick numbers after the delete
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
            df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draft_Points).fillna(0)

            # Reset index Again
            df = df.reset_index(drop=True)

            # Changing the names of some key details:
            # Change system note to describe action
            df['System_Note'].mask(df['Display_Name_Detailed'] == pick_shuffled, 'NGA bid match: pick shuffled backwards', inplace=True)

            # Change the draft round
            #Just take row above? if above and below equal each other, then value, if not take one above.
            #Find row above:
            rowno_new_rd_no = df.index[df.Display_Name_Detailed == pick_shuffled][0] - 1

            #Fine Round No from row above:
            new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

            #Make Changes
            df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == pick_shuffled, new_rd_no,inplace=True)
            df['Draft_Round'].mask(df['Display_Name_Detailed'] == pick_shuffled, 'RD' + str(int(new_rd_no)), inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick_shuffled, str(v_current_year) + '-RD'+ new_rd_no + '-ShuffledBack', inplace=True)

            # Reset points value
            df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == pick_shuffled, picks_shuffled_points_value, inplace=True)


            #Summary:
            new_shuffled_pick_no = df.index[df.Display_Name_Detailed == pick_shuffled][0] + 1
            print(pick_shuffled + ' will be shuffled back to pick ' + new_shuffled_pick_no.astype(str) + ' in RD' + str(int(new_rd_no)))

            #Summary Dataframe
            pick_shuffle_details = pd.DataFrame(
                {'Pick': pick_shuffled, 'Moves_To': 'RD' + str(int(new_rd_no)) + '-Pick' + new_shuffled_pick_no.astype(str), 'New_Points_Value': picks_shuffled_points_value},index=[0])

    else:
            pick_shuffle_details = []

    
    
    if len(pick_deficit) > 0:
            deficit_subset = df.copy()
            deficit_subset = deficit_subset[(deficit_subset.Current_Owner.astype(int) == fs_team) & (deficit_subset.Year.astype(int) == v_current_year_plus1) & (deficit_subset.Draft_Round_Int >= fs_bid_round_int)]
        
        #Finding the first pick in the round to take the points off (and rowno)
            deficit_attached_pick = deficit_subset['Display_Name_Detailed'].iloc[0]
            deficit_pickshuffled_rowno = df.index[df.Display_Name_Detailed == deficit_attached_pick][0]


            #finding the points value of that pick and then adjusting the deficit
            deficit_attached_pts = deficit_subset['AFL_Points_Value'].iloc[0]
            deficit_pick_points =   deficit_attached_pts + fs_points_deficit

            # Find the row number of where the pick should be inserted:
            deficit_pickshuffled_to = df[(df.Year.astype(int) == int(v_current_year_plus1))]['AFL_Points_Value'].astype(float).ge(deficit_pick_points).idxmin()

            #Execute pick shuffle
            df = pd.concat([df.iloc[:deficit_pickshuffled_to], df.iloc[[deficit_pickshuffled_rowno]], df.iloc[deficit_pickshuffled_to:]]).reset_index(drop=True)

            # Find row number to delete and execute delete:
            df.drop(deficit_pickshuffled_rowno, axis=0, inplace=True)

            # If needing to update pick numbers after the delete
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
            df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draft_Points).fillna(0)

            # Reset index Again
            df = df.reset_index(drop=True)

            # Change system note to describe action
            df['System_Note'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'FS bid match: Points Deficit',
                                inplace=True)

            # Change the draft round
            # Just take row above? if above and below equal each other, then value, if not take one above.
            # Find row above:
            rowno_new_rd_no = df.index[df.Display_Name_Detailed == deficit_attached_pick][0] - 1

            # Fine Round No from row above:
            new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

            # Make Changes
            df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, new_rd_no, inplace=True)
            df['Draft_Round'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'RD' + new_rd_no.round(0).astype(str),
                                inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == deficit_attached_pick,
                                str(v_current_year) + '-RD' + new_rd_no.round(0).astype(str) + '-FS_Deficit', inplace=True)

            # Reset points value
            df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, deficit_pick_points , inplace=True)
            

            # Summary:
            #getting the new overall pick number and what round it belongs to:
            deficit_new_shuffled_pick_no = df[df.Display_Name_Detailed == deficit_attached_pick].Overall_Pick.iloc[0]
            deficit_new_shuffled_pick_RD_no = df[df.Display_Name_Detailed == deficit_attached_pick].Draft_Round.iloc[0]
            

        
        

        #2021-RD3-Pick43-Richmond
            pick_deficit_details = pd.DataFrame(
                {'Pick': deficit_attached_pick, 'Moves_To': deficit_new_shuffled_pick_no, 'New_Points_Value': deficit_pick_points},index=[0])

            print(deficit_attached_pick + ' moves to pick ' + deficit_new_shuffled_pick_no.astype(str) + ' in ' + deficit_new_shuffled_pick_RD_no)

    else:
        pick_deficit_details = []


    ########## EXECUTE INSERT OF PICK TO THE SPOT OF THE BID ##############
    #inserting pick above fs_bid

    # Make the changes to the masterlist:

    rowno = df.index[df['Display_Name_Detailed'] == fs_pick][0]
    
    # create the line to insert:

    line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(fs_team), 'Position'].iloc[0], 'Year': v_current_year,
                         'TeamName': fs_team, 'PickType': 'FS_BidMatch', 'Original_Owner': fs_team, 'Current_Owner': fs_team,
                         'Previous_Owner': '', 'Draft_Round': fs_bid_round, 'Draft_Round_Int': fs_bid_round_int,
                         'Pick_Group': str(v_current_year) + '-' + fs_bid_round + '-FSBidMatch','Reason': 'FS Bid Match',
                         'Pick_Status':'Used','Selected_Player': fs_player}, index=[rowno])
    
    # Execute Insert
    #i.e stacks 3 dataframes on top of each other
    df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]).reset_index(drop=True)
    df= df.iloc[rowno]
    
    del df['TeamName_id']
    del df['Original_Owner_id']
    del df['Previous_Owner_id']
    
    df['id'] = rowno
    df['TeamName'] = fs_team
    df['projectid_id'] = pk

    MasterList.objects.filter(id=rowno).update(**df)

    new_df = []
    Queryset = MasterList.objects.filter(projectid_id=pk).values()
    
    for picks in Queryset:
        new_df.append(picks)

    df1 = pd.DataFrame(new_df)
    df1.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    df1.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    df1.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)
        
    ########################## Called Update masterlist ###########################################
     
    updatedf = update_masterlist(df1)
    iincreament_id = 1
    for index,updaterow in updatedf.iterrows():
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

        # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
        #     previous_owner + team.ShortName + \
        #     ')' if Original_Owner != Current_Ownerr else team.ShortName
        # df.reset_index(drop=False)

        # print(row1['Display_Name_Mini'])
        # exit()
        fs_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        fs_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        # MasterList(**row1).save()   
        model_dictionary = {
            'Year':fs_dict['Year'],
            'PickType':fs_dict['PickType'],
            'TeamName':fs_dict['TeamName'],
            'Position':fs_dict['Position'],
            'Original_Owner':fs_dict['Original_Owner'],
            'Current_Owner':fs_dict['Current_Owner'],
            'Previous_Owner':fs_dict['Previous_Owner'],
            'Draft_Round':fs_dict['Draft_Round'],
            'Draft_Round_Int':fs_dict['Draft_Round_Int'],
            'Pick_Group':fs_dict['Pick_Group'],
            'System_Note':fs_dict['System_Note'],
            'User_Note':fs_dict['User_Note'],
            'Reason':fs_dict['Reason'],
            'Overall_Pick':fs_dict['Overall_Pick'],
            'AFL_Points_Value':fs_dict['AFL_Points_Value'],
            'Unique_Pick_ID':fs_dict['Unique_Pick_ID'],
            'Club_Pick_Number':fs_dict['Club_Pick_Number'],
            'Display_Name':fs_dict['Display_Name'],
            'Display_Name_Short':fs_dict['Display_Name_Short'],
            'Display_Name_Detailed':fs_dict['Display_Name_Detailed'],
            'Display_Name_Mini':fs_dict['Display_Name_Mini'],
            'Current_Owner_Short_Name':fs_dict['Current_Owner_Short_Name'],
            'Pick_Status':fs_dict['Pick_Status'],
            'Selected_Player':fs_dict['Selected_Player'],
            'projectid':fs_dict['projectid']
        }
    
        
        MasterList.objects.filter(id=iincreament_id).update(**model_dictionary)
        
        iincreament_id +=1
        

    ######## Combine into a summary dataframe: #############
    fs_summaries_list = [pick_lost_details,pick_shuffle_details,pick_deficit_details]
    fs_summary_df = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])
    for x in fs_summaries_list:
        if len(x) > 0:
            fs_summary_df = fs_summary_df.append(x)


    fs_summary_dict = fs_summary_df.to_dict(orient="list")

    ######### Exporting Transaction Details: ###############
    current_time = datetime.datetime.now(pytz.timezone('Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    fs_dict = {fs_team: [fs_pick_type, fs_bid, fs_bid_pick_no, fs_player]}

    ###Create Simple description.
    fs_description = 'Father Son Bid Match: Pick '+ str(fs_bid_pick_no) + ' ' + str(fs_teamname) + ' (' + str(fs_player) + ')'

    proj_obj = Project.objects.get(id=pk)
    transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'FS_Bid_Match',
         'Transaction_Details': [fs_dict],
         'Transaction_Description': fs_description,
         'projectId':proj_obj.id,
         'Type':"Father-Son"
         })

    Transactions(**transaction_details).save()
    lastinsertedId = Transactions.objects.latest('id')
    Transactions.objects.filter(id=lastinsertedId.id).update(Transaction_Number=lastinsertedId.id)

    ########## EXPORT TRANSACTION OF DRAFT SELECTION ###########
    #Create Drafted Player dict
    
    drafted_player_dict = {fs_team: [fs_bid_round, fs_bid_pick_no,fs_player]}
    drafted_description = 'With pick ' + str(fs_bid_pick_no) + ' ' + str(fs_teamname) + ' have selected ' + str(fs_player)

    drafted_player_transaction_details = (
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Drafted_Player',
         'Transaction_Details': [drafted_player_dict],
         'Transaction_Description': drafted_description,
          'projectId':proj_obj.id,
         'Type':"Drafted-Player-Transactions"
         
        })
    Transactions(**drafted_player_transaction_details).save()
    lastinsertedId = Transactions.objects.latest('id')
    Transactions.objects.filter(id=lastinsertedId.id).update(Transaction_Number=lastinsertedId.id)
    return Response("Success", status=status.HTTP_201_CREATED)

    
def add_nga_bid_inputs(request):

    bid_list = []
    data = request.data
    
    #Ask for player name:
    
    nga_player = data['playerid']
    nga_team_id = data['teamid']
    nga_bid_id = data['pickid']
    teamlist = []
    
    teamqueryset = Teams.objects.filter(id__in = nga_team_id).values()
    for teamvalues in teamqueryset:
        teamlist.append(teamvalues['TeamNames'])
        
    nga_team = "".join(teamlist)
    
    bidqueryset = MasterList.objects.filter(id__in=[nga_bid_id]).values()
    
    for bidvalues in bidqueryset:
        
        bid_list.append(bidvalues['Display_Name_Detailed'])
    
    nga_bid = "".join(bid_list)
    
      #Check to make sure NGA bid is not before pick 40:

    if int(nga_bid_id) < 21:
        
        print("NGA bid match invalid (Bid pick is inside 20)")
        sys.exit("Exiting Function")
        
        #Return variables for main function
    return nga_team_id,nga_player, nga_team, nga_bid 

@api_view(['POST'])
@permission_classes([AllowAny])
def add_nga_bid(request,pk):
    current_day = date.today()
    v_current_year = current_day.year
    v_current_year_plus1 = v_current_year+1
    nga_team_id,nga_player, nga_team, nga_bid = add_nga_bid_inputs(request)
    df = dataframerequest(request,pk) 
        #originals to be returned if cancelling bid:
    df_original = df.copy()
    deficit_subset = df.copy()
    df_subset = df.copy()
    
    
    df.rename(columns = {'Current_Owner_id':'Current_Owner'}, inplace = True)
    df_subset.rename(columns = {'Current_Owner_id':'Current_Owner'}, inplace = True)

        # Details of the bid
 
    nga_pts_value = df.loc[df.Display_Name_Detailed.astype(str) == str(nga_bid), 'AFL_Points_Value'].iloc[0]

    nga_bid_round = df.loc[df.Display_Name_Detailed == nga_bid, 'Draft_Round'].iloc[0]
    nga_bid_round_int = df.loc[df.Display_Name_Detailed == nga_bid, 'Draft_Round_Int'].iloc[0]
    nga_bid_team = df.loc[df.Display_Name_Detailed == nga_bid, 'Current_Owner'].iloc[0]
    nga_bid_pick_no = df.loc[df.Display_Name_Detailed == nga_bid, 'Overall_Pick'].iloc[0]

    nga_pick_type = 'NGA Bid Match'
    
    sum_line1 = str(nga_bid_team) + ' have placed a bid on a ' + str(nga_team) +' NGA player at pick ' + str(nga_bid_pick_no) + ' in ' + nga_bid_round

      # Creating a copy df of that teams available picks to match bid

    df_subset = df_subset[(df_subset.Current_Owner.astype(int) == int(nga_team_id)) & (df_subset.Year.astype(int) == int(v_current_year)) & (df_subset.Overall_Pick.astype(float) >= float(nga_bid_pick_no))]
     
    #Finding out the next pick the club owns in case the bid comes after 40:
    nga_team_next_pick = df_subset.loc[df_subset.Current_Owner.astype(int) == int(nga_team_id), 'Display_Name_Detailed'].iloc[0]
      
      
     ##If the bid is less than pick 41 the it follows the normal points based calculations:    
    if int(nga_bid_pick_no) <41:

        # Defining discounts based off what round the bid came in:
        if nga_bid_round == 'RD1':
            nga_pts_required = float(nga_pts_value) * .8
            sum_line2 = nga_team +' will require ' + f"{nga_pts_required}" + ' draft points to match bid.'
            
        else:
            nga_pts_required = float(nga_pts_value) -197
            sum_line2 = nga_team +' will require ' + f"{nga_pts_required}" + ' draft points to match bid.'
            
            
        df_subset['Cumulative_Pts'] = df_subset.groupby('Current_Owner')['AFL_Points_Value'].transform(pd.Series.cumsum)
        df_subset['Payoff_Diff'] = df_subset['Cumulative_Pts'].astype(float) - nga_pts_required   
        df_subset['AFL_Pts_Left'] = np.where(
            df_subset['Payoff_Diff'] <= 0,
            0,
            np.where(
                df_subset['Payoff_Diff'] < df_subset['AFL_Points_Value'].astype(float),
                df_subset['Payoff_Diff'],
                df_subset['AFL_Points_Value']
            )
        )
                
        #creating previous pick rows to compare whether the picks have to be used or not:
        df_subset['AFL_Pts_Left_previous_pick'] = df_subset['AFL_Pts_Left'].shift()
        df_subset['AFL_Pts_Value_previous_pick'] = df_subset['AFL_Points_Value'].shift()
        
        df_subset['AFL_Pts_Value_previous_pick'] = np.array(list(df_subset['AFL_Pts_Value_previous_pick'])).astype(float)
        df_subset.fillna(0)
        df_subset['Action'] =  np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left']== 0),
                        'Pick lost to back of draft',
                        np.where((df_subset['AFL_Pts_Left'] != df_subset['AFL_Points_Value']) & (df_subset['AFL_Pts_Left'].astype(float)>0),
                        'Pick Shuffled Backwards',
                        np.where((df_subset['AFL_Pts_Left'] == df_subset['AFL_Points_Value']) & (df_subset['Payoff_Diff'].astype(float) < 0) & (df_subset['AFL_Pts_Value_previous_pick'].fillna(0).astype(float) > 0)
                        ,'Points Deficit',
                        'No Change')))

        df_subset['Deficit_Amount'] = np.where(df_subset['Action'] == 'Points Deficit', df_subset['Payoff_Diff'],np.nan)
        
         #defining the deficit amount
        try:
            nga_points_deficit = df_subset.loc[df_subset.Action == 'Points Deficit', 'Deficit_Amount'].iloc[0]
            
        except:
            nga_points_deficit = []
            
        #Create lists of changes to make:
        picks_lost = df_subset.loc[df_subset.Action == 'Pick lost to back of draft', 'Display_Name_Detailed'].to_list()
        picks_shuffled = df_subset.loc[df_subset.Action == 'Pick Shuffled Backwards', 'Display_Name_Detailed'].to_list()
        pick_deficit = df_subset.loc[df_subset.Action == 'Points Deficit', 'Display_Name_Detailed'].to_list()

        try:
            picks_shuffled_points_value = df_subset.loc[df_subset.Action == 'Pick Shuffled Backwards', 'AFL_Pts_Left'].iloc[0]
            # print(picks_shuffled_points_value)
        except:
            picks_shuffled_points_value = np.nan
            # print(picks_shuffled_points_value)
        carry_over_deficit = nga_points_deficit
        # Step 1: Moving all picks to the back of the draft:

        if len(picks_lost) > 0:
            pick_lost_details = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])
            
            
            for pick in picks_lost:
                    # Reset the index
                df = df.reset_index(drop=True)
                #Find row number of pick lost
                rowno_picklost = df.index[df.Display_Name_Detailed == pick][0]
                #Find row number of the first pick in the next year
                rowno_startnextyear = df.index[(df.Year.astype(int) ==int( v_current_year_plus1)) & (df.Overall_Pick.astype(int) == 1)][0]
                #print(rowno_startnextyear)

                #Insert pick to the row before next years draft:
                df = pd.concat([df.iloc[:rowno_startnextyear], df.iloc[[rowno_picklost]], df.iloc[rowno_startnextyear:]]).reset_index(drop=True)
                #Find row number to delete and execute delete:
                rowno_delete = df.index[df.Display_Name_Detailed == pick][0]
                #print(rowno_delete)
                df.drop(rowno_delete, axis=0, inplace=True)
                #Changing the names of some key details:
                #Change system note to describe action
                df['System_Note'].mask(df['Display_Name_Detailed'] == pick, 'NGA bid match: pick lost to back of draft', inplace=True)

                #Change the draft round
                df['Draft_Round'].mask(df['Display_Name_Detailed'] == pick, 'BOD', inplace=True)
                df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == pick, 99, inplace=True)
                df['Pick_Group'].mask(df['Display_Name_Detailed'] == pick, str(v_current_year) + '-Back of Draft', inplace=True)

                #Reset points value
                df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == pick, 0, inplace=True)

                # If needing to update pick moves before the inserts
                df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
                library_AFL_Draft_Points = df['AFL_Points_Value']
                df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draft_Points).fillna(0)

                #Reset index Again
                df = df.reset_index(drop=True)
                
                #One line summary:
                print(pick + ' has been lost to the back of the draft.')
                
                #Update picks lost details df
                pick_lost_details_loop = pd.DataFrame({'Pick': pick,
                    'Moves_To': 'End of Draft',
                    'New_Points_Value': 0},index=[0])
                pick_lost_details = pick_lost_details.append(pick_lost_details_loop)
        

        else:
            pick_lost_details = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])

        
                # Step 2: Shuffling Pick back to their spot

        if len(picks_shuffled) > 0:
            

            pick_shuffled = picks_shuffled[0]
  
            # Find row number of pick shuffled
            
            rowno_pickshuffled = df.index[df.Display_Name_Detailed == pick_shuffled][0]
     
      
            # Find the row number of where the pick should be inserted:

            rowno_pickshuffled_to = df[(df.Year.astype(int) == int(v_current_year))]['AFL_Points_Value'].astype(float).ge(picks_shuffled_points_value).idxmin()
   
            #Execute Shuffle
            # Insert pick to the row before next years draft:
            df = pd.concat([df.iloc[:rowno_pickshuffled_to], df.iloc[[rowno_pickshuffled]], df.iloc[rowno_pickshuffled_to:]]).reset_index(drop=True)
            # Find row number to delete and execute delete:
            df.drop(rowno_pickshuffled, axis=0, inplace=True)


            # If needing to update pick numbers after the delete
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
            library_AFL_Draft_Points = df['AFL_Points_Value']
            df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draft_Points).fillna(0)

            # Reset index Again
            df = df.reset_index(drop=True)

            # Changing the names of some key details:
            # Change system note to describe action
            picks_shuffled_str = "".join(picks_shuffled)
            df['System_Note'].mask(df['Display_Name_Detailed'].astype(str) == picks_shuffled_str, 'NGA bid match: pick shuffled backwards', inplace=True)

            # Change the draft round
            #Just take row above? if above and below equal each other, then value, if not take one above.
            #Find row above:
            rowno_new_rd_no = df.index[df.Display_Name_Detailed == picks_shuffled_str][0] - 1

            #Fine Round No from row above:
            new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

            #Make Changes
            df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == picks_shuffled_str, new_rd_no,inplace=True)
            df['Draft_Round'].mask(df['Display_Name_Detailed'] == picks_shuffled_str, 'RD' + str(int(new_rd_no)), inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == picks_shuffled_str, str(v_current_year) + '-RD'+ new_rd_no + '-ShuffledBack', inplace=True)

            # Reset points value
            df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == picks_shuffled_str, picks_shuffled_points_value, inplace=True)


            #Summary:
            new_shuffled_pick_no = df.index[df.Display_Name_Detailed == picks_shuffled_str][0] + 1
            # print(picks_shuffled + ' will be shuffled back to pick ' + new_shuffled_pick_no.astype(str) + ' in RD' + str(int(new_rd_no)))

            #Summary Dataframe
            pick_shuffle_details = pd.DataFrame(
                {'Pick': picks_shuffled_str, 'Moves_To': 'RD' + str(int(new_rd_no)) + '-Pick' + new_shuffled_pick_no.astype(str), 'New_Points_Value': picks_shuffled_points_value},index=[0])
        
        else:
            pick_shuffle_details = []
            
        # Step 3: Applying the deficit to next year:

        if len(pick_deficit) > 0:
            library_AFL_Draft_Points = df['AFL_Points_Value']
            deficit_subset.rename(columns = {'Current_Owner_id':'Current_Owner'}, inplace = True)
            deficit_subset = deficit_subset[(deficit_subset.Current_Owner.astype(int) == int(nga_team_id)) & (int(deficit_subset.Year[0])+1 == int(v_current_year_plus1)) & (deficit_subset.Draft_Round_Int.astype(int) >= int(nga_bid_round_int))]

            #Finding the first pick in the round to take the points off (and rowno)
            deficit_attached_pick = deficit_subset['Display_Name_Detailed'].iloc[0]
            deficit_pickshuffled_rowno = df.index[df.Display_Name_Detailed == deficit_attached_pick][0]


            #finding the points value of that pick and then adjusting the deficit
            deficit_attached_pts = deficit_subset['AFL_Points_Value']

            deficit_pick_points =   deficit_attached_pts + nga_points_deficit

            # Find the row number of where the pick should be inserted:
            deficit_pickshuffled_to = df[(df.Year == v_current_year_plus1)]['AFL_Points_Value'].ge(deficit_pick_points.astype(float)).idxmin()

            #Execute pick shuffle
            df = pd.concat([df.iloc[:deficit_pickshuffled_to], df.iloc[[deficit_pickshuffled_rowno]], df.iloc[deficit_pickshuffled_to:]]).reset_index(drop=True)

            # Find row number to delete and execute delete:
            df.drop(deficit_pickshuffled_rowno, axis=0, inplace=True)

            # If needing to update pick numbers after the delete
            df['Overall_Pick'] = df.groupby('Year').cumcount() + 1
            
            df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draft_Points).fillna(0)

            # Reset index Again
            df = df.reset_index(drop=True)

            # Change system note to describe action
            df['System_Note'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'NGA bid match: Points Deficit',
                                inplace=True)

            # Change the draft round
            # Just take row above? if above and below equal each other, then value, if not take one above.
            # Find row above:
            rowno_new_rd_no = df.index[df.Display_Name_Detailed == deficit_attached_pick][0] - 1

            # Fine Round No from row above:
            new_rd_no = df.iloc[rowno_new_rd_no].Draft_Round_Int

            # Make Changes
            df['Draft_Round_Int'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, new_rd_no, inplace=True)
            df['Draft_Round'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, 'RD' + str(int(new_rd_no)),
                                inplace=True)
            df['Pick_Group'].mask(df['Display_Name_Detailed'] == deficit_attached_pick,
                                str(v_current_year) + '-RD' + str(int(new_rd_no)) + '-NGA_Deficit', inplace=True)

            # Reset points value
            df['AFL_Points_Value'].mask(df['Display_Name_Detailed'] == deficit_attached_pick, deficit_pick_points , inplace=True)

            # Summary:
            #getting the new overall pick number and what round it belongs to:
            deficit_new_shuffled_pick_no = df[df.Display_Name_Detailed == deficit_attached_pick].Overall_Pick.iloc[0]
            deficit_new_shuffled_pick_RD_no = df[df.Display_Name_Detailed == deficit_attached_pick].Draft_Round.iloc[0]

            #2021-RD3-Pick43-Richmond
            pick_deficit_details = pd.DataFrame(
                {'Pick': deficit_attached_pick, 'Moves_To': deficit_new_shuffled_pick_no, 'New_Points_Value': deficit_pick_points},index=[0])

            print(deficit_attached_pick + ' moves to pick ' + deficit_new_shuffled_pick_no.astype(str) + ' in ' + deficit_new_shuffled_pick_RD_no)

        else:
            pick_deficit_details = []
        
        ########## EXECUTE INSERT OF PICK TO THE SPOT OF THE BID ##############
        #inserting pick above nga_bid

        # Make the changes to the masterlist:
        rowno = df.index[df['Display_Name_Detailed'] == nga_bid][0]
     
        # create the line to insert:
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(nga_team_id), 'Position'].iloc[0], 'Year': v_current_year,
                            'TeamName': nga_team_id, 'PickType': 'NGA_BidMatch', 'Original_Owner': nga_team_id, 'Current_Owner': nga_team_id,
                            'Previous_Owner': '', 'Draft_Round': nga_bid_round, 'Draft_Round_Int': nga_bid_round_int,
                            'Pick_Group': str(v_current_year) + '-' + nga_bid_round + '-NGABidMatch','Reason': 'NGA Bid Match',
                            'Pick_Status':'Used','Selected_Player': nga_player}, index=[rowno])

        # Execute Insert
        #i.e stacks 3 dataframes on top of each other

        df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]).reset_index(drop=True)
        
        del df['TeamName']
        # del df['Current_Owner']
        del df['Original_Owner']
        del df['Previous_Owner']
        del df['projectid_id']
        df.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
        df.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
        df.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)
        df.rename(columns={'Previous_Owner_id': 'Previous_Owner'}, inplace=True)
        # df = df.astype({"TeamName":'int'})
        df = df.iloc[rowno]
        df['id']= rowno+1
        df['projectid'] = pk
        df['Original_Owner'] = nga_team_id
        df['TeamName'] = nga_team_id   
        df['Previous_Owner'] = ''

        MasterList.objects.filter(id=rowno+1).update(**df) 
        
        
        ######## #### call update masterlist ###################################
        
        df1 = dataframerequest(request,pk) 
        df1.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
        df1.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
        df1.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)
        df1.rename(columns={'Previous_Owner_id': 'Previous_Owner'}, inplace=True)
        updatedf = update_masterlist(df1)

        iincreament_id = 1
        for index,updaterow in updatedf.iterrows():
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

            # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
            #     previous_owner + team.ShortName + \
            #     ')' if Original_Owner != Current_Ownerr else team.ShortName
            # df.reset_index(drop=False)

            # print(row1['Display_Name_Mini'])
            # exit()
            nga_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
                previous_owner + team.ShortName + \
                ')' if Original_Owner != Current_Ownerr else team.ShortName

            nga_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
                previous_owner + team.ShortName + \
                ')' if Original_Owner != Current_Ownerr else team.ShortName

            # MasterList(**row1).save()   
            model_dictionary = {
                'Year':nga_dict['Year'],
                'PickType':nga_dict['PickType'],
                'TeamName':nga_dict['TeamName'],
                'Position':nga_dict['Position'],
                'Original_Owner':nga_dict['Original_Owner'],
                'Current_Owner':nga_dict['Current_Owner'],
                'Previous_Owner':nga_dict['Previous_Owner'],
                'Draft_Round':nga_dict['Draft_Round'],
                'Draft_Round_Int':nga_dict['Draft_Round_Int'],
                'Pick_Group':nga_dict['Pick_Group'],
                'System_Note':nga_dict['System_Note'],
                'User_Note':nga_dict['User_Note'],
                'Reason':nga_dict['Reason'],
                'Overall_Pick':nga_dict['Overall_Pick'],
                'AFL_Points_Value':nga_dict['AFL_Points_Value'],
                'Unique_Pick_ID':nga_dict['Unique_Pick_ID'],
                'Club_Pick_Number':nga_dict['Club_Pick_Number'],
                'Display_Name':nga_dict['Display_Name'],
                'Display_Name_Short':nga_dict['Display_Name_Short'],
                'Display_Name_Detailed':nga_dict['Display_Name_Detailed'],
                'Display_Name_Mini':nga_dict['Display_Name_Mini'],
                'Current_Owner_Short_Name':nga_dict['Current_Owner_Short_Name'],
                'Pick_Status':nga_dict['Pick_Status'],
                'Selected_Player':nga_dict['Selected_Player'],
                'projectid':nga_dict['projectid']
            }
        
            
            MasterList.objects.filter(id=iincreament_id).update(**model_dictionary)
            
            iincreament_id +=1
    

            ######## Combine into a summary dataframe: #############
            nga_summaries_list = [pick_lost_details,pick_shuffle_details,pick_deficit_details]
            nga_summary_df = pd.DataFrame(columns=['Pick', 'Moves_To', 'New_Points_Value'])
            for x in nga_summaries_list:
                if len(x) > 0:
                    nga_summary_df = nga_summary_df.append(x)

            nga_summary_dict = nga_summary_df.to_dict(orient="list")

            ######### Exporting Transaction Details: ###############
            current_time = datetime.datetime.now(pytz.timezone('Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
            nga_dict = {nga_team: [nga_pick_type, nga_bid, nga_bid_pick_no, nga_player]}

            ###Create Simple description.
            nga_description = 'NGA Bid Match: Pick '+ str(nga_bid_pick_no) + ' ' + str(nga_team) + ' (' + str(nga_player) + ')'

            obj = Project.objects.get(id=pk)
            transaction_details = (
                {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'NGA_Bid_Match',
                'Transaction_Details': [nga_dict],
                'Transaction_Description': nga_description,
                'Type':'NGA-Bid',
                'projectId':obj.id
                })
            Transactions(**transaction_details).save()
            last_obj = Transactions.objects.latest('id')
            Transactions.objects.filter(id=last_obj.id).update(Transaction_Number=last_obj.id)
            return Response({'success':'success'}, status=status.HTTP_201_CREATED) 

# #####################################################  Code Done By ABhishek ##########################


def add_draft_night_selection_request(request):   
    data=request.data
    selected_pick_id=data['selected_pick_id']
    player_taken_id=data['player_taken_id']
    return selected_pick_id, player_taken_id


@ api_view(['POST'])
@ permission_classes([AllowAny, ])
def add_draft_night_selection(request,pk):
    masterlist = dataframerequest(request,pk)
    current_date = date.today()
    v_current_year = current_date.year
    selected_pick_id, player_taken_id = add_draft_night_selection_request(request)
    
    pick_obj=MasterList.objects.get(id=selected_pick_id)
    selected_pick = pick_obj.Display_Name_Detailed
    player_obj=Players.objects.get(id=player_taken_id)
    player_taken = player_obj.Full_Name
    masterlist['Pick_Status'].mask(masterlist['Display_Name_Detailed'] == selected_pick, 'Used' , inplace=True)
    masterlist['Selected_Player'].mask(masterlist['Display_Name_Detailed'] == selected_pick, player_taken , inplace=True)

    current_time = datetime.datetime.now(pytz.timezone('Australia/Melbourne')).strftime('%Y-%m-%d %H:%M')
    team_name = masterlist.loc[masterlist.Display_Name_Detailed == selected_pick, 'Current_Owner'].iloc[0]
    pick_round = masterlist.loc[masterlist.Display_Name_Detailed == selected_pick, 'Draft_Round'].iloc[0]
    overall_pick = masterlist.loc[masterlist.Display_Name_Detailed == selected_pick, 'Overall_Pick'].iloc[0]
  
    drafted_player_dict = {team_name: [pick_round, overall_pick,player_taken]}
    drafted_description = 'With pick ' + str(overall_pick)+ ' ' + str(team_name) + ' have selected ' + str(player_taken)
    
    # ####################call masterlist ########################################
    
    # df = dataframerequest(request,pk) 

    masterlist.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    masterlist.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    masterlist.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)
    masterlist.rename(columns={'Previous_Owner_id': 'Previous_Owner'}, inplace=True)
    updatedf = update_masterlist(masterlist)


    iincreament_id = 1
    for index,updaterow in updatedf.iterrows():

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

        # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
        #     previous_owner + team.ShortName + \
        #     ')' if Original_Owner != Current_Ownerr else team.ShortName
        # df.reset_index(drop=False)

        # print(row1['Display_Name_Mini'])
        # exit()
        draft_night_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        draft_night_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        # MasterList(**row1).save()   
        model_dictionary = {
            'Year':draft_night_dict['Year'],
            'PickType':draft_night_dict['PickType'],
            'TeamName':draft_night_dict['TeamName'],
            'Position':draft_night_dict['Position'],
            'Original_Owner':draft_night_dict['Original_Owner'],
            'Current_Owner':draft_night_dict['Current_Owner'],
            'Previous_Owner':draft_night_dict['Previous_Owner'],
            'Draft_Round':draft_night_dict['Draft_Round'],
            'Draft_Round_Int':draft_night_dict['Draft_Round_Int'],
            'Pick_Group':draft_night_dict['Pick_Group'],
            'System_Note':draft_night_dict['System_Note'],
            'User_Note':draft_night_dict['User_Note'],
            'Reason':draft_night_dict['Reason'],
            'Overall_Pick':draft_night_dict['Overall_Pick'],
            'AFL_Points_Value':draft_night_dict['AFL_Points_Value'],
            'Unique_Pick_ID':draft_night_dict['Unique_Pick_ID'],
            'Club_Pick_Number':draft_night_dict['Club_Pick_Number'],
            'Display_Name':draft_night_dict['Display_Name'],
            'Display_Name_Short':draft_night_dict['Display_Name_Short'],
            'Display_Name_Detailed':draft_night_dict['Display_Name_Detailed'],
            'Display_Name_Mini':draft_night_dict['Display_Name_Mini'],
            'Current_Owner_Short_Name':draft_night_dict['Current_Owner_Short_Name'],
            'Pick_Status':draft_night_dict['Pick_Status'],
            'Selected_Player':draft_night_dict['Selected_Player'],
            'projectid':draft_night_dict['projectid']
        }
    
        
        MasterList.objects.filter(id=iincreament_id).update(**model_dictionary)
        
        iincreament_id +=1
    Projobj = Project.objects.get(id=pk)
    Proj_id = Projobj.id
    drafted_player_transaction_details = pd.DataFrame(
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Drafted_Player',
         'Transaction_Details': [drafted_player_dict],
         'Transaction_Description': drafted_description,
         'Type':'Add-Draft-Night-Selection',
         'projectId':Proj_id
         })
    Transactions(**drafted_player_transaction_details).save()      
    obj=Transactions.objects.latest('id')
    Transactions.objects.filter(id=obj.id).update(Transaction_Number=obj.id)
    return Response({'success':"Add-draft-Night-Selection created successfully"}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def AddManualRequest(request, pk):
    current_date = date.today()
    v_current_year = current_date.year
    masterlist = []
    dfobj = MasterList.objects.filter(projectid=pk).values()
    for df_data in dfobj:
        masterlist.append(df_data)
    df = pd.DataFrame(masterlist)
    data  =  request.data
    pick_id  = data['pickid']
    manual_team  = data['teamid']
    manual_round = data['round']
    manual_insert_instructions = data['instructions']
    reason = data['reason']
    manual_pick_type = 'Manual Insert'
    
    manual_aligned_pick = []
    pickqueryset  = MasterList.objects.filter(id = pick_id).values()
    manual_aligned_pick = pickqueryset[0]['Display_Name_Detailed']
 
    rowno = df.index[df['Display_Name_Detailed'] == manual_aligned_pick][1]


    line = pd.DataFrame({'Position': df.loc[df.TeamName_id.astype(int) == int(manual_team), 'Position'].iloc[0], 'Year': v_current_year,
                         'TeamName': int(manual_team), 'PickType': 'Manual_Insert', 'Original_Owner': manual_team, 'Current_Owner': manual_team,
                         'Previous_Owner': '', 'Draft_Round': manual_round, 'Pick_Group': str(v_current_year) + '-' + 'RD1-Manual', 'Reason': reason},
                        index=[rowno])

    
    if manual_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                       ).reset_index(drop=True)
            df = df.iloc[rowno]
            
            del df['TeamName_id']
            del df['Current_Owner_id']
            del df['Previous_Owner_id']
            del df['Original_Owner_id']

            df['id'] = rowno
            df['TeamName']=manual_team
            df['projectid_id']=pk

            MasterList.objects.filter(id=rowno).update(**df)
    else:
        df = pd.concat([df.iloc[:rowno + 1], line,
                       df.iloc[rowno + 1:]]).reset_index(drop=True)
        df = df.iloc[rowno]
        del df['TeamName_id']
        del df['Current_Owner_id']
        del df['Previous_Owner_id']
        del df['Original_Owner_id']

        df['id'] = rowno+1
        df['TeamName']=manual_team
        df['Current_Owner']=manual_team
        df['Original_Owner']=manual_team
        df['Previous_Owner']=''
        df['projectid_id']=pk
        MasterList.objects.filter(id=rowno+1).update(**df)
    
    df1 = dataframerequest(request,pk)

    updatedf = update_masterlist(df1)

    updatedf.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    updatedf.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    updatedf.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)
    updatedf.rename(columns={'Previous_Owner_id': 'Previous_Owner'}, inplace=True)

    iincreament_id = 1
    for index,updaterow in updatedf.iterrows():

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

        # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
        #     previous_owner + team.ShortName + \
        #     ')' if Original_Owner != Current_Ownerr else team.ShortName
        # df.reset_index(drop=False)

        # print(row1['Display_Name_Mini'])
        # exit()
        manual_dict['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        manual_dict['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr + ' (Origin: ' + Original_Owner + ', Via: ' + \
            previous_owner + team.ShortName + \
            ')' if Original_Owner != Current_Ownerr else team.ShortName

        # MasterList(**row1).save()   
        model_dictionary = {
            'Year':manual_dict['Year'],
            'PickType':manual_dict['PickType'],
            'TeamName':manual_dict['TeamName'],
            'Position':manual_dict['Position'],
            'Original_Owner':manual_dict['Original_Owner'],
            'Current_Owner':manual_dict['Current_Owner'],
            'Previous_Owner':manual_dict['Previous_Owner'],
            'Draft_Round':manual_dict['Draft_Round'],
            'Draft_Round_Int':manual_dict['Draft_Round_Int'],
            'Pick_Group':manual_dict['Pick_Group'],
            'System_Note':manual_dict['System_Note'],
            'User_Note':manual_dict['User_Note'],
            'Reason':manual_dict['Reason'],
            'Overall_Pick':manual_dict['Overall_Pick'],
            'AFL_Points_Value':manual_dict['AFL_Points_Value'],
            'Unique_Pick_ID':manual_dict['Unique_Pick_ID'],
            'Club_Pick_Number':manual_dict['Club_Pick_Number'],
            'Display_Name':manual_dict['Display_Name'],
            'Display_Name_Short':manual_dict['Display_Name_Short'],
            'Display_Name_Detailed':manual_dict['Display_Name_Detailed'],
            'Display_Name_Mini':manual_dict['Display_Name_Mini'],
            'Current_Owner_Short_Name':manual_dict['Current_Owner_Short_Name'],
            'Pick_Status':manual_dict['Pick_Status'],
            'Selected_Player':manual_dict['Selected_Player'],
            'projectid':manual_dict['projectid']
        }
    
        
        MasterList.objects.filter(id=iincreament_id).update(**model_dictionary)
        
        iincreament_id +=1
        
    
    manual_dict = {manual_team: [
        manual_pick_type, manual_round, manual_aligned_pick, manual_insert_instructions, reason]}
    manual_description = manual_team + ' received a ' + manual_pick_type + ' Pick'
    manual_dict_list = []
    for key,value in manual_dict.items():
        for i in value:
            result = ' ' + key + ' ' + i
            manual_dict_list.append(result)
    manual_desc_str = "".join(manual_dict_list)
        
    current_time = datetime.datetime.now(pytz.timezone(
        'Australia/Melbourne')).strftime('%Y-%m-%d %H:%M') 
    
    transaction_details = pd.DataFrame(
        {'Transaction_Number': '', 'Transaction_DateTime': current_time, 'Transaction_Type': 'Manual_Insert', 'Transaction_Details': [manual_dict], 'Transaction_Description': manual_description,'projectId':pk})

    Transactions(**transaction_details).save()
    obj = Transactions.objects.latest('id')
    Transactions_count = Transactions.objects.filter().count()

    Transactions.objects.filter(id=obj.id).update(Transaction_Number=Transactions_count)
    return Response({'success': 'Add Manual created Successfully'}, status=status.HTTP_201_CREATED)

    
@api_view(['GET'])
@permission_classes([AllowAny])
def ConstraintsRquest(request,pk):
    loggeduser_id = ''
    f = open('RestApp/userfile.py', 'r')
    
    if f.mode == 'r':
       loggeduser_id =f.read()
    Userobj = User.objects.get(id=loggeduser_id)
    Teamid = Userobj.Teams.id
    Teamobj = Teams.objects.get(id=Teamid)  
    v_team_name = Teamobj.id
        
    df = dataframerequest(request,pk)
    
    constraints_1 = df[df['Current_Owner_id'] ==v_team_name]['Display_Name_Detailed'].tolist()
    constraints_2 = df[df['Current_Owner_id'] ==v_team_name]['Year'].unique().tolist()
    constraints_3 = df[df['Current_Owner_id'] ==v_team_name]['Draft_Round'].unique().tolist()
    constraints_4 = [0]
    constraints_5 = [99999999]
    constraints_6 = df[df['Current_Owner_id'] !=v_team_name]['Current_Owner_id'].unique().tolist()
    constraints_7 = df[df['Current_Owner_id'] !=v_team_name]['Display_Name_Detailed'].unique().tolist()
    constraints_8 = df[df['Current_Owner_id'] !=v_team_name]['Year'].unique().tolist()
    constraints_9 = df[df['Current_Owner_id'] !=v_team_name]['Draft_Round'].unique().tolist()
    constraints_10 = [0]
    constraints_11 = [99999999]
    constraints_12 = [0.10]
    constraints_13 = [0]
    constraints_14 = [10]
    
    my_dict = {"constraints_1": constraints_1 ,
               "constraints_2": constraints_2,
               "constraints_3": constraints_3,
               "constraints_4": constraints_4,
               'constraints_5':constraints_5,
               'constraints_6':constraints_6,
               'constraints_7':constraints_7,
               'constraints_8':constraints_8,
               'constraints_9':constraints_9,
               'constraints_10':constraints_10,
               'constraints_11':constraints_11,
               'constraints_12':constraints_12,
               'constraints_13':constraints_13,
               'constraints_14':constraints_14,
               } 
    return Response(my_dict, status=status.HTTP_201_CREATED)


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


@api_view(['GET'])
@permission_classes([AllowAny])
def Get_Rounds_Pick(request, pk):

    df = dataframerequest(request,pk)
    
    df['column'] = np.zeros(len(df))
    df['column'].describe()
    df = df[~df.isin([np.nan, np.inf, -np.inf]).any(1)]

    current_date = date.today()

    v_current_year = current_date.year
    v_current_year_plus1 = v_current_year+1
    
    TeamList = []
    imgQuery = Teams.objects.all()
    serializer = ListImageSerializer(
        imgQuery, many=True, context={'request': request})
    data = serializer.data
    for values in data:
        TeamList.append(values['Image'])
        
    Imgdf = pd.DataFrame(TeamList) 
    
    df = pd.concat([Imgdf,df],axis=1).fillna('')
    
    data_current_year_rd1 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD1')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short',0]]

    data_current_year_rd2 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD2')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short',0]]

    data_current_year_rd3 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD3')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_current_year_rd4 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD4')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_current_year_rd5 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD5')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_current_year_rd6 = df[(df.Year.astype(int) == v_current_year) & (df.Draft_Round == 'RD6')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    # Next Year Round by Round:

    data_next_year_rd1 = df[(int(df.Year[0])+1 == v_current_year_plus1) & (df['Draft_Round'] == 'RD1')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_next_year_rd2 = df[(int(df.Year[0])+1 == v_current_year_plus1) & (df.Draft_Round == 'RD2')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_next_year_rd3 = df[(int(df.Year[0])+1 == v_current_year_plus1) & (df['Draft_Round'] == 'RD1')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_next_year_rd4 = df[(int(df.Year[0])+1 == v_current_year_plus1) & (df.Draft_Round == 'RD4')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_next_year_rd5 = df[(int(df.Year[0])+1 == v_current_year_plus1) & (df.Draft_Round == 'RD5')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_next_year_rd6 = df[(int(df.Year[0])+1 == v_current_year_plus1) & (df.Draft_Round == 'RD6')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    # Order of Entry Table

    Teamnames = []
    teamobj = Teams.objects.filter(id=pk).values()
    for teams in teamobj:
        Teamnames.append(teams['TeamNames'])
    data_order_of_entry = df[(int(df.Year[0])+1 == v_current_year_plus1) & (df.Draft_Round == 'RD6')][[
        'TeamName_id', 'Overall_Pick', 'Club_Pick_Number']].sort_values(by='Overall_Pick')

    # data_order_of_entry = pd.crosstab(data_order_of_entry.TeamName_id, data_order_of_entry.Club_Pick_Number, values=data_order_of_entry.Overall_Pick,aggfunc=sum)

    data_order_of_entry.reset_index(drop=True, inplace=True)
    data_order_of_entry_dict = data_order_of_entry.to_dict(orient="index")

    # Draft Assets Graph - Bar Graph

    my_dict = {}
    graph_list = []
    data_draft_assets_graph = df.groupby(['Current_Owner_Short_Name', 'Year'])[
        'AFL_Points_Value'].sum()
    dict = data_draft_assets_graph.items()
    for data in dict:

        my_dict['shortname'] = list(data).pop(0)[0]
        my_dict['Year'] = list(data).pop(0)[1]
        my_dict['AFL_POINTS'] = list(data).pop(1)
        graph_list.append(my_dict)

    ##### Full List of Draft Picks #####

    data_full_masterlist = df[['Year', 'Draft_Round', 'Overall_Pick', 'TeamName_id',
                               'PickType', 'Original_Owner_id', 'Current_Owner_id', 'Previous_Owner_id', 'AFL_Points_Value', 'Club_Pick_Number']]

    dict = data_full_masterlist.items()
    data_full_list = list(dict)
    data_full_masterlist_array = np.array(data_full_list, dtype=object)

    Current_Year_Round = {

        'data_current_year_rd1': data_current_year_rd1,
        'data_current_year_rd2': data_current_year_rd2,
        'data_current_year_rd3': data_current_year_rd3,
        'data_current_year_rd4': data_current_year_rd4,
        'data_current_year_rd5': data_current_year_rd5,
        'data_current_year_rd6': data_current_year_rd6
    }

    Next_Year_Round = {
        'data_next_year_rd1': data_next_year_rd1,
        'data_next_year_rd2': data_next_year_rd2,
        'data_next_year_rd3': data_next_year_rd3,
        'data_next_year_rd4': data_next_year_rd4,
        'data_next_year_rd5': data_next_year_rd5,
        'data_next_year_rd6': data_next_year_rd6
    }

    return Response({'Current_Year_Round': Current_Year_Round, 'Next_Year_Round': Next_Year_Round, 'data_order_of_entry_dict': data_order_of_entry_dict, 'data_full_masterlist_array': data_full_masterlist_array, 'graph_list': graph_list}, status=status.HTTP_201_CREATED)

    
@api_view(['POST'])
@permission_classes([AllowAny])
def MakeCompanyRequest(request):

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
def ProjPlayer(request,format=None):
    serializer = PlayersSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success':'Player has been created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    

#  ########################################  GET Requests ###############################################################


@ api_view(['GET'])
@ permission_classes([AllowAny])
def ProjectDetailsRequest(request, pk):
    project = Project.objects.filter(id=pk).values()
    masterlist = MasterList.objects.filter(projectid=pk).count()

    return Response({'ProjectDetails': project, 'MasterlistCount': masterlist}, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny, ])
def LogoutRequest(self,request):
    if request.session['userId']:
        # url = request.build_absolute_uri()
        request.session['userId'] = 0
        # return HttpResponseRedirect(redirect_to='')
        res = "You have been logged out !"
        raw = open('RestApp/userfile.py', "r+")
        contents = raw.read().split("\n")
        raw.seek(0)                        # <- This is the missing piece
        raw.truncate()
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
        print( data['projectId_id'])
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
    data_dict = MasterList.objects.filter(projectId=pk).values()[
        offset:offset+limit]
    data_count = MasterList.objects.filter(projectId=pk).values().count()
    PagesCount = data_count/20
    Count = math.ceil(PagesCount)
    for masterlistdata in data_dict:
        TeamNamesList = Teams.objects.filter(
            id=masterlistdata['TeamName_id']).values('id', 'TeamNames', 'ShortName')
        NamesWithShortNames = Teams.objects.filter(
            id=masterlistdata['TeamName_id']).values('id', 'TeamNames')
        masterlistdata['TeamName_id'] = TeamNamesList[0].copy()
        masterlistdata['Original_Owner_id'] = NamesWithShortNames[0].copy()
        masterlistdata['Current_Owner_id'] = NamesWithShortNames[0].copy()
        ProjectQuery = Project.objects.filter(
            id=masterlistdata['projectId_id']).values('id', 'project_name')
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
    MasterList.objects.filter(id=pk).delete()
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






