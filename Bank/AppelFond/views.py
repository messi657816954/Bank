# ajout philippe
from rest_framework import serializers, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from . import models
import requests
import datetime
import calendar

from AppelFond.serializers import banqSerializers, appelsSerializers, plafondSerializers

# Create your views here.

# api view banques
class banqView(APIView):
    # http://localhost:8000/%5Ebanques/?nom_banq=bicec&code_banq=code_bicec&code_agence=code_agence_bicec&client_id=2
    def post(self, request, *args, **kwargs):
        print('#####################')
        print(request.query_params)
        intput_serializer = banqSerializers(data=request.query_params)
        intput_serializer.is_valid(raise_exception=True)
        if intput_serializer.is_valid(raise_exception=True):
            #         instance = models.Tbanque.Meta.model(**validated_data)
            instance = intput_serializer.save()
            output_serializer = banqSerializers(instance)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        # instance = get_object_or_404(models.Tbanque, pk=intput_serializer.data['banq_id'])
        # output_serializer = banqSerializers(instance)

        return Response(output_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # http://localhost:8000/%5Ebanques/
    def get(self, request, *args, **kwargs):
        # print(request.query_params['pk'])
        if request.query_params:
            # http://localhost:8000/%5Ebanques/?banq_id=1
            items = models.Tbanque.objects.filter(pk=request.query_params['pk'])
        else:
            # http://localhost:8000/%5Ebanques/
            items = models.Tbanque.objects.all()

        output_serializer = banqSerializers(items, many=True)
        return Response(output_serializer.data)



# api view appels de fonds
class appelsView(APIView):
    # http://localhost:8000/%5Eappels/?montant=15000&compte_id=1&compte_numero=008036&numero_recharge=697282623&client_id=1&client_nom=iccsoft&client_prenom=phil&status=WAIT
    def post(self, request, *args, **kwargs):
        # cal = calendar.weekday(2019,8,1)
        # week = datetime.date(2019,8,1).isocalendar()
        # print(cal)
        # print(week[1])
        # d = datetime.date(2019,8,1).timetuple()
        # print(d)
        # print(d[1])
        # request.query_params['mongggtant']
        intput_serializer = appelsSerializers(data=request.query_params)
        intput_serializer.is_valid(raise_exception=True)
        if intput_serializer.is_valid(raise_exception=True):
            #         instance = models.Tbanque.Meta.model(**validated_data)
            # SAUVEGARDE APPEL DE FONDS
            instance = intput_serializer.save()

            # VERIFICATION DU PLAFOND
            if 'client_id' in request.query_params:
                plafond_client = models.TPlafond.objects.get(client_id=request.query_params['client_id'])
                if 'montant' in request.query_params:
                    if float(request.query_params['montant']) >= plafond_client.montant_max:
                        instance.status = 'WAIT'
                        instance.save()
                        print('WAIT')
                        return Response([{
                                             'msg': 'votre montant dépasse le max, veuillez patienter un gestionnaire va valider votre requete'}])

                    if float(request.query_params['montant']) <= plafond_client.montant_min:
                        instance.status = 'CANCEL'
                        instance.save()
                        print('CANCEL')
                        return Response([{'msg': 'vous ne pouvez faire une opération en dessous de %s' % (
                            plafond_client.montant_min)}])

                    """ ici on recupere les appels de fond de l'utilisateur puis on parcours ses appels de fonds
                    si lappel de fond a été effectué dans la meme semaine que celle actuelle on cumule le montant"""
                    all_appel = models.TappelFonds.objects.filter(client_id=request.query_params['client_id'])
                    amount_week = 0
                    amount_month = 0
                    for appel in all_appel:
                        date_appel = appel.date.isocalendar()
                        date_now = instance.date.isocalendar()
                        if date_appel[1] == date_now[1]:
                            amount_week += appel.montant

                        """ on parcours les appels de fonds du user 
                        pour chaque appel de fond si sa date est dans le mois encours
                        on recupere les montants pour obtenir le cumul du mois 
                        puis on compare avec le montant max du mois """
                        date_appel_month = appel.date.timetuple()
                        date_now_month = instance.date.timetuple()
                        if date_appel_month[1] == date_now_month[1]:
                            amount_month += appel.montant

                    # print(amount_week)
                    # print(plafond_client.montant_cumul_max_week)
                    if float(amount_week) >= float(plafond_client.montant_cumul_max_week):
                        instance.status = 'WAIT'
                        instance.save()
                        return Response([{
                                             'msg': 'cette demande a fait dépasser le max de la semaine, veuillez patienter un gestionnaire va valider votre requete'
                                        }])

                    # """ on parcours les appels de fonds du user
                    # pour chaque appel de fond si sa date est dans le mois encours
                    # on recupere les montants pour obtenir le cumul du mois
                    # puis on compare avec le montant max du mois """
                    # amount_month = 0
                    # for appel_month in all_appel:
                    #     date_appel_month = appel_month.date.timetuple()
                    #     date_now_month = instance.date.timetuple()
                    #     if date_appel_month[1] == date_now_month[1]:
                    #         amount_month += appel_month.montant
                    if float(amount_month) >= float(plafond_client.montant_cumul_max_month):
                        instance.status = 'WAIT'
                        instance.save()
                        return Response([{
                                             'msg': 'cette demande a fait dépasser le max du mois, veuillez patienter un gestionnaire va valider votre requete'
                                        }])

            # ENVOI LAPPEL DE FONDS AU CORE ELOGE
            # r = requests.get('url', auth=('iccsoft', 'Iccsoft2019!'))
            # print(r.status_code) #donne le code reponse

            # CHANGEMENT DU STATUS SELON LA REPONSE
            # if r.status_code = 200:
            #     instance.status = 'FINISH'
            #     instance.save()

            output_serializer = appelsSerializers(instance)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        return Response(output_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # http://localhost:8000/%5Eappels/
    # ceci doit servire d historique
    def get(self, request, *args, **kwargs):
        # print(request.query_params.get('pk', False))
        if request.query_params:
            if request.query_params.get('pk', False) != False:
                # CONSULTER LE STATUS
                # http://localhost:8000/%5Eappels/?pk=1
                items = models.TappelFonds.objects.filter(pk=request.query_params['pk'])
            if request.query_params.get('client_id', False) != False:
                # CONSULTER L'HISTORIQUE DES APPELS DE FONDS D'UN CLIENT
                # http://localhost:8000/%5Eappels/?client_id=1
                items = models.TappelFonds.objects.filter(client_id=request.query_params['client_id'])
        else:
            # CONSULTER TOUS LES APPELS DE FONDS
            # http://localhost:8000/%5Eappels/
            items = models.TappelFonds.objects.all()

        output_serializer = appelsSerializers(items, many=True)
        return Response(output_serializer.data)

    # ANNULER/VALIDER LES APPELS DE FONDS
    # http://localhost:8000/%5Eappels/?pk=1/?status='FINISH' ou 'CANCEL'
    def put(self, request, *args, **kwargs):
        if 'pk' in request.query_params:
            if 'status' in request.query_params:
                item = models.TappelFonds.objects.get(pk=request.query_params['pk'])
                item.status = request.query_params['status']

                output_serializer = appelsSerializers(instance=item, data=request.data, partial=True)
                output_serializer.is_valid(raise_exception=True)
                print(output_serializer.is_valid(raise_exception=True))
                if output_serializer.is_valid(raise_exception=True):

                    output_serializer.save()
                    # SI CEST VALIDER ON CONTACTE LE CORE
                    print(item.status)
                    if item.status == "FINISH":
                        pass
                        # ENVOI LAPPEL DE FONDS AU CORE ELOGE
                        # r = requests.get('url', auth=('iccsoft', 'Iccsoft2019!'))
                        # print(r.status_code) #donne le code reponse

                        # CHANGEMENT DU STATUS SELON LA REPONSE
                        # if r.status_code = 200:
                        #     instance.status = 'FINISH'
                        #     instance.save()
                    if item.status == "CANCEL":
                        return Response([{'msg': 'la requete a été annulée'}])

                else:
                    print(output_serializer.errors)
        return Response(output_serializer.data)


# api view plafond
class plafondView(APIView):
    # http://localhost:8000/%5Eplafond/?montant_max=100000&montant_min=25&seuil_validation=200000
    def post(self, request, *args, **kwargs):
        print('#####################')
        print(request.query_params)
        intput_serializer = plafondSerializers(data=request.query_params)
        intput_serializer.is_valid(raise_exception=True)
        if intput_serializer.is_valid(raise_exception=True):
            #         instance = models.Tbanque.Meta.model(**validated_data)
            instance = intput_serializer.save()
            output_serializer = plafondSerializers(instance)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        return Response(output_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # http://localhost:8000/%5Eappels/
    def get(self, request, *args, **kwargs):
        # print(request.query_params['pk'])
        if request.query_params:
            # http://localhost:8000/%5Eplafond/?pk=1
            items = models.TPlafond.objects.filter(pk=request.query_params['pk'])
        else:
            # http://localhost:8000/%5Eplafond/
            items = models.TPlafond.objects.all()

        output_serializer = plafondSerializers(items, many=True)
        return Response(output_serializer.data)

