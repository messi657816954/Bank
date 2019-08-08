from django.shortcuts import render
# ajout philippe
from rest_framework import serializers, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from . import models  # , users
import requests
import datetime
import calendar
from django.http import Http404

from AppelFond.serializers import banqSerializers, appelsSerializers, plafondSerializers
from django.core.paginator import Paginator


# Create your views here.

##########################  api view banques ######################################
class banqView(APIView):
    # http://localhost:8000/%5Ebanques/?nom_banq=bicec&code_banq=code_bicec&code_agence=code_agence_bicec
    def post(self, request, *args, **kwargs):
        # print('#####################')
        # print(request.query_params)
        if request.query_params:
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

    # http://localhost:8000/%5Ebanques/?page=1
    def get(self, request, *args, **kwargs):
        # print(request.query_params['pk'])
        if 'pk' in request.query_params:
            # http://localhost:8000/%5Ebanques/?page=1/?banq_id=1
            items = models.Tbanque.objects.filter(pk=request.query_params['pk'])
        else:
            # http://localhost:8000/%5Ebanques/?page=1
            items = models.Tbanque.objects.all()
        paginator = Paginator(items, 5)
        page = request.query_params['page']
        items = paginator.get_page(page)
        print(items)
        output_serializer = banqSerializers(items, many=True)
        return Response(output_serializer.data)

    # http://localhost:8000/%5Ebanques/?pk=1
    def delete(self, request, *args, **kwargs):
        # item = models.TPlafond.objects.get(pk=request.query_params['pk'])
        item = self.get_object(request.query_params['pk'])
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return models.Tbanque.objects.get(pk=pk)
        except models.Tbanque.DoesNotExist:
            raise Http404

    # http://localhost:8000/%5Ebanques/?pk=1/
    def put(self, request, *args, **kwargs):
        if 'pk' in request.query_params:
            item = self.get_object(request.query_params['pk'])
            print(request.query_params)
            output_serializer = banqSerializers(instance=item, data=request.query_params, partial=True)
            print(output_serializer)
            output_serializer.is_valid(raise_exception=True)
            if output_serializer.is_valid(raise_exception=True):
                output_serializer.save()
            else:
                print(output_serializer.errors)
                return Response(output_serializer.errors)
        return Response(output_serializer.data)

    ##################################### api view appels de fonds ##################################


class appelsView(APIView):

    def verifPlafondUser(self, instance):
        # VERIFICATION DU PLAFOND
        if instance.client_id:
            plafond_client = models.TPlafond.objects.get(client_id=instance.client_id)
            # plafond_client = self.get_object(data_query['client_id'])
            if instance.montant:
                if float(instance.montant) >= plafond_client.montant_max:
                    instance.status = 'WAIT'
                    instance.save()
                    print('WAIT montant_max')
                    return 'montant_max'
                    # return Response([{
                    #                      'msg': 'votre montant dépasse le max, veuillez patienter un gestionnaire va valider votre requete'}])

                if float(instance.montant) <= plafond_client.montant_min:
                    instance.status = 'CANCEL'
                    instance.save()
                    print('CANCEL')
                    return 'montant_min'
                    # return Response([{'msg': 'vous ne pouvez faire une opération en dessous de %s' % (
                    #     plafond_client.montant_min)}])

                """ ici on recupere les appels de fond de l'utilisateur puis on parcours ses appels de fonds
                si lappel de fond a été effectué dans la meme semaine que celle actuelle on cumule le montant"""
                all_appel = models.TappelFonds.objects.filter(client_id=instance.client_id)
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
                    return 'montant_cumul_max_week'
                    # return Response([{
                    #                      'msg': 'cette demande a fait dépasser le max de la semaine, veuillez patienter un gestionnaire va valider votre requete'
                    #                 }])

                if float(amount_month) >= float(plafond_client.montant_cumul_max_month):
                    instance.status = 'WAIT'
                    instance.save()
                    return 'montant_cumul_max_month'
                    # return Response([{
                    #                      'msg': 'cette demande a fait dépasser le max du mois, veuillez patienter un gestionnaire va valider votre requete'
                    #                 }])

        return ''

    # verification de plafond par banque
    def verifPlafondBank(self, instance):
        # VERIFICATION DU PLAFOND
        if instance.banque_id:
            plafond_client = models.TPlafond.objects.get(banque_id=instance.banque_id)
            if instance.montant:
                if float(instance.montant) >= plafond_client.montant_max:
                    instance.status = 'WAIT'
                    instance.save()
                    print('WAIT montant_max')
                    return 'montant_max'

                if float(instance.montant) <= plafond_client.montant_min:
                    instance.status = 'CANCEL'
                    instance.save()
                    print('CANCEL')
                    return 'montant_min'

                """ ici on recupere les appels de fond de l'utilisateur puis on parcours ses appels de fonds
                si lappel de fond a été effectué dans la meme semaine que celle actuelle on cumule le montant"""
                all_appel = models.TappelFonds.objects.filter(client_id=instance.client_id,
                                                              banque_id=instance.banque_id)
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
                    return 'montant_cumul_max_week'

                if float(amount_month) >= float(plafond_client.montant_cumul_max_month):
                    instance.status = 'WAIT'
                    instance.save()
                    return 'montant_cumul_max_month'

        return ''

    # http://localhost:8000/%5Eappels/?montant=15000&compte_id=1&compte_numero=008036&numero_recharge=697282623&client_id=1&client_nom=iccsoft&client_prenom=phil&status=WAIT
    def post(self, request, *args, **kwargs):
        # cal = calendar.weekday(2019,8,1)
        # week = datetime.date(2019,8,1).isocalendar()
        # print(cal)
        # print(week[1])
        # d = datetime.date(2019,8,1).timetuple()
        # print(d)
        # print(d[1])

        data_query = {
            'montant': request.query_params['montant'],
            'compte_id': request.query_params['compte_id'],
            'compte_numero': request.query_params['compte_numero'],
            'numero_recharge': request.query_params['numero_recharge'],
            'client_id': request.user.id,
            'client_nom': request.user.username,
            'status': 'PROGRESS'
        }

        # print(data_query['client_id'])
        # request.query_params['mongggtant']
        intput_serializer = appelsSerializers(data=data_query)
        intput_serializer.is_valid(raise_exception=True)
        if intput_serializer.is_valid(raise_exception=True):
            #         instance = models.Tbanque.Meta.model(**validated_data)
            # SAUVEGARDE APPEL DE FONDS
            instance = intput_serializer.save()

            # # VERIFICATION DU PLAFOND
            # if data_query['client_id']:
            #     plafond_client = models.TPlafond.objects.get(client_id=data_query['client_id'])
            #     #plafond_client = self.get_object(data_query['client_id'])
            #     if 'montant' in request.query_params:
            #         if float(request.query_params['montant']) >= plafond_client.montant_max:
            #             instance.status = 'WAIT'
            #             instance.save()
            #             print('WAIT')
            #             return Response([{
            #                                  'msg': 'votre montant dépasse le max, veuillez patienter un gestionnaire va valider votre requete'}])

            #         if float(request.query_params['montant']) <= plafond_client.montant_min:
            #             instance.status = 'CANCEL'
            #             instance.save()
            #             print('CANCEL')
            #             return Response([{'msg': 'vous ne pouvez faire une opération en dessous de %s' % (
            #                 plafond_client.montant_min)}])

            #         """ ici on recupere les appels de fond de l'utilisateur puis on parcours ses appels de fonds
            #         si lappel de fond a été effectué dans la meme semaine que celle actuelle on cumule le montant"""
            #         all_appel = models.TappelFonds.objects.filter(client_id=data_query['client_id'])
            #         amount_week = 0
            #         amount_month = 0
            #         for appel in all_appel:
            #             date_appel = appel.date.isocalendar()
            #             date_now = instance.date.isocalendar()
            #             if date_appel[1] == date_now[1]:
            #                 amount_week += appel.montant

            #             """ on parcours les appels de fonds du user 
            #             pour chaque appel de fond si sa date est dans le mois encours
            #             on recupere les montants pour obtenir le cumul du mois 
            #             puis on compare avec le montant max du mois """
            #             date_appel_month = appel.date.timetuple()
            #             date_now_month = instance.date.timetuple()
            #             if date_appel_month[1] == date_now_month[1]:
            #                 amount_month += appel.montant

            #         # print(amount_week)
            #         # print(plafond_client.montant_cumul_max_week)
            #         if float(amount_week) >= float(plafond_client.montant_cumul_max_week):
            #             instance.status = 'WAIT'
            #             instance.save()
            #             return Response([{
            #                                  'msg': 'cette demande a fait dépasser le max de la semaine, veuillez patienter un gestionnaire va valider votre requete'
            #                             }])

            #         # """ on parcours les appels de fonds du user
            #         # pour chaque appel de fond si sa date est dans le mois encours
            #         # on recupere les montants pour obtenir le cumul du mois
            #         # puis on compare avec le montant max du mois """
            #         # amount_month = 0
            #         # for appel_month in all_appel:
            #         #     date_appel_month = appel_month.date.timetuple()
            #         #     date_now_month = instance.date.timetuple()
            #         #     if date_appel_month[1] == date_now_month[1]:
            #         #         amount_month += appel_month.montant
            #         if float(amount_month) >= float(plafond_client.montant_cumul_max_month):
            #             instance.status = 'WAIT'
            #             instance.save()
            #             return Response([{
            #                                  'msg': 'cette demande a fait dépasser le max du mois, veuillez patienter un gestionnaire va valider votre requete'
            #                             }])

            if request.user.type_plafond == 'USER':
                verif = self.verifPlafondUser(instance)
                print(verif)
                if verif == 'montant_max':
                    return Response([{
                        'msg': 'votre montant dépasse le max, veuillez patienter un gestionnaire va valider votre requete'
                    }])
                if verif == 'montant_min':
                    plafond_client = models.TPlafond.objects.get(client_id=instance.client_id)
                    return Response([{
                        'msg': 'vous ne pouvez faire une opération en dessous de %s' % (plafond_client.montant_min)
                    }])
                if verif == 'montant_cumul_max_week':
                    return Response([{
                        'msg': 'cette demande a fait dépasser le max de la semaine, veuillez patienter un gestionnaire va valider votre requete'
                    }])
                if verif == 'montant_cumul_max_month':
                    return Response([{
                        'msg': 'cette demande a fait dépasser le max du mois, veuillez patienter un gestionnaire va valider votre requete'
                    }])
            if request.user.type_plafond == 'BANK':
                verif = self.verifPlafondBank(instance)
                print(verif)
                if verif == 'montant_max':
                    return Response([{
                        'msg': 'votre montant dépasse le max autorisé par la banque, veuillez patienter un gestionnaire va valider votre requete'
                    }])
                if verif == 'montant_min':
                    plafond_client = models.TPlafond.objects.get(banque_id=instance.banq_id)
                    return Response([{
                        'msg': 'Pour cette banque vous ne pouvez faire une opération en dessous de %s' % (
                            plafond_client.montant_min)
                    }])
                if verif == 'montant_cumul_max_week':
                    return Response([{
                        'msg': 'cette demande a fait dépasser le max de la semaine autorisé par cette banque, veuillez patienter un gestionnaire va valider votre requete'
                    }])
                if verif == 'montant_cumul_max_month':
                    return Response([{
                        'msg': 'cette demande a fait dépasser le max du mois autorisé par cette banque, veuillez patienter un gestionnaire va valider votre requete'
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

    # http://localhost:8000/%5Eappels/?page=1
    # ceci doit servire d historique
    def get(self, request, *args, **kwargs):
        # print(request.query_params.get('pk', False))
        items = ''
        if 'page' in request.query_params:
            if request.query_params.get('pk', False) != False:
                # CONSULTER LE STATUS
                # http://localhost:8000/%5Eappels/?page=1/?pk=1
                items = models.TappelFonds.objects.filter(pk=request.query_params['pk'])
            if request.query_params.get('client_id', False) != False:
                # CONSULTER L'HISTORIQUE DES APPELS DE FONDS D'UN CLIENT
                # http://localhost:8000/%5Eappels/?page=1/?client_id=1
                items = models.TappelFonds.objects.filter(client_id=request.query_params['client_id'])
            if request.query_params.get('banque_id', False) != False:
                # CONSULTER L'HISTORIQUE DES APPELS DE FONDS D'UNE BANQUE
                # http://localhost:8000/%5Eappels/?page=1/?banque_id=1
                items = models.TappelFonds.objects.filter(banque_id=request.query_params['banque_id'])
            else:
                # CONSULTER TOUS LES APPELS DE FONDS
                # http://localhost:8000/%5Eappels/?page=1
                items = models.TappelFonds.objects.all()
            print(items)
            paginator = Paginator(items, 5)
            page = request.query_params['page']
            items = paginator.get_page(page)
            print(items)
            output_serializer = appelsSerializers(items, many=True)
        return Response(output_serializer.data)

    # ANNULER/VALIDER LES APPELS DE FONDS
    # http://localhost:8000/%5Eappels/?pk=1/?status='FINISH' ou 'CANCEL'
    def put(self, request, *args, **kwargs):
        if 'pk' in request.query_params:
            if 'status' in request.query_params:
                # item = models.TappelFonds.objects.get(pk=request.query_params['pk'])
                item = self.get_object(request.query_params['pk'])
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
                    return Response(output_serializer.errors)
        return Response(output_serializer.data)

    def delete(self, request, *args, **kwargs):
        # item = models.TPlafond.objects.get(pk=request.query_params['pk'])
        item = self.get_object(request.query_params['pk'])
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return models.TappelFonds.objects.get(pk=pk)
        except models.TappelFonds.DoesNotExist:
            raise Http404


####################################### api view plafond ###################################
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

    # http://localhost:8000/%5Eplafond/?page=1
    def get(self, request, *args, **kwargs):
        # print(request.query_params['pk'])
        if 'page' in request.query_params:
            if 'pk' in request.query_params:
                # http://localhost:8000/%5Eplafond/?page=1/?pk=1
                items = models.TPlafond.objects.filter(pk=request.query_params['pk'])
            else:
                # http://localhost:8000/%5Eplafond/?page=1
                items = models.TPlafond.objects.all()
            paginator = Paginator(items, 5)
            page = request.query_params['page']
            items = paginator.get_page(page)
            output_serializer = plafondSerializers(items, many=True)
        return Response(output_serializer.data)

    def delete(self, request, *args, **kwargs):
        # item = models.TPlafond.objects.get(pk=request.query_params['pk'])
        item = self.get_object(request.query_params['pk'])
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return models.TPlafond.objects.get(pk=pk)
        except models.TPlafond.DoesNotExist:
            raise Http404

    # http://localhost:8000/%5Eplafond/?pk=1/?status='FINISH' ou 'CANCEL'
    def put(self, request, *args, **kwargs):
        if 'pk' in request.query_params:
            item = self.get_object(request.query_params['pk'])

            output_serializer = plafondSerializers(instance=item, data=request.query_params, partial=True)
            output_serializer.is_valid(raise_exception=True)
            if output_serializer.is_valid(raise_exception=True):
                output_serializer.save()
            else:
                print(output_serializer.errors)
                return Response(output_serializer.errors)
        return Response(output_serializer.data)

    ########################## api view des comptes ############################


class comptesView(APIView):
    # http://localhost:8000/%5Ecomptes/
    def get(self, request, *args, **kwargs):
        # print(request.query_params['pk'])
        if 'pk' in request.query_params:
            # http://localhost:8000/%5Ecomptes/?pk=1
            r = requests.get('http://localhost:8000/%5Eplafond/', params={'pk': request.query_params['pk']},
                             auth=('iccsoft', 'Iccsoft2019!'))
            print(r.status_code)  # donne le code reponse

        else:
            # http://localhost:8000/%5Ecomptes/
            r = requests.get('http://localhost:8000/%5Eplafond/', auth=('iccsoft', 'Iccsoft2019!'))
            print(r.status_code)  # donne le code reponse

        return Response(r)


# liste de mes compte
class mescomptesView(APIView):
    # http://localhost:8000/%5Emescomptes/
    def get(self, request, *args, **kwargs):
        if resquest.user:
            r = requests.get('http://localhost:8000/%5Eplafond/', params={'pk': resquest.user.id},
                             auth=('iccsoft', 'Iccsoft2019!'))
            print(r.status_code)

            return Response(r)
        return Response(status=status.HTTP_204_NO_CONTENT)


#################################### liste de mes appels de fonds
class mesappelsView(APIView):
    # http://localhost:8000/%5Emescomptes/
    def get(self, request, *args, **kwargs):
        if request.user:
            items = models.TappelFonds.objects.filter(client_id=request.user.id)
            paginator = Paginator(items, 5)
            page = request.query_params['page']
            items = paginator.get_page(page)
            output_serializer = appelsSerializers(items, many=True)
            return Response(output_serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)


################################### consulter le solde
class soldeView(APIView):
    # http://localhost:8000/%5Emescomptes/
    def get(self, request, *args, **kwargs):
        if resquest.user:
            r = requests.get('http://localhost:8000/%5Eplafond/', params={'pk': resquest.user.id},
                             auth=('iccsoft', 'Iccsoft2019!'))
            print(r.status_code)

            return Response(r)
        return Response(status=status.HTTP_204_NO_CONTENT)