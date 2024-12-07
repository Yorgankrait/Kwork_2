from django.shortcuts import render

#
from django.db import transaction

from rest_framework import viewsets
from rest_framework.exceptions import APIException

from assignments.models import Assignment
from assignments.serializers import AssignmentSerializer
from assignments.tasks import task_execute

from rest_framework import serializers, viewsets, filters

from .models import *

import logging
from rest_framework.views import APIView
import json
from django.http import JsonResponse

import urllib.parse


logger = logging.getLogger(__name__)

class AssignmentViewSet(viewsets.ModelViewSet):

    serializer_class = AssignmentSerializer
    queryset = Assignment.objects.all()

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                # save instance
                instance = serializer.save()
                instance.save()

                # create task params
                job_params = {"db_id": instance.id}

                # submit task for background execution
                transaction.on_commit(lambda: task_execute.delay(job_params))

        except Exception as e:
            raise APIException(str(e))


class IzdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Izd
        fields = ['img','name','har','cout','price']
        #fields = '__all__'

class AdditionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Additional
        fields = ['img','sticker','name','note']
        #fields = '__all__'
    
#class OfferSerializer(serializers.HyperlinkedModelSerializer):
class OfferSerializer(serializers.ModelSerializer):
    izds = IzdSerializer(many=True)
    additionals = AdditionalSerializer(many=True)
    class Meta:
        model = Offer        
        fields = ['offer_hash','price','text_small','text_big','price_crossed','term','price_izd','price_kompl','price_service','manager','izds', 'additionals']
        #fields = '__all__'
    
    def create(self, validated_data):
        izds_data = validated_data.pop('izds')
        additionals_data = validated_data.pop('additionals')        
        offer = Offer.objects.create(**validated_data)
        for izd_data in izds_data:
            Izd.objects.create(offer=offer, **track_data)
        for additional_data in additionals_data:
            Additional.objects.create(offer=offer, **track_data)
        return offer

class FileUploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUploadImage
        fields = '__all__'
        
class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all().filter(is_active=True)
    serializer_class = OfferSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=offer_hash']

class FileUploadImageViewSet(viewsets.ModelViewSet):
    queryset = FileUploadImage.objects.all()
    serializer_class = FileUploadImageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=hash']

#class InDataSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = InData
#        fields = '__all__'
        
#https://offer.okonti.ru/show/334343
#class InDataViewSet(viewsets.ModelViewSet):
#    queryset = InData.objects.all()
#    serializer_class = InDataSerializer
#    filter_backends = [filters.SearchFilter]
#    search_fields = ['=GUID']
    
class InDataView(APIView):
    #authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            logger.error(request.data)
            postData = json.dumps(request.data)
            jsonData = json.loads(postData)
            if ('GUID' in jsonData and  'json_in' in jsonData):
                obj = InData.objects.filter(GUID=jsonData['GUID']).order_by('-pk').first()
                if obj!=None:
                    obj_new = InData.objects.create(GUID=jsonData['GUID'], json_in=jsonData['json_in'])
                    #obj_new.hash = obj.hash
                    #obj_new.save()
                    return JsonResponse({'result': 'offer update', 'data': {'GUID': obj_new.GUID, 'url': f'https://offer.okonti.ru/show/{obj_new.hash}'}}, safe=False)
                else:
                    obj_new = InData.objects.create(GUID=jsonData['GUID'], json_in=jsonData['json_in'])
                    return JsonResponse({'result': 'offer insert', 'data': {'GUID': obj_new.GUID, 'url': f'https://offer.okonti.ru/show/{obj_new.hash}'}}, safe=False)
            else:
                #raise APIException({"result": "error", 'data': 'dont find GUID or json_in in json'})
                return JsonResponse({'result': 'error', 'data': 'error data'}, safe=False)
        except Exception as e:
            logger.error(e)
            raise APIException(e)
            #return JsonResponse({"result": "error"}, safe=False)

def get_offer_data(request, hash):
    obj = InData.objects.filter(hash=hash).order_by('-pk').first()
    if obj!=None:
        x = urllib.parse.unquote_plus(obj.json_in)
        x = x.replace('id_сonstr_item', 'id_constr_item')
        #
        x = x.replace('idorder', 'ID заказа', 1)        
        x = x.replace('idsizing', 'ID замера', 1)
        x = x.replace('order_name', 'Номер заказа', 1)
        x = x.replace('agree_date', 'Дата готовности договора', 1)
        x = x.replace('calc_date', 'Рассчетная дата заказа (Для расчета стоимости на указанную дату. Если дата продажи отсутствует, то это текущая дата)', 1)
        x = x.replace('iddocoper', 'ID типа заказа', 1)
        x = x.replace('docoper_name', 'Наименование типа заказа', 1)
        #
        x = x.replace('seller_name', 'Наименование офиса', 1)
        x = x.replace('seller_address', 'Адрес офиса', 1)
        x = x.replace('alt_seller_address', 'Альтернативный адрес офиса', 1)
        #x = x.replace('seller_phone', 'Телефон офиса', 1)
        #x = x.replace('seller_phonemobile', 'Мобильный телефон офиса', 1)
        x = x.replace('seller_email', 'Email офиса', 1)
        x = x.replace('seller_logo', 'Логотип офиса', 1)
        x = x.replace('for_contact', 'Контактное лицо клиента', 1)
        x = x.replace('consid_text', 'Необязательный текст', 1)
        x = x.replace('recommend_text', 'Необязательный текст заполняемый в форме отчета', 1)
        x = x.replace('trademark', 'Торговая марка (если партнер работает под своей ТМ)', 1)
        x = x.replace('people_shortname', 'Имя менеджера', 1)
        x = x.replace('people_phone', 'Телефон менеджера', 1)
        
        x = x.replace('prof_corsa', 'Количество изделий из профильной системы Corsa (Provedal)', 1)
        x = x.replace('prof_solo', 'Количество изделий из профильной системы Solo (Slidors)', 1)
        x = x.replace('prof_econo', 'Количество изделий из профильной системы Econo', 1)
        x = x.replace('prof_largo', 'Количество изделий из профильной системы Largo', 1)
        x = x.replace('prof_euro', 'Количество изделий из профильной системы Euro', 1)
        x = x.replace('prof_bravo', 'Количество изделий из профильной системы Bravo', 1)
        x = x.replace('prof_grande', 'Количество изделий из профильной системы Grande', 1)
        x = x.replace('prof_primo', 'Количество изделий из профильной системы Primo', 1)
        x = x.replace('prof_nero70out', 'Количество изделий из профильной системы Nero70 Out', 1)
        x = x.replace('prof_nero70', 'Количество изделий из профильной системы Nero70', 1)
        x = x.replace('prof_mira', 'Количество изделий из профильной системы Mira', 1)
        x = x.replace('prof_delight', 'Количество изделий из профильной системы Delight', 1)
        x = x.replace('prof_ser3', 'Количество изделий из профильной системы Rehau Серия 3', 1)
        x = x.replace('prof_ser4', 'Количество изделий из профильной системы Rehau Серия 4', 1)
        x = x.replace('prof_ser5', 'Количество изделий из профильной системы Rehau Серия 5', 1)
        x = x.replace('furn_siegenia', 'Количество изделий с фурнитурной системой Siegenia', 1)
        x = x.replace('furn_maco', 'Количество изделий с фурнитурной системой MACO', 1)
        x = x.replace('furn_romb', 'Количество изделий с фурнитурной системой Robm', 1)
        x = x.replace('furn_accado', 'Количество изделий с фурнитурной системой Accado', 1)
        x = x.replace('furn_fornax', 'Количество изделий с фурнитурной системой Fornax', 1)
        
        x = x.replace('glass_jaluzi', 'Количество изделий с остеклением содержащим Жалюзи', 1)
        x = x.replace('glass_smart', 'Количество изделий с остеклением SMART', 1)
        x = x.replace('glass_kterm', 'Количество изделий с остеклением KTerm', 1)
        x = x.replace('glass_tp20', 'Количество изделий с теплопакетами 2.0', 1)
        x = x.replace('glass_ds', 'Количество изделий с теплопакетами DS', 1)
        x = x.replace('glass_tp', 'Количество изделий с теплопакетами (другие с теплорамкой TSS)', 1)
        x = x.replace('glass_lgc', 'Количество изделий с остеклением LifeGlassClear', 1)
        
        x = x.replace('is_vitraj', 'Признак наличия Витражей (1 или 0)', 1)
        x = x.replace('mont_brus', 'Количество услуг монтажа в брусовом доме', 1)
        x = x.replace('mont_panel', 'Количество услуг монтажа в панельном доме', 1)
        x = x.replace('mont_kirpich', 'Количество услуг монтажа в крипичном доме', 1)
        
        x = x.replace('is_mont_logy', 'Признак наличия отделки лоджии (1 или 0)', 1)
        x = x.replace('is_promo_sm_from_comment', 'Признак необходимости отображения суммы акционной доп. скидки из комментария к скидке', 1)
        x = x.replace('is_tender', 'Признак тендерного заказа', 1)
        x = x.replace('sm_order', 'Стоимость заказа', 1)
        x = x.replace('sm_order_full', 'Базовая стоимость заказа (без скидки)', 1)
        x = x.replace('sm_items', 'Стоимость изделий с доп. материалами без скидки', 1)
        x = x.replace('sm_item_discount_promo_type1', 'Сумма акционнной доп. скидки на изделия рассчитываемой автоматически до применения регламентных скидок (снижающей розничную стоимость)', 1)
        x = x.replace('sm_item_discount_promo_type2', 'Сумма акционнной доп. скидки на изделия добавляемой менеджером вручную параллельно с регламентной скидкой', 1)
        x = x.replace('sm_order_discount_regl', 'Сумма регламентной скидки на заказ', 1)
        x = x.replace('sm_order_discount_add', 'Сумма акционной доп. скидки на заказ', 1)
        x = x.replace('order_discount_add_name', 'Наименование акционной доп. скидки на заказ', 1)
        x = x.replace('sm_bonus_plan', 'Плановая сумма для начисления бонусов по заказу', 1)
        x = x.replace('constructions', 'Массив проемов заказа', 1)
        #
        x = x.replace('id_сonstr_item', 'ID проема/изделия')
        x = x.replace('is_model', 'Является ли позиция изделием (1 или 0)')
        x = x.replace('num_pos', 'Минимальный порядковый номер изделия из проема')
        x = x.replace('num_constr', 'Порядковый номер конструкции')
        x = x.replace('qu', 'Количество копий проема/изделия')
        x = x.replace('qu_model', 'Общее количество изделий проема')
        x = x.replace('sqr_model', 'Общая площадь изделий проема')
        x = x.replace('sm_model', 'Общая стоимость изделий проема')
        x = x.replace('sm_model_full', 'Общая стоимость изделий проема без скидки')
        
        x = x.replace('sm_discount_promo_type1', 'Сумма акционнной доп. скидки на изделия проема рассчитываемой автоматически до применения регламентных скидок (снижающей розничную стоимость)')
        x = x.replace('sm_discount_promo_type2', 'Сумма акционнной доп. скидки на изделия проема добавляемой менеджером вручную параллельно с регламентной скидкой')
        x = x.replace('sm_packs (было sm_upak)', 'Сумма наценки за большой вес изделий проема')
        x = x.replace('constr_pic_type (было pic_type)', 'Тип изображения конструкции/изделия (4 - общий вид, 0 - изделие (если одно в проеме), 1 - изделие в низком качестве (если одно в проеме и нет стандартного качества))')
        x = x.replace('constr_pic_b64 (был pic_b64)', 'Изображение конструкции/изделия')
        
        x = x.replace('model_name', 'Наименование изделия')
        x = x.replace('model_numpos', 'Порядковый номер изделия')
        x = x.replace('model_constrnum', 'Порядковый номер проема, к которому относится изделие')
        x = x.replace('model_xml', 'Характеристики изделия в формате XML')
        x = x.replace('glass_in_pack', 'Массив стеклопакетов проема выделенных из изделий в упаковки')
        x = x.replace('model_part', 'Часть изделия, к которой относится стеклопакет')
        x = x.replace('model_name', 'Наименование изделия, к которому относится стеклопакет')
        x = x.replace('glass_xml', 'Характеристики стеклопакета в формате XML')
        x = x.replace('connectors', 'Массив соединителей проема')
        x = x.replace('connector_marking', 'Артикул соединителя')
        x = x.replace('connector_qu', 'Количество соединителей')
        x = x.replace('connector_length', 'Длина соединителя в мм')
        x = x.replace('connector_description', 'Описание соединителя (наименование)')
        x = x.replace('warnings', 'Массив предупреждений и ошибок проема')
        x = x.replace('model_names', 'Наименование изделий, к которым относится предупреждение/ошибка')
        x = x.replace('warning_picture_b64', 'Пиктограмма предупреждения/ошибки')
        x = x.replace('warning_text', 'Текст предупреждения/ошибки')
        #
        
        x = x.replace('services', 'Массив услуг заказа')
        x = x.replace('id_goodservice (было goodservice_id)', 'ID услуги заказа')
        x = x.replace('goodservice_name', 'Наименование услуги')
        x = x.replace('goodservice_date', 'Дата выполнения услуги')
        x = x.replace('goodservice_qu', 'Количество услуг')
        x = x.replace('goodservice_sm_full', 'Стоимость услуги без скидки')
        x = x.replace('goodservice_comment', 'Комментарий к услуге')
        x = x.replace('recommend_num', 'Рекоммендуемый порядок отображения услуг')
        x = x.replace('goodservice_details', 'Детализация услуги (массив работ услуги)')
        x = x.replace('id_goodservice', 'ID услуги заказа')
        x = x.replace('goodservice_detail_name', 'Наименование работы услуги')
        x = x.replace('goodservice_detail_measure', 'Единица измерения работы услуги')
        x = x.replace('goodservice_detail_qu', 'Количество работы услуги')
        x = x.replace('goodservice_detail_sm_full', 'Стоимость работы услуги без скидки')
        x = x.replace('addgoods', 'Массив дополнительных материалов заказа')
        #
        x = x.replace('good_name', 'Наименование материала')
        x = x.replace('good_measure', 'Единица измерения материала')
        x = x.replace('good_color', 'Цвет материала')
        
        x = x.replace('good_qu', 'Количество материала (шт)')
        x = x.replace('good_thick', 'Длина материала, мм (если материал измеряется в погонных метрах)')
        x = x.replace('good_size', 'Размер материала (для любой единицы измерения)')
        
        x = x.replace('good_sm_full', 'Общая стоимость материала без скидки (с учетом количества)')
        x = x.replace('good_type_name', 'Наименование типа материала')
        x = x.replace('good_num', 'Порядок сортировки для отображения')
        x = x.replace('promo_discounts', 'Массив акционных скидок заказа')
        x = x.replace('discount_promo_name', 'Наименование акционной доп. скидки рассчитываемой автоматически до применения регламентных скидок (снижающей розничную стоимость)')
        x = x.replace('discount_promo_sm', 'Сумма акционной доп. скидки рассчитываемой автоматически до применения регламентных скидок (снижающей розничную стоимость)')
        '''
        
        
        
        


        '''
        x_obj = json.loads(x)
        with open('/app/backend/upload/data.json', 'w') as f:
            json.dump(x_obj, f)
        return JsonResponse(x_obj, safe=False)
    else: 
        raise APIException({"result": "error", 'data': 'dont found'})
    
'''
import urllib.parse
import json

x = urllib.parse.unquote_plus(i.json_in)
x_obj = json.loads(x)
with open('/app/backend/upload/data.json', 'w') as f:
    json.dump(x_obj, f)
    
если все ок то 200
и  новая:
{'result': 'offer insert', 'data': {'GUID': '343fdjfkl44', 'url': 'https://offer.okonti.ru/show/GHJK4'}}
и  старая:
{'result': 'offer update', 'data': {'GUID': '343fdjfkl44', 'url': 'https://offer.okonti.ru/show/GHJK4'}}

class InDataViewSet(viewsets.ModelViewSet):
    authentication_classes = [] #disables authentication
    permission_classes = [] #disables permission
    def post(self, request):
        headers = {'Content-type': 'application/json;charset=utf-8'}
        session = requests.Session()        
        postData = json.dumps(request.data)
        jsonData = json.loads(postData)
        logger.error('jsonData_in->')
        logger.error(str(jsonData))
        InData.objects.create()
        return JsonResponse({"result": "ok"}, safe=False)
'''