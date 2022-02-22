from ast import Add
from logging import raiseExceptions
from django.http import Http404
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from RestApi.settings import SECRET_KEY
from .serializers import (
    LocalLaddderSerializer,
    CreateProjectSerializer,
    MasterLIstSerializer,
    MakeCompanySerializer,
    AddTeamSerializer,
    TransactionsSerialzer,
    DraftAnalyserSerializer,
    AddTraderSerializer,
    AcademyBidSerializer,
    PriorityPickSerializer,
    ManualTeamSerializer,
    FA_CompansationsSerializer,
    LibraryAFLTeamSerializer,
    PicksTypeSerializer
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import jwt
from django.conf import settings
from .models import (
    AddTeam, MasterList, LocalLadder,
    Project,
    User,
    Company,
    AddTrade,
    ManualTeam,
    FA_Compansations,
    AcademyBid,
    PriorityPick,
    LibraryAFLTeams,
    PicksType
)
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
import pandas as pd

#########################################  POST Requests ###############################################################


class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    # def post(self, request):
    #     C_Name = Company.objects.filter().values('id', 'Name')
    #     user = request.data
    #     serializer = UserSerializer(data=user)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     last_inserted_id = serializer.data['id']
    #     User.objects.filter(id=last_inserted_id).update(uui=unique_id)
    #     return Response({'success': 'User Created Successfuly'}, status=status.HTTP_201_CREATED)


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
    TeamNames = AddTeam.objects.filter(id=fk).values('TeamName')
    NamesDict = {
        "Names": TeamNames
    }
    fk = serializer.data['projectId']
    # ProjectName = Project.objects.filter(id=fk).values('id', 'projectId')
    return Response({'success': 'LocalLadder Created Successfuly', 'data': serializer.data, "NamesDict": NamesDict}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def CreateMasterListRequest(request):
    MasterList = request.data
    serializer = MasterLIstSerializer(data=MasterList)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    Original_OwnerId = serializer.data['Original_Owner']
    Current_OwnerId = serializer.data['Current_Owner']
    Most_Recent_OwnerId = serializer.data['Most_Recent_Owner']
    OriginalOwner = AddTeam.objects.filter(
        id=Original_OwnerId).values('TeamName')
    CurrentOwner = AddTeam.objects.filter(
        id=Current_OwnerId).values('TeamName')
    RecentOwner = AddTeam.objects.filter(
        id=Most_Recent_OwnerId).values('TeamName')
    Names = {
        'OriginalOwner': OriginalOwner,
        'CurrentOwner': CurrentOwner,
        'RecentOwner': RecentOwner
    }
    fk = serializer.data['projectId']
    ProjectName = Project.objects.filter(id=fk).values('id', 'project_name')
    return Response({'success': 'MasterList Created Successfuly', 'data': serializer.data, 'Names': Names, 'Project': ProjectName}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def UpdateMasterListRequest(request):
    data_dict = request.data
    instance = MasterList.objects.filter().update(**data_dict)
    return Response({"Success": "Data Updated Successfully", "data": instance}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def MakeCompanyRequest(request):
    Company_obj = request.data
    serializer = MakeCompanySerializer(data=Company_obj)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    fk = serializer.data['project_id']
    ProjectName = Project.objects.filter(id=fk).values('id', 'project_name')
    return Response({'success': 'Company Created Successfuly', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def AddTeamRequest(request):
    TeamObj = request.data
    serializer = AddTeamSerializer(data=TeamObj)
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
def AcademyBidRequest(request):
    Tran_data = request.data
    serializer = AcademyBidSerializer(data=Tran_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'success': 'Academy Bid created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def PriorityPickRequest(request):
    Tran_data = request.data
    serializer = PriorityPickSerializer(data=Tran_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'success': 'Priority pick created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def ManualTeamRequest(request):
    Tran_data = request.data
    serializer = ManualTeamSerializer(data=Tran_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'success': 'Manual Team created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def FARequest(request):
    Tran_data = request.data
    serializer = FA_CompansationsSerializer(data=Tran_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'success': 'created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)


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
@ permission_classes([AllowAny, ])
def GETMasterListRequest(request):
    data_dict = MasterList.objects.filter().values()
    return Response(data_dict, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def CompanyListRequest(request):
    data_dict = Company.objects.filter().values()
    PorjectNames = Project.objects.filter().values()
    return Response(data_dict, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def UserListRequest(request):
    data_dict = User.objects.filter().values()
    return Response(data_dict, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def TeamRequest(request):
    data_dict = AddTeam.objects.filter().values()
    return Response(data_dict, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def LadderRequest(request):
    TeamId = list()
    TeamName = list()
    positions = list()
    Season = list()
    ProjectId = list()
    ProjectNames = list()
    Ladder = LocalLadder.objects.filter().values()
    if Ladder:
            for Ladders in Ladder:
                positions.append(Ladders['position'])
                Season.append(Ladders['season'])
                TeamId.append(Ladders['teamname_id'])
                ProjectId.append(Ladders['Project_id'])
            TeamDict = AddTeam.objects.filter(id__in=TeamId).values('TeamName')
            for Team in TeamDict:
                TeamName.append(Team['TeamName'])
            ProjectDict = Project.objects.filter( id__in=ProjectId).values()
            for ProjName in ProjectDict:
                ProjectNames.append(ProjName['project_name'])
            df = pd.DataFrame( {'position': positions, 'season': Season, 'teamname': TeamName,'Project':ProjectNames})
            df_html = df.to_html()
            return Response(df_html, status=status.HTTP_200_OK)

    else:
        res = {
                'error': 'No Ladder Created Yet ?'
            }
        return Response(res, status=status.HTTP_403_FORBIDDEN)
        

@ api_view(['GET'])
@ permission_classes([AllowAny])
def ProjectDetailsRequest(request, pk):
    data = Project.objects.filter(id=pk).values()
    return Response(data)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def ShowTeamRequest(request):
    data = AddTeam.objects.filter().values()
    return Response(data)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def LibraryAFLTeamsRequest(request):
    data = LibraryAFLTeams.objects.filter().values()
    return Response(data)


@ api_view(['GET'])
@ permission_classes([AllowAny])
def PicksTypeTeamsRequest(request):
    data = PicksType.objects.filter().values()
    return Response(data)


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
    AddTeam.objects.filter(id=pk).delete()
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


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeleteManualTeamRequest(request, pk):
    ManualTeam.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeleteFARequest(request, pk):
    FA_Compansations.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeletePriorityPickrequest(request, pk):
    PriorityPick.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)


@ api_view(["DELETE"])
@ permission_classes([AllowAny, ])
def DeleteAcadmemyrequest(request, pk):
    AcademyBid.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully"}, status=status.HTTP_200_OK)
