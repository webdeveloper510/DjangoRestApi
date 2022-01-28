from rest_framework import serializers
from.models import User


class UserSerializer(serializers.ModelSerializer):

    date_joined = serializers.ReadOnlyField()

    class Meta(object):
        model = User
        fields =  '__all__'