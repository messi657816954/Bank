from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers, fields
from AppelFond.models import User, Tbanque, TappelFonds, TPlafond

class CostumSerial(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'role', 'password', 'banque']


# class BanqueSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = ('id', 'nom',)
#         model = Tbanque


class UseregisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'},write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username','email','phone','role','password','password2','banque']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self,data):
        pw = data.get('password')
        pw2 = data.get('password2')
        if pw != pw2:
            raise serializers.ValidationError("Passwords must match")
        return data

    def create(self, validated_data):
        banqu_id = validated_data.pop('banque')
        banque = Tbanque.objects.get(nom=banqu_id)
        if banque:
            user_obj = User(
                username=validated_data.get('username'),
                email=validated_data.get('email'),
                phone=validated_data.get('phone'),
                role=validated_data.get('role'),
                banque=banque
            )
            user_obj.set_password(validated_data.get('password'))
            user_obj.save()
            return user_obj

ROLES = (
    ('ADMIN', 'ADMIN'),
    ('CLIENT', 'CLIENT'),
)

class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(required=True)
    phone = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(choices=ROLES)
    banque = serializers.PrimaryKeyRelatedField(queryset=Tbanque.objects.all())

    class Meta:
        model = User
        exclude = ('password1','password2')

    def validate(self, data):
        pass

    def get_cleaned_data(self):
        return {
            'password': self.validated_data.get('password', ''),
            'email': self.validated_data.get('email', ''),
            'username': self.validated_data.get('username', ''),
            'role': self.validated_data.get('role', ''),
            'phone': self.validated_data.get('phone', ''),
            'banque': self.validated_data.get('banque', ''),
        }
    
    def save(self, request):
        return super(CustomRegisterSerializer, self).save(request)




############################# philippe ####################################

class banqSerializers(serializers.ModelSerializer):

    class Meta:
        model = Tbanque
        fields = ('nom_banq', 'code_banq', 'code_agence', 'client_id', 'url_core',)




class appelsSerializers(serializers.ModelSerializer):

    class Meta:
        model = TappelFonds
        fields = ('montant', 'date', 'compte_id', 'compte_numero', 'numero_recharge', 'client_id', 'client_nom', 'client_prenom', 'status',)



class plafondSerializers(serializers.ModelSerializer):

    class Meta:
        model = TPlafond
        fields = ('montant_max', 'montant_min', 'montant_cumul_max_week', 'montant_cumul_max_month', 'seuil_validation',)

































