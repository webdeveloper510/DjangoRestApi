from array import array
from ast import Add
from dataclasses import replace
from distutils.command.config import dump_file
from doctest import master
# from locale import D_T_FMT
from logging import raiseExceptions
from re import T
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
    ListImageSerializer
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
from collections import defaultdict
from django.core.files import File


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 500)

#########################################  POST Requests ###############################################################

unique_id = uuid.uuid4().hex[:6].upper()
logged_user = ''

def getuser(userid):
    logged_user = userid
    print(userid)

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
                getuser(user[0].id)
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
    serializer.save()
    fk = serializer.data['teamname']
    TeamNames = Teams.objects.filter(id=fk).values('TeamNames')
    NamesDict = {
        "Names": TeamNames
    }
    fk = serializer.data['projectId']
    ProjectId = Project.objects.filter(id=fk).values('id', 'project_name')
    return Response({'success': 'LocalLadder Created Successfuly', 'data': serializer.data, "NamesDict": NamesDict, 'Projectid': ProjectId}, status=status.HTTP_201_CREATED)


def import_ladder_dragdrop(library_team_dropdown_list, library_AFL_Team_Names, v_current_year, v_current_year_plus1):

    ladder_current_year = pd.DataFrame(
        library_team_dropdown_list, columns=['TeamName'])

    ladder_current_year['Position'] = np.arange(len(ladder_current_year)) + 1

    ladder_current_year['Year'] = v_current_year

    ladder_current_year = ladder_current_year[['TeamName', 'Year', 'Position']]

    ladder_current_year_plus1 = ladder_current_year.copy()

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
        projectId=pId

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

    picks_trading_out_team1 = picks_trading_out_team1_obj[0]['value']
    # picks_trading_out_team1 = picks_trading_out_team1_obj

    # players_trading_out_team1_no = data['Team1_Players_no']
    players_trading_out_team1 = data['Team1_players'] or ''
    picks_trading_out_team2_obj = data['Team2_Pick2']
    picks_trading_out_team2 = picks_trading_out_team2_obj[0]['value']
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

    trade_dict = {Teamid1: team1_out, Teamid2: team2_out}

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
        id=picks_trading_out_team2[0]['value'])

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
        Transaction_Details=trade_dict,
        Transaction_Description=trade_description,
        projectId=pId

    )

    pk = Transactions.objects.latest('id')
    row_count = Transactions.objects.filter().count()
    Transactions.objects.filter(id=pk.id).update(Transaction_Number=row_count)

    return Response({'success': 'Trade and Trasactions Created'}, status=status.HTTP_201_CREATED)


def update_masterlist(df):
    library_AFL_Draft_Pointss = []
    library_AFL_Team_Names = []

    Team = Teams.objects.filter().values('id', 'TeamNames', 'ShortName')
    for teamdata in Team:
        library_AFL_Team_Names.append(teamdata['id'])

    PointsQueryset = library_AFL_Draft_Points.objects.filter().values('points')

    for pointss in list(PointsQueryset):

        library_AFL_Draft_Pointss.append(pointss['points'])

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
                df['Previous_Owner'] = previous_owner
                team = Teams.objects.get(id=updaterow.TeamName)
                row1['TeamName'] = team
                row1['Original_Owner'] = Original_Owner
                row1['Current_Owner'] = Current_Ownerr
                row1['projectid'] = Project1
                # row1['Overall_Pick'] = Overall_pickk

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

    df_list = []
    pp_round = ''

    project_Id = data['projectId']
    pp_insert_instructions = data['pp_insert_instructions']

    MasterListobj = MasterList.objects.filter(id=Idd).values()

    pp_team_id = MasterListobj[0]['id']
    ppid = MasterListobj[0]['Display_Name_Detailed']

    for teamsid in MasterListobj:
        pp_team.append(teamsid['TeamName_id'])

    Pickobj = MasterList.objects.filter(id=pp_id).values()
    pp_aligned_pick = Pickobj[0]['Display_Name_Detailed']

    for picks in Pickobj:
        arr.append(picks)
    df_queryset = MasterList.objects.filter(projectid_id=project_Id).values()
    for df_data in df_queryset:
        df_list.append(df_data)
    df = pd.DataFrame(df_list)

    pp_pick_type_re = PicksType.objects.filter(
        pickType=p_type).values('id', 'pickType')

    pp_pick_type = pp_pick_type_re[0]['pickType']
    df = pd.DataFrame(arr)
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

        pp_description = str(pp_team) + 'received a ' + \
            str(pp_pick_type) + ' Priority Pick'

        pp_dict['pp_team'] = [pp_pick_type]
        pp_dict['pp_team'] = [pp_pick_type, reason]
        pp_description = str(pp_team) + 'received a ' + \
            str(pp_pick_type) + ' Priority Pick'

        MasterList.objects.filter(id=rowno+1).update(**df)

    # df1 = pd.DataFrame(df)

    if pp_pick_type == 'First Round':


        Pickobj = MasterList.objects.filter(
            Display_Name_Detailed=ppid).values()
        # print(Pickobj)

        rowno = df.id[df['Display_Name_Detailed'] == pp_aligned_pick][0]

        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName_id': pp_team_id, 'PickType': 'Priority', 'Original_Owner_id': pp_team_id, 'Current_Owner_id': pp_team_id,
                             'Previous_Owner': '', 'Draft_Round': pp_round,
                             'Pick_Group': str(v_current_year) + '-' + 'RD1-Priority-' + pp_pick_type},
                            index=[rowno])

        if pp_insert_instructions == 'Before':

            df = pd.concat([df.loc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)

            df = df.iloc[1]

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
            df = df.iloc[1]
            df['id'] = rowno
            df['Previous_Owner_id'] = ''
            df['projectid_id'] = project_Id
            del df['Previous_Owner']

            MasterList(**df).save()

    if pp_pick_type == 'End of First Round':
        pp_dict = {}
        arr = []

        rowno = df.index[df.Unique_Pick_ID.str.contains(
            str(v_current_year) + '-RD1-Standard')][-1]

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

        df['id'] = rowno+1
        df['Original_Owner_id'] = Idd
        df['Current_Owner_id'] = Idd
        df['TeamName_id'] = Idd
        df['Previous_Owner_id'] = ''
        df['projectid_id'] = project_Id

        pp_dict['pp_team'] = [pp_pick_type]
        pp_description = str(pp_team) + ' received a ' + \
            str(pp_pick_type) + ' Priority Pick'

        MasterList.objects.filter(id=rowno+1).update(**df)

    if pp_pick_type == 'Start of Second Round':
        pp_dict = {}
        arr = []

        rowno = df.id[df.Unique_Pick_ID.str.contains(str(v_current_year) + '-RD2-Standard')][0]

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

        df['id'] = rowno
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

        Pickobj = MasterList.objects.filter(
            Display_Name_Detailed=ppid).values()

        # for picks in Pickobj:
        #     pp_aligned_pick.append(picks['Display_Name_Detailed'])
        #     pp_aligned_pick.append(picks['id'])
        rowno = df.id[df['Display_Name_Detailed'] == pp_aligned_pick][0]

        # rowno = pp_aligned_pick[1]
 
        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority', 'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id,
                             'Previous_Owner': '', 'Draft_Round': pp_round,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type},
                            index=[rowno])

        if pp_insert_instructions == 'Before':
            pp_dic = {}
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[1]
   
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
            df = df.iloc[1]
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

            MasterList(**df).save()
            pp_dict['pp_team'] = [pp_pick_type, pp_round,
                                  pp_aligned_pick, pp_insert_instructions]
            pp_description = str(pp_team) + ' received a ' + \
                str(pp_pick_type) + ' Priority Pick'

    if pp_pick_type == 'End of Second Round':
        arr = []
        pp_dict = {}
        obj = MasterList.objects.filter().values()
        for data in obj:
            arr.append(data)
        df = pd.DataFrame(arr)

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

    if pp_pick_type == 'Third Round':
        pp_dict = {}

        rowno = df.id[df['Display_Name_Detailed'] == pp_aligned_pick][0]
 


        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority', 'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id,
                             'Previous_Owner': '', 'Draft_Round': pp_round,
                             'Pick_Group': str(v_current_year) + '-' + 'RD2-Priority-' + pp_pick_type},
                            index=[rowno])
        if pp_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)
            df = df.iloc[1]

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
            df = df.iloc[1]
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
            MasterList(**df).save()
            pp_dict['pp_team'] = [pp_pick_type, pp_round,
                                  pp_aligned_pick, pp_insert_instructions]
            pp_description = str(pp_team) + ' received a ' + \
                str(pp_pick_type) + ' Priority Pick'

    if pp_pick_type == 'Custom Fixed Position':
        pp_dict = {}

        rowno = df.id[df['Display_Name_Detailed'] == pp_aligned_pick][0]
  

        line = pd.DataFrame({'Position': df.loc[df.TeamName_id == pp_team_id, 'Position'].iloc[0], 'Year': v_current_year,
                             'TeamName': pp_team_id, 'PickType': 'Priority', 'Original_Owner': pp_team_id, 'Current_Owner': pp_team_id,
                             'Previous_Owner': '', 'Draft_Round': 'RD3',
                             'Pick_Group': str(v_current_year) + '-' + pp_round + '-Priority-' + pp_pick_type},
                            index=[rowno])

        if pp_insert_instructions == 'Before':
            df = pd.concat([df.iloc[:rowno], line, df.iloc[rowno:]]
                           ).reset_index(drop=True)

            df = df.iloc[1]
 

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
            df = pd.concat([df.iloc[:rowno + 1], line,
                           df.iloc[rowno + 1:]]).reset_index(drop=True)
            df = df.iloc[1]
            del df['TeamName']
            del df['Current_Owner']
            del df['Previous_Owner']
            del df['Original_Owner']

            df['id'] = rowno
            df['Original_Owner_id'] = Idd
            df['Previous_Owner_id'] = Idd
            df['Current_Owner_id'] = Idd
            df['TeamName_id'] = Idd
            df['projectid_id'] = project_Id

            MasterList(**df).save()
    pp_dict = {}

    new_df = []
    Queryset = MasterList.objects.filter(projectid_id=project_Id).values()
    for picks in Queryset:
        new_df.append(picks)
    df1 = pd.DataFrame(new_df)
    df1.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    df1.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    df1.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)

    # updatedf = update_masterlist(df1)
    df1.reset_index()


    # MasterList.objects.filter(projectid=project_Id).delete()


    for index, updaterow in df1.iterrows():
        row1 = dict(updaterow)

        Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
        Current_Ownerr = Teams.objects.get(id=updaterow.Current_Owner)
        previous_owner = Teams.objects.get(id=updaterow.Current_Owner)
        team = Teams.objects.get(id=updaterow.TeamName)

        Overall_pickk = row1['Overall_Pick']
        Project1 = Project.objects.get(id=project_Id)

        row1['TeamName'] = team
        row1['Original_Owner'] = Original_Owner
        row1['Current_Owner'] = Current_Ownerr
        row1['projectid'] = Project1

        row1['Display_Name'] = str(Current_Ownerr.TeamNames)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner.TeamNames != Current_Ownerr.TeamNames else Current_Ownerr.TeamNames

        row1['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
            updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(row1['Display_Name'])

        # row1['Display_Name_Mini'] = str(Overall_pickk)+  '  ' + Current_Ownerr +  ' (Origin: '+ Original_Owner +  ', Via: ' + \
        #     previous_owner + team.ShortName + \
        #     ')' if Original_Owner != Current_Ownerr else team.ShortName

        # row1['Display_Name_Mini'] = str(Overall_pickk)+'(o:'+team.ShortNames+' , Via:' + \
        #     None + ')' if Original_Owner != Current_Ownerr else df['Current_Owner'].map(lambda x: team.ShortName)

        row1['Display_Name'] = str(Current_Ownerr.TeamNames)+' (Origin: '+team.TeamNames+', Via: ' + \
            None + ')' if Original_Owner.TeamNames != Current_Ownerr.TeamNames else Current_Ownerr.TeamNames
        row1['Display_Name_Short'] = str(Overall_pickk) + '  ' + Current_Ownerr.TeamNames + ' (Origin: ' + Original_Owner.TeamNames + ', Via: ' + \
            previous_owner.TeamNames + team.ShortName + \
            ')' if Original_Owner.TeamNames != Current_Ownerr.TeamNames else team.ShortName

        row1['Current_Owner_Short_Name'] = str(Overall_pickk) + '  ' + Current_Ownerr.TeamNames + ' (Origin: ' + Original_Owner.TeamNames + ', Via: ' + \
            previous_owner.TeamNames + team.ShortName + \
            ')' if Original_Owner.TeamNames != Current_Ownerr.TeamNames else team.ShortName

        MasterList(**row1).save()

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


print(logged_user)


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

    Masterlist = []
    QueryObj =  MasterList.objects.filter(projectid_id=pk).values()
    for data in QueryObj:
        Masterlist.append(data)
        df = pd.DataFrame(Masterlist)
    c1_dropdown = df[df['Current_Owner_id'] ==v_team_name]['Display_Name_Detailed'].tolist()
    c2_dropdown = df[df['Current_Owner_id'] ==v_team_name]['Year'].unique().tolist()
    c3_dropdown = df[df['Current_Owner_id'] ==v_team_name]['Draft_Round'].unique().tolist()
    c4_set = 0
    c5_set = 99999999
    c6_dropdown = df[df['Current_Owner_id'] !=v_team_name]['Current_Owner_id'].unique().tolist()
    c7_dropdown = df[df['Current_Owner_id'] !=v_team_name]['Display_Name_Detailed'].unique().tolist()
    c8_dropdown = df[df['Current_Owner_id'] !=v_team_name]['Year'].unique().tolist()
    c9_dropdown = df[df['Current_Owner_id'] !=v_team_name]['Draft_Round'].unique().tolist()
    c10_set = 0
    c11_set = 99999999
    c12_set = 0.10

    c_dict = {}
    c_dict['c1_dropdown'] = c1_dropdown
    c_dict['c2_dropdown'] = c2_dropdown
    c_dict['c3_dropdown'] = c3_dropdown
    c_dict['c4_set'] = c4_set
    c_dict['c5_set'] = c5_set
    c_dict['c6_dropdown'] = c6_dropdown
    c_dict['c7_dropdown'] = c7_dropdown
    c_dict['c8_dropdown'] = c8_dropdown
    c_dict['c9_dropdown'] = c9_dropdown
    c_dict['c10_set'] = c10_set
    c_dict['c11_set'] = c11_set
    c_dict['c12_set'] = c12_set
   
    return Response({'constraints-data': c_dict}, status=status.HTTP_201_CREATED)


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

    df_list = []

    newdf_data = MasterList.objects.filter(projectid=pk).values()

    for new_df in newdf_data:
        df_list.append(new_df)
    df = pd.DataFrame(df_list)
    df['column'] = np.zeros(len(df))
    df['column'].describe()
    df = df[~df.isin([np.nan, np.inf, -np.inf]).any(1)]

    current_date = date.today()

    v_current_year = current_date.year
    v_current_year_plus1 = v_current_year+1

    data_current_year_rd1 = df[(int(df.Year[0]) == v_current_year) & (df.Draft_Round == 'RD1')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_current_year_rd2 = df[(int(df.Year[0]) == v_current_year) & (df.Draft_Round == 'RD2')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_current_year_rd3 = df[(int(df.Year[0]) == v_current_year) & (df.Draft_Round == 'RD3')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_current_year_rd4 = df[(int(df.Year[0]) == v_current_year) & (df.Draft_Round == 'RD4')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_current_year_rd5 = df[(int(df.Year[0]) == v_current_year) & (df.Draft_Round == 'RD5')][[
        'Draft_Round', 'Overall_Pick', 'Display_Name_Short']]

    data_current_year_rd6 = df[(int(df.Year[0]) == v_current_year) & (df.Draft_Round == 'RD6')][[
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
def AcademyBidRequest(request, pk):
    masterlist = []
    dfobj = MasterList.objects.filter(projectid=pk).values()
    for df_data in dfobj:
        masterlist.append(df_data)
    df = pd.DataFrame(masterlist)

    df.rename(columns={'Original_Owner_id': 'Original_Owner'}, inplace=True)
    df.rename(columns={'Current_Owner_id': 'Current_Owner'}, inplace=True)
    df.rename(columns={'TeamName_id': 'TeamName'}, inplace=True)

    data = request.data
    academy_player = data['player']

    teamid = data['team']
    teamQurerySet = Teams.objects.filter(TeamName=teamid).values('TeamNames')
    academy_team = teamQurerySet[0]['TeamNames']

    academy_pick_type = 'Academy Bid Match'
    pick_id = data['pickid']
    PickQueryset = MasterList.objects.filter(
        id=pick_id).values('Display_Name_Detailed')
    academy_bid = PickQueryset[0]['Display_Name_Detailed']
    academy_pts_value = df.loc[df.Display_Name_Detailed ==
                               academy_bid, 'AFL_Points_Value'].iloc[0]
    academy_bid_round = df.loc[df.Display_Name_Detailed ==
                               academy_bid, 'Draft_Round'].iloc[0]
    # academy_bid_round_int = df.loc[df.Display_Name_Detailed == academy_bid, 'Draft_Round_Int'].iloc[0]
    academy_bid_team = df.loc[df.Display_Name_Detailed ==
                              academy_bid, 'Current_Owner'].iloc[0]
    academy_bid_pick_no = df.loc[df.Display_Name_Detailed ==
                                 academy_bid, 'Overall_Pick'].iloc[0]
    sum_line1 = academy_bid_team + ' have placed a bid on a ' + academy_team + \
        ' academy player at pick ' + academy_bid_pick_no + ' in ' + academy_bid_round
    print(sum_line1)


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

#  ########################################  GET Requests ###############################################################


@ api_view(['GET'])
@ permission_classes([AllowAny])
def ProjectDetailsRequest(request, pk):
    project = Project.objects.filter(id=pk).values()
    masterlist = MasterList.objects.filter(projectid=pk).count()
    print("masterlist", masterlist)

    return Response({'ProjectDetails': project, 'MasterlistCount': masterlist}, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny, ])
def LogoutRequest(request):
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
    return Response(CompanyList, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def UserListRequest(request):
    data_dict = User.objects.filter().values()
    return Response(data_dict, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def TeamRequest(request):
    data_dict = Teams.objects.filter().values()
    return Response(data_dict, status=status.HTTP_200_OK)


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

    Pick1dict = MasterList.objects.filter(Display_Name=TeamName).values(
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

    imgobj = Teams.objects.all()

    serializer = ListImageSerializer(
        imgobj, many=True, context={'request': request})
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
