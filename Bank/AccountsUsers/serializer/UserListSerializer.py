from rest_framework import serializers
from AppelFond.models import User



class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']


















