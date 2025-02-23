from celery import shared_task

from assignments.models import *
import json


'''
@shared_task()
def task_execute(job_params):
    assignment = Assignment.objects.get(pk=job_params["db_id"])
    assignment.sum = assignment.first_term + assignment.second_term
    assignment.save()
'''

@shared_task()
def parse_in_data():
#if(1==1):    
    indata = InData.objects.all().last()
    data = json.loads(indata.json_in)
    office, _ = Office.objects.get_or_create(
        name=data['Офис']['Наименование'],
        defaults={'address': data['Офис']['Адрес']}
    )
    manager, _ = Manager.objects.get_or_create(
        first_name=data['Менеджер']['Имя'],
        office=office,  # Привязка к найденному или созданному офису
        defaults={'phone': data['Менеджер']['Телефон']}
    )
    order, _ = Order.objects.get_or_create(
        number=data['Номер'],
        defaults={
            'office': office,
            'manager': manager,
            'old_price': data['Цена старая'],
            'new_price': data['Цена новая']
        }
    )
    for product_data in data['Изделия']:
        # Ищем или создаем изделие по `identifier` и связанному `order`
        product, _ = Product.objects.get_or_create(
            identifier=product_data['Идентификатор'],
            order=order,  # Привязка к конкретному заказу
            defaults={
                'system': product_data['Система'],
                'series': product_data['Серия'],
                'width': product_data['Ширина'],
                'height': product_data['Высота'],
                'base_color': product_data['Цвет основания'],
                'inner_color': product_data['Цвет внутренний'],
                'outer_color': product_data['Цвет внешний'],
                'handles': product_data['Ручки'],
                'quantity': product_data['Количество'],
                'image': product_data['Изображение']
            }
        )
        # Перебираем опции из JSON и добавляем их к продукту
        for option_data in product_data.get('Опции', []):
            # Создаем или находим опцию для данного продукта
            option, _ = Option.objects.get_or_create(
                name=option_data['Наименование'],
                product=product                
            )    
    # Перебираем услуги из JSON и добавляем их к заказу
    for service_data in data.get('Услуги', []):
        # Создаем или находим услугу для данного заказа
        service, _ = Service.objects.get_or_create(
            name=service_data['Название'],
            order=order,  # Привязка услуги к заказу
            defaults={
                'cost': service_data['Стоимость']
            }
        )    
    for upsale_data in data.get('Допы', []):
        # Создаем или находим услугу для данного заказа
        upsale, _ = UpSale.objects.get_or_create(
            name=upsale_data['Название'],
            order=order,  # Привязка услуги к заказу            
            defaults={
                'cost': upsale_data['Стоимость'],
                'quantity': upsale_data['Количество'],
            }
        )

    