from django.shortcuts import render
# ajout philippe
from rest_framework import serializers, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from AppelFond.models import TappelFonds
from . import models  # , users
import requests
import datetime
import calendar
from django.http import Http404

from AppelFond.serializer.banqSerializers import banqSerializers
from AppelFond.serializer.appelsSerializers import appelsSerializers
from AppelFond.serializer.plafondSerializers import plafondSerializers
from django.core.paginator import Paginator
from Configurations.utils import API_MSG_CODE_CREAT_BANK, reponses_generale, USER, BANK
from django.contrib.auth.models import User
import socket
from AppelFond.SocketHandler import SocketHandler
import json


# Create your views here.

##########################  api view banques ######################################
class banqView(APIView):
    # http://localhost:8000/%5Ebanques/?nom_banq=bicec&code_banq=code_bicec&code_agence=code_agence_bicec
    def post(self, request, *args, **kwargs):
        # print('#####################')
        # print(request.query_params)
        print(request.user.is_authenticated)
        if request.user.is_authenticated:
            if request.query_params:
                intput_serializer = banqSerializers(data=request.query_params)
                intput_serializer.is_valid(raise_exception=True)
                # return Response(intput_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                if intput_serializer.is_valid(raise_exception=True):
                    #         instance = models.Tbanque.Meta.model(**validated_data)
                    instance = intput_serializer.save()
                    output_serializer = banqSerializers(instance)
                    res = reponses_generale(msg_code='MG0022', sucess=1, results=output_serializer.data)
                    return Response(res)
                # instance = get_object_or_404(models.Tbanque, pk=intput_serializer.data['banq_id'])
                # output_serializer = banqSerializers(instance)
                else:
                    return Response(intput_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    res = reponses_generale(msg_code='MG000', sucess=0, results=intput_serializer.errors,error_code='invalid', error_msg='les données sont invalide')
                    return Response(res)
            else:
                res = reponses_generale(msg_code='MG000', sucess=0, results=status.HTTP_400_BAD_REQUEST,
                                        error_code='invalid', error_msg="vous n'avez rien saisi")
                return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)
        # return Response([{'error_code': 2, 'content': {'msg': 'vous devez vous authentifier'}}], status=status.HTTP_400_BAD_REQUEST)

    # http://localhost:8000/%5Ebanques/?page=1
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # print(request.query_params['pk'])
            if 'pk' in request.query_params:
                # http://localhost:8000/%5Ebanques/?page=1/?banq_id=1
                items = models.Tbanque.objects.filter(pk=request.query_params['pk'])
            elif 'pk' not in request.query_params:
                # http://localhost:8000/%5Ebanques/?page=1
                items = models.Tbanque.objects.all()
            paginator = Paginator(items, 5)
            page = request.query_params['page']
            items = paginator.get_page(page)
            print(items)
            output_serializer = banqSerializers(items, many=True)
            counts = paginator.num_pages
            res_pages = {'total_page': counts, "content": output_serializer.data}
            res = reponses_generale(msg_code='MG0021', sucess=1, results=res_pages)
            return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

        # http://localhost:8000/%5Ebanques/?pk=1

    # def delete(self, request, *args, **kwargs):
    #     #item = models.TPlafond.objects.get(pk=request.query_params['pk'])
    #     item = self.get_object(request.query_params['pk'])
    #     item.delete()
    #     return Response(status= status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return models.Tbanque.objects.get(pk=pk)
        except models.Tbanque.DoesNotExist:
            raise Http404

    # http://localhost:8000/%5Ebanques/?pk=1/
    def put(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if 'pk' in request.query_params:
                item = self.get_object(request.query_params['pk'])
                output_serializer = banqSerializers(instance=item, data=request.query_params, partial=True)
                output_serializer.is_valid(raise_exception=True)
                if output_serializer.is_valid(raise_exception=True):
                    output_serializer.save()
                    res = reponses_generale(msg_code='MG0023', sucess=1, results=output_serializer.data)
                    return Response(res)
                else:
                    res = reponses_generale(msg_code='MG000', sucess=0, results=output_serializer.errors,
                                            error_code='invalid', error_msg="données invalide")
                    return Response(res)
            else:
                res = reponses_generale(msg_code='MG000', sucess=0, results=output_serializer.errors,
                                        error_code='invalid', error_msg="le pk est invalide")
                return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

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
                if float(instance.montant) <= plafond_client.montant_min:
                    instance.status = 'CANCEL'
                    instance.save()
                    print('CANCEL')
                    return 'montant_min'
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

                if float(amount_week) >= float(plafond_client.montant_cumul_max_week):
                    instance.status = 'WAIT'
                    instance.save()
                    return 'montant_cumul_max_week'

                if float(amount_month) >= float(plafond_client.montant_cumul_max_month):
                    instance.status = 'WAIT'
                    instance.save()
                    return 'montant_cumul_max_month'
            else:
                return 'NotMontant'
        else:
            return 'NotClient'
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

                if float(amount_week) >= float(plafond_client.montant_cumul_max_week):
                    instance.status = 'WAIT'
                    instance.save()
                    return 'montant_cumul_max_week'

                if float(amount_month) >= float(plafond_client.montant_cumul_max_month):
                    instance.status = 'WAIT'
                    instance.save()
                    return 'montant_cumul_max_month'
            else:
                return 'NotMontant'
        else:
            return 'NotBank'
        return ''

    # http://localhost:8000/%5Eappels/?montant=15000&compte_id=1&compte_numero=008036&numero_recharge=697282623
    def post(self, request, *args, **kwargs):
        # cal = calendar.weekday(2019,8,1)
        # week = datetime.date(2019,8,1).isocalendar()
        # print(cal)
        # print(week[1])
        # d = datetime.date(2019,8,1).timetuple()
        # print(d)
        # print(d[1])
        print(request)
        if request.user.is_authenticated:
            data_query = {
                'montant': request.data['montant'],
                'compte_id': request.data['compte_id'],
                'compte_numero': request.data['compte_numero'],
                'numero_recharge': request.data['numero_recharge'],
                'client_id': request.user.id,
                'client_nom': request.user.username,
                'banque_id': request.user.banque,
                'status': 'PROGRESS'
            }

            intput_serializer = appelsSerializers(data=data_query)
            intput_serializer.is_valid(raise_exception=True)
            if intput_serializer.is_valid(raise_exception=True):
                #         instance = models.Tbanque.Meta.model(**validated_data)
                # if not data_query['banque_id']:
                #     res = reponses_generale(msg_code='MG000', sucess=0, error_code='NotBank',
                #                             error_msg="cet utilisateur n'a pas de banque")
                #     return Response(res)
                # SAUVEGARDE APPEL DE FONDS
                instance = intput_serializer.save()
                # VERIFICATION DES PLAFONDS
                if request.user.type_plafond == USER:
                    verif = self.verifPlafondUser(instance)
                    print(verif)

                    if verif == 'montant_max':
                        # return Response([
                        #     {'content':{'msg': 'votre montant dépasse le montant maximal que vous pouvez effectuer, veuillez patienter svp!'}}
                        #     ])
                        msg = 'votre montant dépasse le montant maximal que vous pouvez effectuer, veuillez patienter svp!'
                        res = reponses_generale(msg_code='MG011', sucess=0, results=intput_serializer.data,
                                                error_code='plafond', error_msg=msg)
                        return Response(res)
                    elif verif == 'montant_min':
                        plafond_client = models.TPlafond.objects.get(client_id=instance.client_id)
                        # return Response([
                        #     {'content':{'msg': 'vous ne pouvez faire une opération en dessous de %s' % (plafond_client.montant_min)}}
                        #     ])
                        msg = 'vous ne pouvez faire une opération en dessous de %s' % (plafond_client.montant_min)
                        res = reponses_generale(msg_code='MG011', sucess=0, results=intput_serializer.data,
                                                error_code='plafond', error_msg=msg)
                        return Response(res)
                    elif verif == 'montant_cumul_max_week':
                        # return Response([
                        #     {'content':{'msg': 'cette demande a fait dépasser le maximum de la semaine, veuillez patienter svp!'}}
                        #     ])
                        msg = 'cette demande a fait dépasser le maximum de la semaine, veuillez patienter svp!'
                        res = reponses_generale(msg_code='MG011', sucess=0, results=intput_serializer.data,
                                                error_code='plafond', error_msg=msg)
                        return Response(res)
                    elif verif == 'montant_cumul_max_month':
                        # return Response([
                        #     {'content':{'msg': 'cette demande a fait dépasser le maximum du mois, veuillez patienter svp!'}}
                        #     ])
                        msg = 'cette demande a fait dépasser le maximum du mois, veuillez patienter svp!'
                        res = reponses_generale(msg_code='MG011', sucess=0, results=intput_serializer.data,
                                                error_code='plafond', error_msg=msg)
                        return Response(res)
                # if request.user.type_plafond == BANK:
                else:
                    verif = self.verifPlafondBank(instance)
                    print(verif)

                    if verif == 'montant_max':
                        # return Response([
                        #     {'content':{'msg': 'votre montant dépasse le maximum autorisé par votre banque, veuillez patienter svp!'}}
                        #     ])
                        msg = 'votre montant dépasse le maximum autorisé par votre banque, veuillez patienter svp!'
                        res = reponses_generale(msg_code='MG011', sucess=0, results=intput_serializer.data,
                                                error_code='plafond', error_msg=msg)
                        return Response(res)
                    elif verif == 'montant_min':
                        plafond_client = models.TPlafond.objects.get(banque_id=instance.banq_id)
                        # return Response([
                        #     {'content':{'msg': 'Pour cette banque vous ne pouvez faire une opération en dessous de %s' % (plafond_client.montant_min)}}
                        #     ])
                        msg = 'Pour cette banque vous ne pouvez faire une opération en dessous de %s' % (
                            plafond_client.montant_min)
                        res = reponses_generale(msg_code='MG011', sucess=0, results=intput_serializer.data,
                                                error_code='plafond', error_msg=msg)
                        return Response(res)
                    elif verif == 'montant_cumul_max_week':
                        # return Response([
                        #     {'content':{'msg': 'cette demande a fait dépasser le maximum de la semaine autorisé par cette banque, veuillez patienter !'}}
                        #     ])
                        msg = 'cette demande a fait dépasser le maximum de la semaine autorisé par cette banque, veuillez patienter !'
                        res = reponses_generale(msg_code='MG011', sucess=0, results=intput_serializer.data,
                                                error_code='plafond', error_msg=msg)
                        return Response(res)
                    elif verif == 'montant_cumul_max_month':
                        # return Response([
                        #     {'content':{'msg': 'cette demande a fait dépasser le maximum du mois autorisé par cette banque, veuillez patienter svp!'}}
                        #     ])
                        msg = 'cette demande a fait dépasser le maximum du mois autorisé par cette banque, veuillez patienter svp!'
                        res = reponses_generale(msg_code='MG011', sucess=0, results=intput_serializer.data,
                                                error_code='plafond', error_msg=msg)
                        return Response(res)

                # ENVOI LAPPEL DE FONDS AU CORE ELOGE
                data = {'user_id': instance.client_id.id,
                        'transaction_key': instance.id,
                        'account_number': instance.compte_numero,
                        'phone_number': instance.numero_recharge,
                        'date': instance.date,
                        'amount': instance.montant,
                        }
                #s = "[{'msg_code': 'MG001', 'params': %s}]" % (data)
                socket_obj = SocketHandler(sock=None)
                MSG_CODE = 'MG002'
                data_list = socket_obj.get_response(MSG_CODE,data)
                # CHANGEMENT DU STATUS SELON LA REPONSE
                #if data_list[0].has_key('success'):
                if  data_list[0]['success']:
                    instance.status = 'FINISH'
                    instance.save()
                    # appel_obj = self.get_object(data_list[0]['transaction_key'])
                    # appel_obj.status = 'FINISH'
                    # appel_obj.save()
                else:
                    res = reponses_generale(msg_code=MSG_CODE, sucess=0, results='',
                                            error_code=data_list[0]['error'][0]['err_code'], error_msg=data_list[0]['error'][0]['err_msg'])
                    return  Response(res)
                return Response(data_list)

                # output_serializer = appelsSerializers(instance)
                # # return Response([{'content': output_serializer.data}], status=status.HTTP_201_CREATED)
                # res = reponses_generale(msg_code='MG0011', sucess=1, results=output_serializer.data)
                # return Response(res)
            else:
                # Response(output_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                res = reponses_generale(msg_code='MG000', sucess=0, results=intput_serializer.errors,
                                        error_code='invalid', error_msg="données invalide")
                return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

        # http://localhost:8000/%5Eappels/?page=1

    # ceci doit servire d historique
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
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
                output_serializer = appelsSerializers(items, many=True)
                counts = paginator.num_pages
                res_pages = {'total_page': counts,"content": output_serializer.data}
                # return Response([{'content': output_serializer.data}])
                res = reponses_generale(msg_code='MG0011', sucess=1, results=res_pages)
                return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

    # ANNULER/VALIDER LES APPELS DE FONDS
    # http://localhost:8000/%5Eappels/?pk=1/?status='FINISH' ou 'CANCEL'
    def put(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if 'pk' in request.query_params:
                if 'status' in request.query_params:
                    # item = models.TappelFonds.objects.get(pk=request.query_params['pk'])
                    item = self.get_object(request.query_params['pk'])
                    item.status = request.query_params['status']

                    output_serializer = appelsSerializers(instance=item, data=request.data, partial=True)
                    output_serializer.is_valid(raise_exception=True)
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
                            # res = reponses_generale(msg_code='MG0020', sucess=1, results=output_serializer.data)
                            # return Response(res)
                        if item.status == "CANCEL":
                            res = reponses_generale(msg_code='MG0020', sucess=1, results=output_serializer.data)
                            return Response(res)

                    else:
                        res = reponses_generale(msg_code='MG000', sucess=0, results=intput_serializer.errors,
                                                error_code='invalid', error_msg="données invalide")
                        return Response(res)
            # return Response([{'content': output_serializer.data}])
            else:
                res = reponses_generale(msg_code='MG000', sucess=0, results=output_serializer.errors,
                                        error_code='invalid', error_msg="le pk est invalide")
                return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

    # def delete(self, request, *args, **kwargs):
    #     #item = models.TPlafond.objects.get(pk=request.query_params['pk'])
    #     item = self.get_object(request.query_params['pk'])
    #     item.delete()
    #     return Response(status= status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        return get_object_or_404(TappelFonds,pk=pk)


####################################### api view plafond ###################################
class plafondView(APIView):
    # http://localhost:8000/%5Eplafond/?montant_max=100000&montant_min=25&seuil_validation=200000
    def post(self, request, *args, **kwargs):
        print('#####################')
        print(request.query_params)
        if request.user.is_authenticated:
            intput_serializer = plafondSerializers(data=request.query_params)
            intput_serializer.is_valid(raise_exception=True)
            if intput_serializer.is_valid(raise_exception=True):
                #         instance = models.Tbanque.Meta.model(**validated_data)
                instance = intput_serializer.save()
                output_serializer = plafondSerializers(instance)
                res = reponses_generale(msg_code='MG0024', sucess=1, results=output_serializer.data)
                return Response(res)
            else:
                res = reponses_generale(msg_code='MG000', sucess=0, results=intput_serializer.errors,
                                        error_code='invalid', error_msg="données invalide")
                return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

    # http://localhost:8000/%5Eplafond/?page=1
    def get(self, request, *args, **kwargs):
        # print(request.query_params['pk'])
        if request.user.is_authenticated:
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
                counts = paginator.num_pages
                res_pages = {'total_page': counts, "content": output_serializer.data}

                res = reponses_generale(msg_code='MG0024', sucess=1, results=res_pages)
                return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

    # def delete(self, request, *args, **kwargs):
    #     #item = models.TPlafond.objects.get(pk=request.query_params['pk'])
    #     item = self.get_object(request.query_params['pk'])
    #     item.delete()
    #     return Response(status= status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return models.TPlafond.objects.get(pk=pk)
        except models.TPlafond.DoesNotExist:
            raise Http404

    # http://localhost:8000/%5Eplafond/?pk=1/?status='FINISH' ou 'CANCEL'
    def put(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if 'pk' in request.query_params:
                item = self.get_object(request.query_params['pk'])

                output_serializer = plafondSerializers(instance=item, data=request.query_params, partial=True)
                output_serializer.is_valid(raise_exception=True)
                if output_serializer.is_valid(raise_exception=True):
                    output_serializer.save()

                    res = reponses_generale(msg_code='MG0024', sucess=1, results=output_serializer.data)
                    return Response(res)
                else:
                    res = reponses_generale(msg_code='MG000', sucess=0, results=output_serializer.errors,
                                            error_code='invalid', error_msg="données invalide")
                    return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

    ########################## api view des comptes ############################


# Detail dun compte ou tous les compte (LES COMPTES DE QUELQU'UN)
# parametres pk et banque_id
class comptesView(APIView):
    # http://localhost:8000/%5Ecomptes/
    def get(self, request, *args, **kwargs):
        # print(request.query_params['pk'])
        if request.user:
            # les comptes de quelqu'un dans une banque'
            if 'pk' in request.query_params:
                if 'banque_id' in request.query_params:
                    # envoi au serveur
                    socket_obj = SocketHandler(sock=None)
                    data = {'user_id': request.query_params['pk'], 'banque_id': request.query_params['banque_id']}
                    # s = "[{'msg_code': 'MG001', 'params': %s}]" % (data)
                    # socket_obj.send(bytes(s, encoding='utf8'))
                    #
                    # #  transfert la reponse
                    # recep = socket_obj.receive()
                    # ''' formatage de la reponse en json '''
                    # rep_json = recep.decode('utf-8').replace("'", '"')
                    # ''' formatage json enliste '''
                    # data_list = json.loads(rep_json)
                    MSG_CODE = 'MG001'
                    data_list = socket_obj.get_response(MSG_CODE,data)
                    return Response(data_list)
                else:
                    res = reponses_generale(msg_code='MG000', sucess=0, error_code='invalid',
                                            error_msg="invalide banque_id")
                    return Response(res)

            else:
                res = reponses_generale(msg_code='MG000', sucess=0, error_code='invalid', error_msg="invalide pk")
                return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

    # liste de mes compte (MES COMPTES)


# parametres
class mescomptesView(APIView):
    # http://localhost:8000/%5Emescomptes/
    def get(self, request, *args, **kwargs):
        if request.user:
            #if not request.user.banque:
            #    res = reponses_generale(msg_code='MG000', sucess=0, error_code='NotBank',
            #                            error_msg="cet utilisateur n'a pas de banque")
            #    return Response(res)
            socket_obj = SocketHandler(sock=None)
            # envoi au serveur
            print(request.user.id)
            data = {'user_id': request.user.id}
            # s = "[{'msg_code': 'MG001', 'params': %s}]" % (data)
            # socket_obj.send(bytes(s, encoding='utf8'))
            # #  transfert la reponse
            # recep = socket_obj.receive()
            # ''' formatage de la reponse en json '''
            # rep_json = recep.decode('utf-8').replace("'", '"')
            # ''' formatage json enliste '''
            # data_list = json.loads(rep_json)
            MSG_CODE = "MG001"
            data_list = socket_obj.get_response(MSG_CODE,data)
            return Response(data_list)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

    #################################### liste de mes appels de fonds (HISTORIQUE)


# parametres page
class mesappelsView(APIView):
    # http://localhost:8000/%5Emescomptes/
    def get(self, request, *args, **kwargs):
        if request.user:
            if not request.user.banque:
                res = reponses_generale(msg_code='MG000', sucess=0, error_code='NotBank',
                                        error_msg="cet utilisateur n'a pas de banque")
                return Response(res)
            # items = models.TappelFonds.objects.filter(client_id=request.user.id, banque_id=request.user.banque)
            items = models.TappelFonds.objects.filter(client_id=request.user.id)
            paginator = Paginator(items, 5)
            page = request.query_params['page']
            items = paginator.get_page(page)
            output_serializer = appelsSerializers(items, many=True)
            counts = paginator.num_pages
            res_pages = {'total_page': counts, "content": output_serializer.data}
            res = reponses_generale(msg_code='MG0025', sucess=1, results=res_pages)
            return Response(res)

        res = reponses_generale(msg_code='MG001', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)

    ################################### consulter le solde (MON SOLDE)


# parametres compte_numero
class soldeView(APIView):
    # http://localhost:8000/%5Emescomptes/
    def get(self, request, *args, **kwargs):
        if request.user:
            # if not request.user.banque:
            #     res = reponses_generale(msg_code='MG000', sucess=0, error_code='NotBank', error_msg="cet utilisateur n'a pas de banque")
            #     return Response(res)

            socket_obj = SocketHandler(sock=None)
            # msg = [1, 2]
            # msg2 = {}
            # msg3 = b"[{'1', '2'}]"
            # socket_obj.send(bytes('auclert ca marche', encoding='utf8'))
            # socket_obj.send(bytes(msg))
            # socket_obj.send(bytes(msg2))

            data = {'user_id': request.user.id, 'account_number': request.query_params['compte_numero']}
            # s = "[{'msg_code': 'MG001', 'params': %s}]" % (data)
            # socket_obj.send(bytes(s, encoding='utf8'))

            # recep = socket_obj.receive()
            # print(recep)  # en bytes code
            # ''' formatage de la reponse en json '''
            # rep_json = recep.decode('utf-8').replace("'", '"')
            # ''' formatage json enliste '''
            # data_list = json.loads(rep_json)
            # final = json.dumps(data_list, indent=4, sort_keys=True)
            MSG_CODE = "MG003"
            data_list = socket_obj.get_response(MSG_CODE,data)
            #res = reponses_generale(msg_code='MG003', sucess=1,results=data_list, error_code='',error_msg='')
            return Response(data_list)

        res = reponses_generale(msg_code='MG003', sucess=0, error_code='auth1',
                                error_msg='vous devez vous authentifier')
        return Response(res)


class getAppelFondUserCountView(APIView):
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        count = TappelFonds.objects.filter(client_id=user).count()
        res = {"count": count}
        return Response(res)

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
