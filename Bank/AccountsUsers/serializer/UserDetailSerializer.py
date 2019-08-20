from rest_framework import serializers
from AppelFond.models import User



class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'phone', 'banque', 'type_plafond']



















