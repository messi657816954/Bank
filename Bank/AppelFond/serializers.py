from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers, fields
from AppelFond.models import User, Tbanque, TappelFonds, TPlafond

############################# philippe ####################################

class banqSerializers(serializers.ModelSerializer):

    class Meta:
        model = Tbanque
        fields = ('nom_banq', 'code_banq', 'code_agence', 'url_core',)




class appelsSerializers(serializers.ModelSerializer):

    class Meta:
        model = TappelFonds
        fields = ('montant', 'date', 'compte_id', 'compte_numero', 'numero_recharge', 'client_id', 'client_nom', 'client_prenom', 'status','banque_id',)



class plafondSerializers(serializers.ModelSerializer):

    class Meta:
        model = TPlafond
        fields = ('montant_max', 'montant_min', 'montant_cumul_max_week', 'montant_cumul_max_month', 'seuil_validation', 'client_id', 'banque_id', 'libelle')






























