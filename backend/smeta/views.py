import json
import os
import logging
from uuid import UUID
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404, HttpResponse
from django.conf import settings
from django.template import Template, Context
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import OrderSerializer
from .services import transform_keys, get_or_create_user_id
from .tasks import save_pdf_to_order
from .models import (
    Order, OrderRating, LogFile, AnalyticsCode, ChatCode, 
    RawJSON, ScriptCode, WebhookSettings, TemplateSettings, LogFilter, LogKeyword
)

# Настройка логгера
logger = logging.getLogger('django')

class SmetaCreateAPIView(APIView):
    """ Сохраняет смету разбивая на объекты """
    def post(self, request, *args, **kwargs):
        # Логирование получения запроса
        logger.info(f"Получен запрос на создание сметы")
        
        if 'Данные' not in request.data or not request.data['Данные']:
            logger.error("Ошибка: Поле 'Данные' отсутствует или пусто")
            return Response({'ошибка': 'Поле "Данные" является обязательным'}, status=status.HTTP_400_BAD_REQUEST)

        if 'Документ' not in request.data or not request.data['Документ']:
            document_missing = True  # Флаг, что документа нет
            logger.warning("Документ отсутствует в запросе")
        else:
            document_missing = False  # Документ присутствует

        # Получаем данные и преобразовываем ключи на английский
        data_str = request.data['Данные']
        
        try:
            # Сохраняем оригинальный JSON
            original_data = json.loads(data_str)
            
            # Трансформируем данные для сериализатора
            transformed_data = transform_keys(original_data)
            
            serializer = OrderSerializer(data=transformed_data)
            if serializer.is_valid():
                order = serializer.save()
                
                # Сохраняем оригинальный JSON
                raw_json = RawJSON.objects.create(
                    order=order,
                    data=original_data
                )
                logger.info(f"Создана смета с UUID: {order.uuid}, сохранен исходный JSON")

                # Получаем PDF файл и ставим задачу в очередь для сохранения PDF
                if not document_missing:
                    pdf_file = request.FILES.get('Документ')
                    save_pdf_to_order.delay(order.id, pdf_file.read(), pdf_file.name)
                    logger.info(f"PDF документ сохранен для сметы с UUID: {order.uuid}")

                # Отправка данных в вебхук, если настроен
                webhook_settings = WebhookSettings.objects.filter(is_active=True).first()
                if webhook_settings:
                    from .tasks import send_webhook
                    send_webhook.delay(webhook_settings.url, {
                        'order_uuid': str(order.uuid),
                        'order_number': order.number
                    })
                    logger.info(f"Задача отправки в вебхук для сметы с UUID: {order.uuid}")

                return Response(f'{settings.SITE_URL}/smeta/{order.uuid}', status=status.HTTP_201_CREATED)
            
            # В случае ошибок в валидации, все равно пытаемся создать заказ из того, что понимаем
            error_data = serializer.errors
            logger.warning(f"Ошибки валидации при создании сметы: {error_data}")
            
            # Попытка создать заказ с максимальным количеством валидных данных
            valid_data = {}
            for field, value in transformed_data.items():
                if field not in error_data:
                    valid_data[field] = value
            
            if valid_data:
                try:
                    partial_serializer = OrderSerializer(data=valid_data, partial=True)
                    if partial_serializer.is_valid():
                        order = partial_serializer.save()
                        
                        # Сохраняем оригинальный JSON даже при частичной валидации
                        raw_json = RawJSON.objects.create(
                            order=order,
                            data=original_data
                        )
                        logger.info(f"Создана частичная смета с UUID: {order.uuid}, сохранен исходный JSON")
                        
                        if not document_missing:
                            pdf_file = request.FILES.get('Документ')
                            save_pdf_to_order.delay(order.id, pdf_file.read(), pdf_file.name)
                            logger.info(f"PDF документ сохранен для частичной сметы с UUID: {order.uuid}")
                            
                        # Отправка данных в вебхук, если настроен
                        webhook_settings = WebhookSettings.objects.filter(is_active=True).first()
                        if webhook_settings:
                            from .tasks import send_webhook
                            send_webhook.delay(webhook_settings.url, {
                                'order_uuid': str(order.uuid),
                                'order_number': order.number,
                                'partial_data': True
                            })
                            
                        return Response(f'{settings.SITE_URL}/smeta/{order.uuid}', status=status.HTTP_201_CREATED)
                except Exception as e:
                    logger.error(f"Ошибка при создании частичной сметы: {str(e)}")
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {str(e)}")
            return Response({'ошибка': f'Некорректный JSON: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Необработанная ошибка при создании сметы: {str(e)}")
            return Response({'ошибка': f'Ошибка сервера: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def smeta_details(request, uuid):
    """ Возвращает страницу сметы по хэшу """
    try:
        # Логирование просмотра сметы
        logger.info(f"Запрос на просмотр сметы с UUID: {uuid}")
        
        # Попытка получить объект заказа по UUID
        order = get_object_or_404(Order, uuid=uuid)
    except Http404:
        # Если заказ не найден, возвращаем ошибку 404
        logger.warning(f"Смета с UUID {uuid} не найдена")
        return JsonResponse({'success': False, 'error': 'UUID сметы указан не верно'}, status=400)

    # Создаем или получаем ID юзера чтобы привязать оценку
    user_id = get_or_create_user_id(request)

    order_rating = OrderRating.objects.filter(order=order, user_id=user_id).first()

    # Расчёт стоимости всех доп. изделий
    total_additionals_cost = sum([additional.cost for additional in order.additionals.all()])
    # Расчёт стоимости всех услуг
    total_services_cost = sum([service.cost for service in order.services.all()])
    
    # Получаем активные скрипты
    head_start_scripts = ScriptCode.objects.filter(placement='head_start', is_active=True)
    head_end_scripts = ScriptCode.objects.filter(placement='head_end', is_active=True)
    body_start_scripts = ScriptCode.objects.filter(placement='body_start', is_active=True)
    body_end_scripts = ScriptCode.objects.filter(placement='body_end', is_active=True)
    
    # Проверяем, есть ли активный шаблон
    template_settings = TemplateSettings.objects.filter(is_active=True).first()

    context = {
        'order': order,
        'office': order.office,
        'manager': order.manager,
        'products': order.products.all(),
        'additionals': order.additionals.all(),
        'services': order.services.all(),
        'code': order.code,
        'created_at': order.created_at,
        'total_additionals_cost': total_additionals_cost,
        'total_services_cost': total_services_cost,
        'order_rating': order_rating,
        'analytics_code': AnalyticsCode.objects.first() or None,
        'chat_code': ChatCode.objects.first() or None,
        # Новые скрипты по местам размещения
        'head_start_scripts': head_start_scripts,
        'head_end_scripts': head_end_scripts,
        'body_start_scripts': body_start_scripts,
        'body_end_scripts': body_end_scripts,
    }
    
    # Логирование успешного просмотра
    logger.info(f"Смета с UUID {uuid} успешно отображена")

    # Если есть активный шаблон, обрабатываем его
    if template_settings:
        try:
            # Обрабатываем HTML-шаблон с заданным контекстом
            custom_template = Template(template_settings.html_template)
            custom_context = Context(context)
            rendered_html = custom_template.render(custom_context)
            
            # Добавляем обработанный шаблон в контекст
            context['rendered_template'] = rendered_html
            context['template'] = template_settings
            
            # Логируем для отладки
            logger.info(f"Шаблон успешно обработан, длина HTML: {len(rendered_html)}")
            logger.info(f"Первые 100 символов шаблона: {rendered_html[:100]}")
            
            return render(request, 'custom_template.html', context)
        except Exception as e:
            logger.error(f"Ошибка при обработке шаблона: {str(e)}")
            # В случае ошибки, используем стандартный шаблон
            return render(request, 'order_detail.html', context)
    
    # Иначе используем стандартный шаблон
    return render(request, 'order_detail.html', context)


def rate_smeta(request, uuid):
    """ Обрабатывает оценку заказа """
    order = get_object_or_404(Order, uuid=uuid)

    if request.method == 'POST':
        # Декодируем JSON из тела запроса
        try:
            data = json.loads(request.body)
            liked = data.get('liked') # True = Нравится | False = Не нравится
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Не корректный JSON'}, status=400)

        # Получаем user_id из cookies или генерируем новый
        user_id = get_or_create_user_id(request)

        # Обновляем или создаем запись об оценке
        rating, created = OrderRating.objects.update_or_create(
            order=order,
            user_id=user_id,
            defaults={'liked': liked},
        )

        response = JsonResponse({'success': True, 'liked': rating.liked, 'created': created})

        # Устанавливаем user_id в cookies, если его не было
        if not request.COOKIES.get('user_id'):
            response.set_cookie('user_id', user_id, max_age=365 * 24 * 60 * 60)  # Срок действия 1 год

        return response


def download_log(request, file_name):
    """Скачивание лог-файла по имени"""
    logger.info(f"Запрос на скачивание лог-файла: {file_name}")
    
    # Проверяем, существует ли запись в базе данных
    log_file = LogFile.objects.filter(file_name=file_name).first()
    if not log_file:
        logger.warning(f"Запрошен несуществующий лог-файл: {file_name}")
        raise Http404(f"Файл {file_name} не найден в базе данных")
    
    file_path = os.path.join(settings.LOG_DIR, file_name)
    logger.info(f"Путь к лог-файлу: {file_path}")
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            logger.info(f"Файл {file_name} успешно отправлен пользователю")
            return response
    
    logger.error(f"Файл {file_name} существует в базе, но не найден на диске")
    raise Http404(f"Файл {file_name} не найден на диске")

def delete_log(request, pk):
    log_file = get_object_or_404(LogFile, pk=pk)
    log_file.delete()
    return redirect('admin:smeta_logfile_changelist')


def view_log(request, file_name):
    log_file = get_object_or_404(LogFile, file_name=file_name)
    file_path = log_file.file_path()

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "Файл не найден."

    return render(request, 'view_log.html', {'log_file': log_file, 'content': content})

def export_filtered_log(request, filter_id):
    """Экспортирует логи, отфильтрованные по заданным критериям"""
    log_filter = get_object_or_404(LogFilter, id=filter_id)
    
    # Получаем все ключевые слова из фильтра
    keywords = [kw.keyword for kw in log_filter.keywords.all() if kw.keyword.strip()]
    
    # Определяем шаблон для фильтрации по уровню
    level_prefixes = {
        'INFO': 'INFO',
        'WARNING': 'WARNING',
        'ERROR': 'ERROR',
        'DEBUG': 'DEBUG',
    }
    
    # Получаем основной файл логов
    log_path = os.path.join(settings.LOG_DIR, 'app.log')
    
    if not os.path.exists(log_path):
        return HttpResponse(f"Основной файл логов не найден: {log_path}", status=404)
    
    # Читаем и фильтруем логи
    filtered_lines = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Если выбран конкретный уровень (не ALL), проверяем соответствие
            if log_filter.log_level != 'ALL' and level_prefixes.get(log_filter.log_level) not in line:
                continue
                
            # Если заданы ключевые слова, проверяем их наличие в строке
            if keywords and not any(kw in line for kw in keywords):
                continue
                
            # Строка прошла все фильтры
            filtered_lines.append(line)
    
    # Создаем файл с отфильтрованными логами
    filtered_log_name = f"filtered_{log_filter.name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    filtered_log_path = os.path.join(settings.LOG_DIR, filtered_log_name)
    
    with open(filtered_log_path, 'w', encoding='utf-8') as f:
        f.write(f"# Отфильтрованные логи: {log_filter.name}\n")
        f.write(f"# Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Уровень логов: {log_filter.log_level}\n")
        if keywords:
            f.write(f"# Ключевые слова: {', '.join(keywords)}\n")
        f.write("#" + "-" * 50 + "\n\n")
        f.writelines(filtered_lines)
    
    # Создаем запись о файле в базе данных
    log_file = LogFile.objects.create(file_name=filtered_log_name)
    
    # Обновляем счетчики использования ключевых слов
    for keyword in log_filter.keywords.all():
        keyword.usage_count += 1
        keyword.save()
    
    # Возвращаем ссылку на скачивание
    download_url = reverse('download_log', args=[log_file.file_name])
    if not download_url.endswith('/'):
        download_url += '/'
    
    return redirect(download_url)

