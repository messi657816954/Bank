from rest_framework import serializers

class CheckPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)



















