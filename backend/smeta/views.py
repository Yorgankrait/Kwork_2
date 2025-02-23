import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import OrderSerializer
from .services import transform_keys, get_or_create_user_id
from .tasks import save_pdf_to_order
from .models import Order, OrderRating, LogFile, AnalyticsCode, ChatCode


class SmetaCreateAPIView(APIView):
    """ Сохраняет смету разбивая на объекты """
    def post(self, request, *args, **kwargs):
        if 'Данные' not in request.data or not request.data['Данные']:
            return Response({'ошибка': 'Поле "Данные" является обязательным'}, status=status.HTTP_400_BAD_REQUEST)

        if 'Документ' not in request.data or not request.data['Документ']:
            document_missing = True  # Флаг, что документа нет
        else:
            document_missing = False  # Документ присутствует

        # Получаем данные и преобразовываем ключи на английский
        data = json.loads(request.data['Данные'])
        transformed_data = transform_keys(data)

        serializer = OrderSerializer(data=transformed_data)
        if serializer.is_valid():
            order = serializer.save()

            # Получаем PDF файл и ставим задачу в очередь для сохранения PDF
            if not document_missing:
                pdf_file = request.FILES.get('Документ')
                save_pdf_to_order.delay(order.id, pdf_file.read(), pdf_file.name)

            return Response(f'{settings.SITE_URL}/smeta/{order.uuid}', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def smeta_details(request, uuid):
    """ Возвращает страницу сметы по хэшу """
    try:
        # Попытка получить объект заказа по UUID
        order = get_object_or_404(Order, uuid=uuid)
    except Http404:
        # Если заказ не найден, возвращаем ошибку 404
        return JsonResponse({'success': False, 'error': 'UUID сметы указан не верно'}, status=400)

    # Создаем или получаем ID юзера чтобы привязать оценку
    user_id = get_or_create_user_id(request)

    order_rating = OrderRating.objects.filter(order=order, user_id=user_id).first()

    # Расчёт стоимости всех доп. изделий
    total_additionals_cost = sum([additional.cost for additional in order.additionals.all()])
    # Расчёт стоимости всех услуг
    total_services_cost = sum([service.cost for service in order.services.all()])

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
        'chat_code': ChatCode.objects.first() or None
    }

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
    file_path = os.path.join(settings.LOG_DIR, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    raise Http404("Файл не найден")

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

