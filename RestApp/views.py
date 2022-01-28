import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from RestApi.settings import SECRET_KEY
from .models import User
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.settings import api_settings
from rest_framework.permissions import AllowAny
import jwt
from django.conf import settings


class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# https://code.tutsplus.com/tutorials/how-to-authenticate-with-jwt-in-django--cms-30460


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
    SECRET_KEY = settings.SECRET_KEY
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    try:
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email, password=password)
        if user:
            try:
                payload = jwt_payload_handler(user[0])
                token = jwt.encode(payload, settings.SECRET_KEY)
                user_details = {}
                user_details['user'] = payload['username']
                user_details['token'] = token
                print(user_details)
                return Response(user_details, status=status.HTTP_200_OK)

            except Exception as e:
                raise e
        else:
            res = {
                'error': 'can not authenticate with the given credentials or the account has been deactivated'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'error': 'please provide a email and a password'}
        return Response(res)
