from rest_framework import serializers, fields

############################# philippe ####################################
from AppelFond.models import Tbanque, TappelFonds, TPlafond


class banqSerializers(serializers.ModelSerializer):

    class Meta:
        model = Tbanque
        fields = ('pk', 'nom_banq', 'code_banq', 'code_agence', 'url_core',)
