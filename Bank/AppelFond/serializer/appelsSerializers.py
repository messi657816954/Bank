from rest_framework import serializers, fields

############################# philippe ####################################
from AppelFond.models import TappelFonds



class appelsSerializers(serializers.ModelSerializer):

    class Meta:
        model = TappelFonds
        fields = ('pk',
                  'montant',
                  'date',
                  'compte_id',
                  'compte_numero',
                  'numero_recharge',
                  'client_id',
                  'client_nom',
                  'client_prenom',
                  'status',
                  'banque_id',)
