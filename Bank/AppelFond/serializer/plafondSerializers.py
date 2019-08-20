from rest_framework import serializers, fields

############################# philippe ####################################
from AppelFond.models import TPlafond


class plafondSerializers(serializers.ModelSerializer):

    class Meta:
        model = TPlafond
        fields = ('pk', 'montant_max', 'montant_min', 'montant_cumul_max_week', 'montant_cumul_max_month', 'seuil_validation', 'client_id', 'banque_id', 'libelle')







