from ast import Add
from doctest import master
from logging import raiseExceptions
from re import T
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
    AddTraderSerializer,
    UserSerializer,
    TeamSerializer
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import jwt
from django.conf import settings
from .models import (
    MasterList,
    LocalLadder,
    Project,
    User,
    Company,
    AddTrade,
    Teams,
    PicksType,
    library_AFL_Draft_Points
)
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
import pandas as pd
import uuid
from pandas.io import sql
# import MySQLdb
# import pymysql
# from sqlalchemy import create_engine
from datetime import date
import numpy as np
import math
from rest_framework.parsers import JSONParser
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


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
    # superusers_emails = User.objects.filter(is_superuser=True)

    try:
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email, password=password)
        if user:
            request.session['userId'] = user[0].id
            try:
                token = jwt.encode({'unique_Id': user[0].uui}, SECRET_KEY)
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                print(payload)
                request.session['token'] = token
                user_details = {}
                user_details['username'] = user[0].username
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
@permission_classes([AllowAny, ])
def ProjNameDescRequest(request):
    Projectdata = request.data
    serializer = CreateProjectSerializer(data=Projectdata)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'success': 'Project Created Successfuly', 'data': serializer.data}, status=status.HTTP_201_CREATED)


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


def update_masterlist(df):

    library_AFL_Draft_Pointss = []

    PointsQueryset = library_AFL_Draft_Points.objects.filter().values('points')

    for pointss in list(PointsQueryset):

        library_AFL_Draft_Pointss.append(pointss['points'])


    overalllist = df.groupby(['Year'])
    df['Overall_Pick'] = len(list(overalllist['Year']))+1

    ss = enumerate(library_AFL_Draft_Pointss)
    library_AFL_Draf = dict(ss)
    df['AFL_Points_Value'] = df['Overall_Pick'].map(library_AFL_Draf).fillna(0)

    df['Unique_Pick_ID'] = df['Year'].astype(str) + '-' + df['Draft_Round'].astype(
        str) + '-' + df['PickType'].astype(str) + '-' + df['Original_Owner'].astype(str)

    df['Club_Pick_Number'] = df.groupby( ['Year', 'Current_Owner']).cumcount() + 1
    df['Display_Name'] = df['Current_Owner']
    df['Display_Name_Detailed'] = df['Current_Owner']

    return df


@api_view(['GET'])
@permission_classes([AllowAny, ])
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
    ProjectInMasterlist = list()
    MasterListdict = MasterList.objects.filter(projectId=pk).values()

    for MasterProjdata in MasterListdict:
        ProjectInMasterlist.append(MasterProjdata['projectId_id'])

    if ProjectInMasterlist == []:
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
            df['projectId'] = pk
            # for index, row in df.iterrows():
            #     row1 = dict(row)
            #     team = Teams.objects.get(id=row.TeamName)
            #     Original_Owner = Teams.objects.get(id=row.Original_Owner)
            #     Current_Owner = Teams.objects.get(id=row.Current_Owner)

            #     Project1 = Project.objects.get(id=row.projectId)

            #     team = Teams.objects.get(id=row.TeamName)
            #     row1['TeamName'] = team
            #     row1['Original_Owner'] = Original_Owner
            #     row1['Current_Owner'] = Current_Owner
            #     row1['projectId'] = Project1
            #     MasterList(**row1).save()
            #     MasterList.objects.filter(projectId=pk).delete()

            udpatedf = update_masterlist(df)

            for index, updaterow in udpatedf.iterrows():
                row1 = dict(updaterow)
                team = Teams.objects.get(id=updaterow.TeamName)
                Original_Owner = Teams.objects.get(id=updaterow.Original_Owner)
                Current_Owner = Teams.objects.get(id=updaterow.Current_Owner)

                Project1 = Project.objects.get(id=updaterow.projectId)

                team = Teams.objects.get(id=updaterow.TeamName)
                print(team.TeamNames)
                row1['TeamName'] = team
                row1['Original_Owner'] = Original_Owner
                row1['Current_Owner'] = Current_Owner
                row1['projectId'] = Project1
                row1['Display_Name'] = str(Current_Owner)+' (Origin: '+team.TeamNames+', Via: ' + \
                    None + ')' if Original_Owner != Current_Owner else Current_Owner.TeamNames
                row1['Display_Name_Detailed'] = str(v_current_year) + '-' + str(
                    updaterow.Draft_Round) + '-Pick' + str(updaterow.Overall_Pick) + '-' + str(row1['Display_Name'])
                MasterList(**row1).save()
            return Response({'success': 'MasterList Created Successfuly', 'data': df}, status=status.HTTP_201_CREATED)

        except Exception as e:

            raise e

    else:
        return Response({'error': 'Masterlist with same project is already exist'}, status=status.HTTP_208_ALREADY_REPORTED)


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
def TransactionsRequest(request):
    Tran_data = request.data
    serializer = TransactionsSerialzer(data=Tran_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'success': 'Transaction created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def AddTradeRequest(request):
    Tran_data = request.data
    serializer = AddTraderSerializer(data=Tran_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'success': 'Trade created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)




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
    masterlist = MasterList.objects.filter(projectId=pk).count()
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
    return Response(LadderList, status=status.HTTP_200_OK)


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
    data = Teams.objects.filter().values()
    return Response(data)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def PicksTypeTeamsRequest(request):
    data = PicksType.objects.filter().values()
    return Response(data)


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
    AddTrade.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)
