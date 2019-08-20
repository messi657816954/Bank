from rest_framework import serializers
from AppelFond.models import User



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128,min_length=8,write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password','role','phone','banque','type_plafond'] # 'token',
        read_only_fields = ('token',)

