import json
from logging import raiseExceptions
# from mmap import MADV_AUTOSYNC
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from RestApi.settings import SECRET_KEY
from .models import User, LocalLadder
from .serializers import UserSerializer, LocalLaddderSerializer, CreateProjectSerializer, MasterLIstSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.settings import api_settings
from rest_framework.permissions import AllowAny
import jwt
from django.conf import settings
from django.core import serializers
from .models import MasterList, LocalLadder, CreateProject
import json
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt

#  ########################################  POST Requests ###############################################################


class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': 'User Created Successfuly', 'data': serializer.data}, status=status.HTTP_201_CREATED)


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
                token = jwt.encode(
                    {'username': user[0].username}, settings.SECRET_KEY)
                request.session['token'] = token
                user_details = {}
                user_details['user'] = user[0].username
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


@api_view(['GET'])
@permission_classes([AllowAny, ])
def LogoutRequest(request):
    if request.session['userId']:
        url = request.build_absolute_uri()
        request.session['userId'] = 0
        # return HttpResponseRedirect(redirect_to='')
        res = "You have been logged out !"
        return Response(res, status=status.HTTP_403_FORBIDDEN)


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
    return Response({'success': 'LocalLadder Created Successfuly', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def CreateMasterListRequest(request):
    MasterList = request.data
    serializer = MasterLIstSerializer(data=MasterList)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'success': 'MasterList Created Successfuly', 'data': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def UpdateMasterListRequest(request):
    data_dict = request.data
    instance = MasterList.objects.filter().update(**data_dict)
    return Response({"Success": "Data Updated Successfully", "data": instance}, status=status.HTTP_201_CREATED)


#  ########################################  GET Requests ###############################################################

@api_view(['GET'])
@permission_classes([AllowAny, ])
def GETProjectRequest(request):
    data_dict = CreateProject.objects.filter().values()
    return Response(data_dict, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def GETLocalLadderRequest(request):
    data_dict = LocalLadder.objects.filter().values()
    return Response(data_dict, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny, ])
def GETMasterListRequest(request):
    data_dict = MasterList.objects.filter().values()
    return Response(data_dict, status=status.HTTP_201_CREATED)


# ##########################   Delete Api ##########################


@api_view(["DELETE"])
@permission_classes([AllowAny, ]) 
def DeleteMasterListRequest(request, pk):
    instance = MasterList.objects.filter(pk=pk).delete()
    return Response({"Success": "Data Deleted Successfully", "data": instance}, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([AllowAny, ])
def DeleteLocalLadderRequest(self,pk):
    instance = self.get_object(pk)
    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
    # instance = LocalLadder.objects.filter().delete()
    # return Response({"Success": "Data Deleted Successfully", "data": instance}, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([AllowAny, ])
def DeleteProjectRequest(request,pk):
    instance =CreateProject.objects.filter(id=pk).delete()
    return Response({"Success": "Data Deleted Successfully", "data": instance}, status=status.HTTP_201_CREATED)
